import json
import os
import numpy as np
from typing import List, Dict, Any
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# paths
PROCESSED_JSON = "src/data/processed/profiles.json"
EMBEDDINGS_JSON = "src/data/processed/embeddings.json"
EMBEDDINGS_NPY = "src/data/processed/embeddings.npy"
EMBEDDINGS_META = "src/data/processed/embeddings_metadata.json"

# openai configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
EMBEDDING_MODEL = "text-embedding-3-small"

def load_profiles():
    """Load the processed profiles"""
    with open(PROCESSED_JSON, 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    return profiles

def create_embeddings_openai(texts: List[str], client: OpenAI) -> List[List[float]]:
    """Create embeddings using OpenAI API"""
    print("creating embeddings with OpenAI...")
    
    embeddings = []
    batch_size = 100  # process in batches to avoid rate limits
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch
            )
            
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
            
        except Exception as e:
            print(f"error processing batch {i//batch_size + 1}: {e}")
            # add zero embeddings for failed batch
            embeddings.extend([[0.0] * 1536 for _ in batch])  # text-embedding-3-small has 1536 dimensions
    
    return embeddings

def create_embeddings_local(texts: List[str]) -> List[List[float]]:
    """Create embeddings using a local model (sentence-transformers) if no API key"""
    try:
        from sentence_transformers import SentenceTransformer
        
        print("loading local embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("creating embeddings locally...")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        return embeddings.tolist()
        
    except ImportError:
        print("sentence-transformers not installed; install with: pip install sentence-transformers")
        return None

def save_embeddings(profiles: List[Dict], embeddings: List[List[float]]):
    """Save embeddings in multiple formats"""
    
    # 1. save as json with profiles
    print("saving embeddings as json...")
    profiles_with_embeddings = []
    
    for profile, embedding in zip(profiles, embeddings):
        profile_copy = profile.copy()
        profile_copy['embedding'] = embedding
        profiles_with_embeddings.append(profile_copy)
    
    with open(EMBEDDINGS_JSON, 'w', encoding='utf-8') as f:
        json.dump(profiles_with_embeddings, f, ensure_ascii=False, indent=2)
    
    # 2. save as numpy array (for fast loading)
    print("saving embeddings as numpy array...")
    embeddings_array = np.array(embeddings)
    np.save(EMBEDDINGS_NPY, embeddings_array)
    
    # 3. save metadata for easy loading
    metadata = {
        'num_profiles': len(profiles),
        'embedding_dimension': len(embeddings[0]) if embeddings else 0,
        'model_used': EMBEDDING_MODEL,
        'profiles_file': PROCESSED_JSON,
        'embeddings_file': EMBEDDINGS_NPY
    }
    
    with open(EMBEDDINGS_META, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"embeddings saved to:")
    print(f"- {EMBEDDINGS_JSON} (profiles + embeddings)")
    print(f"- {EMBEDDINGS_NPY} (numpy array)")
    print(f"- {EMBEDDINGS_META} (metadata)")

def main():
    """Main function to create embeddings"""
    
    # load profiles
    profiles = load_profiles()
    
    # extract embedding texts
    texts = [profile['embedding_text'] for profile in profiles]
    print(f"extracted {len(texts)} embedding texts")
    
    # try OpenAI API first (better quality)
    if OPENAI_API_KEY:
        print("using OpenAI API for embeddings")
        client = OpenAI(api_key=OPENAI_API_KEY)
        embeddings = create_embeddings_openai(texts, client)
    else:
        print("OpenAI API key not found; using local model instead.")
        embeddings = create_embeddings_local(texts)
        if embeddings is None:
            return
    
    # save embeddings
    save_embeddings(profiles, embeddings)
    
    print(f"\nsuccessfully created embeddings for {len(profiles)} profiles")
    print(f"embedding dimension: {len(embeddings[0]) if embeddings else 0}")

if __name__ == "__main__":
    main()
