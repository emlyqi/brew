import json
import numpy as np
import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from requests import SearchRequest
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# configuration
EMBEDDINGS_JSON = "src/data/processed/embeddings.json"
EMBEDDINGS_NPY = "src/data/processed/embeddings.npy"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = "text-embedding-3-small"

# load data
print("loading profiles and embeddings...")
with open(EMBEDDINGS_JSON, 'r', encoding='utf-8') as f:
    profiles = json.load(f)
embeddings = np.load(EMBEDDINGS_NPY)
print(f"loaded {len(profiles)} profiles with {len(embeddings)} embeddings")

# create FastAPI app
app = FastAPI(title="Brew", version="1.0.0")

# add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def create_query_embedding(query: str) -> List[float]:
    """Create embedding for search query"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query]
    )
    return response.data[0].embedding

def search_profiles(query: str, num_results: int = 10) -> List[Dict]:
    """Search profiles using semantic similarity"""
    try:
        # create query embedding
        query_embedding = create_query_embedding(query)
        query_embedding = np.array(query_embedding).reshape(1, -1)
        
        # calculate similarities
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:num_results]
        
        # prepare results - return clean profile data
        results = []
        for i in top_indices:
            profile = profiles[i].copy()
            # remove the raw embedding data
            if 'embedding' in profile:
                del profile['embedding']
            # add similarity score
            profile['similarity_score'] = float(similarities[i])
            results.append(profile)
        
        return results
    
    except Exception as e:
        print(f"search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"search failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Brew ML Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "profiles_loaded": len(profiles),
        "embeddings_loaded": len(embeddings),
        "openai_configured": client is not None
    }

@app.get("/search")
async def search_endpoint(query: str, num_results: int = 10):
    """Search profiles endpoint (GET)"""
    if not query:
        raise HTTPException(status_code=400, detail="query parameter is required")
    
    results = search_profiles(query, num_results)
    return results

@app.post("/search")
async def search_post(request: SearchRequest):
    """Search profiles endpoint (POST)"""
    results = search_profiles(request.query, request.num_results)
    return results

@app.get("/profile/{profile_id}")
async def get_profile(profile_id: str):
    """Get specific profile by ID"""
    try:
        profile_id = int(profile_id)
        if 0 <= profile_id < len(profiles):
            return profiles[profile_id]
        else:
            raise HTTPException(status_code=404, detail="profile not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid profile id")

@app.get("/profiles")
async def get_all_profiles(limit: int | None = None):
    data = profiles if limit is None or limit <= 0 else profiles[:limit]
    return {
            "total": len(profiles), 
            "profiles": data
        }

@app.post("/generate-message")
async def generate_message(request: dict):
    """Generate personalized LinkedIn message using OpenAI"""
    try:
        profile = request.get("profile", {})
        tone = request.get("tone", "curious")
        your_context = request.get("yourContext", "")
        
        if not profile or not your_context:
            raise HTTPException(status_code=400, detail="profile and yourContext are required")
        
        if not client:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # extract key info from profile
        name = profile.get("name", "there")
        position = profile.get("position", "")
        about = profile.get("about", "")
        current_company = profile.get("current_company", "")
        embedding_text = profile.get("embedding_text", "")
        
        # extract rich context from embedding_text
        def extract_context_from_embedding(embedding_text):
            if not embedding_text:
                return {}
            
            context = {}
            lines = embedding_text.split('\n')
            
            for line in lines:
                if line.startswith('Education Details:'):
                    context['education'] = line.replace('Education Details: ', '')
                elif line.startswith('Experience Details:'):
                    context['experience'] = line.replace('Experience Details: ', '')
                elif line.startswith('Skills:'):
                    context['skills'] = line.replace('Skills: ', '')
                elif line.startswith('Languages:'):
                    context['languages'] = line.replace('Languages: ', '')
                elif line.startswith('Certifications:'):
                    context['certifications'] = line.replace('Certifications: ', '')
                elif line.startswith('Interests:'):
                    context['interests'] = line.replace('Interests: ', '')
                elif line.startswith('Volunteer:'):
                    context['volunteer'] = line.replace('Volunteer: ', '')
            
            return context
        
        rich_context = extract_context_from_embedding(embedding_text)
        
        # create tone-specific prompts
        tone_prompts = {
            "curious": f"Write a natural, conversational LinkedIn message to {name}. Be genuine and mention something specific from their background that caught your attention. Keep it casual and under 80 words. Don't be overly formal or use corporate speak.",
            "networking": f"Write a professional but friendly LinkedIn message to {name}. Find a genuine connection point in their background and introduce yourself naturally. Keep it under 80 words. Avoid buzzwords and be authentic.",
            "collaborative": f"Write a LinkedIn message to {name} about potential collaboration. Be specific about what you'd like to work on together based on their experience. Keep it under 80 words and be direct but friendly.",
            "casual": f"Write a relaxed, friendly LinkedIn message to {name}. Be warm and mention something relatable from their background. Keep it under 80 words. Sound like a real person, not a robot."
        }
        
        prompt = tone_prompts.get(tone, tone_prompts["curious"])
        
        # build comprehensive context
        context_parts = [f"Person's name: {name}"]
        
        if position:
            context_parts.append(f"Current position: {position}")
        if current_company:
            context_parts.append(f"Current company: {current_company}")
        if about:
            context_parts.append(f"About: {about[:150]}...")
        
        # add rich context from embedding_text
        if rich_context.get('education'):
            context_parts.append(f"Education: {rich_context['education'][:200]}...")
        if rich_context.get('experience'):
            context_parts.append(f"Experience: {rich_context['experience'][:200]}...")
        if rich_context.get('skills'):
            context_parts.append(f"Skills: {rich_context['skills'][:150]}...")
        if rich_context.get('interests'):
            context_parts.append(f"Interests: {rich_context['interests'][:150]}...")
        if rich_context.get('languages'):
            context_parts.append(f"Languages: {rich_context['languages']}")
        if rich_context.get('certifications'):
            context_parts.append(f"Certifications: {rich_context['certifications'][:150]}...")
        
        context = '\n'.join(context_parts)
        
        # add sender context
        sender_context = f"About you (the sender): {your_context}"
        
        full_prompt = f"{prompt}\n\nProfile context:\n{context}\n\n{sender_context}\n\nMessage:"
        
        # Generate message using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=150,
            temperature=0.7
        )
        
        message = response.choices[0].message.content.strip()
        
        return {"message": message}
        
    except Exception as e:
        print(f"error generating message: {e}")
        raise HTTPException(status_code=500, detail=f"failed to generate message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
