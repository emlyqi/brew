import pandas as pd
import json
import os
import re
from typing import List, Dict, Any

# paths
RAW_CSV = "src/data/raw/linkedinuserprofiles.csv"
PROCESSED_JSON = "src/data/processed/profiles.json"

def clean_text(text):
    """Clean and normalize text content"""
    if not text or text == '' or text == 'null':
        return ''
    
    # remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', str(text)).strip()
    
    # remove common artifacts
    text = text.replace('\\"', '"').replace("\\'", "'")
    
    return text

def parse_json_field(field_value):
    """Safely parse JSON strings, return original if parsing fails"""
    if not field_value or field_value == '' or field_value == 'null':
        return []
    
    try:
        return json.loads(field_value)
    except (json.JSONDecodeError, TypeError):
        return clean_text(field_value)

def extract_skills(text: str) -> List[str]:
    """Heuristically extract skills from free text (experience, education, about)"""
    if not text:
        return []
    keyword_groups = [
        r"python|java|javascript|typescript|c\+\+|c#|go|rust|ruby|php",
        r"react|vue|angular|svelte|next\.js|node|express",
        r"sql|nosql|postgres|mysql|sqlite|mongo(?:db)?",
        r"aws|azure|gcp|google cloud|cloudflare",
        r"docker|kubernetes|terraform|ansible|ci/cd|jenkins|github actions",
        r"tensorflow|pytorch|scikit-learn|sklearn|pandas|numpy|matplotlib|seaborn|xgboost|lightgbm",
        r"nlp|computer vision|deep learning|machine learning|data science|analytics|statistics",
        r"spark|hadoop|airflow|dbt|snowflake|databricks|kafka",
        r"tableau|power bi|looker|metabase|excel|google sheets",
        r"git|jira|confluence|figma|adobe xd|photoshop|illustrator",
        r"product management|project management|agile|scrum|kanban",
        r"marketing|seo|sem|content marketing|email marketing|salesforce|hubspot",
        r"finance|accounting|financial modeling|sas|stata|r language|r programming"
    ]
    pattern = re.compile(r"\\b(?:" + "|".join(keyword_groups) + r")\\b", re.IGNORECASE)
    matches = pattern.findall(text or "")
    def norm(s: str) -> str:
        ss = s.lower()
        fixed = {
            'sql': 'SQL', 'nosql': 'NoSQL', 'aws': 'AWS', 'gcp': 'GCP', 'ci/cd': 'CI/CD',
            'nlp': 'NLP', 'ai': 'AI', 'ui': 'UI', 'ux': 'UX', 'git': 'Git',
            'c++': 'C++', 'c#': 'C#', 'dbt': 'dbt'
        }
        return fixed.get(ss, s.title())
    seen = set()
    skills: List[str] = []
    for m in matches:
        val = norm(m.strip())
        key = val.lower()
        if key and key not in seen:
            seen.add(key)
            skills.append(val)
    return skills

def normalize_named_list(data: Any, name_keys: List[str] = None) -> List[str]:
    """Normalize a heterogeneous list (strings or dicts) to a list of names/titles"""
    if not data:
        return []
    if name_keys is None:
        name_keys = ['title', 'name', 'label']
    results: List[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                val = item.strip()
                if val:
                    results.append(val)
            elif isinstance(item, dict):
                val = ''
                for k in name_keys:
                    if item.get(k):
                        val = str(item[k]).strip()
                        break
                if val:
                    results.append(val)
    return results

def normalize_volunteer_list(data: Any) -> List[str]:
    """Normalize volunteer experience entries to compact strings"""
    if not data or not isinstance(data, list):
        return []
    lines: List[str] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        org = item.get('company') or item.get('organization') or item.get('title')
        role = item.get('role') or item.get('position') or item.get('subtitle') or item.get('title')
        segs = []
        if role:
            segs.append(str(role).strip())
        if org and (not role or org != role):
            segs.append(f"at {str(org).strip()}")
        if segs:
            lines.append(' '.join(segs))
    return lines


def build_education_items(education_data) -> List[Dict[str, Any]]:
    """Build linked education items tying institution with its details"""
    items: List[Dict[str, Any]] = []
    if not education_data:
        return items

    for edu in education_data:
        if not isinstance(edu, dict):
            continue
        institution = clean_text(edu.get('title', ''))
        degree = clean_text(edu.get('degree', ''))
        field = clean_text(edu.get('field', ''))
        start_year = edu.get('start_year')
        end_year = edu.get('end_year')
        url = clean_text(edu.get('url', ''))

        lower_combo = f"{degree} {field}".lower()
        minor = ''
        major = ''
        if 'minor' in lower_combo:
            minor = field or degree
        if any(w in lower_combo for w in ['major', 'bachelor', 'master', 'phd', 'doctorate', 'msc', 'bsc', 'ba', 'ma']):
            major = field or degree

        items.append({
            'institution': institution,
            'degree': degree,
            'field': field,
            'major': clean_text(major),
            'minor': clean_text(minor),
            'start_year': start_year,
            'end_year': end_year,
            'url': url,
        })

    return items

def build_experience_items(experience_data) -> List[Dict[str, Any]]:
    """Build linked experience items tying company, industry, and title"""
    items: List[Dict[str, Any]] = []
    if not experience_data:
        return items

    for exp in experience_data:
        if not isinstance(exp, dict):
            continue
        company = clean_text(exp.get('company', ''))
        industry = clean_text(exp.get('industry', ''))
        top_title = clean_text(exp.get('title', ''))
        top_desc = clean_text(exp.get('description', ''))
        start_date = exp.get('start_date') or exp.get('start') or exp.get('from')
        end_date = exp.get('end_date') or exp.get('end') or exp.get('to')

        positions = exp.get('positions') if isinstance(exp.get('positions'), list) else None
        if positions:
            for pos in positions:
                if not isinstance(pos, dict):
                    continue
                title = clean_text(pos.get('title', top_title))
                description = clean_text(pos.get('description', top_desc))
                p_start = pos.get('start_date') or pos.get('start') or start_date
                p_end = pos.get('end_date') or pos.get('end') or end_date
                items.append({
                    'company': company,
                    'industry': industry,
                    'title': title,
                    'description': description,
                    'start_date': p_start,
                    'end_date': p_end,
                })
        else:
            if company or top_title or top_desc:
                items.append({
                    'company': company,
                    'industry': industry,
                    'title': top_title,
                    'description': top_desc,
                    'start_date': start_date,
                    'end_date': end_date,
                })

    return items

def extract_interests(text: str) -> List[str]:
    """Extract interests and specializations from text"""
    if not text:
        return []
    
    interest_patterns = [
        r'\b(?:fintech|financial technology|banking|finance|investment|trading|cryptocurrency|blockchain)\b',
        r'\b(?:cogsci|cognitive science|psychology|neuroscience|brain|mental|cognitive)\b',
        r'\b(?:startup|entrepreneur|founder|co-founder|startup|venture|innovation)\b',
        r'\b(?:machine learning|AI|artificial intelligence|data science|analytics|statistics)\b',
        r'\b(?:design|UI|UX|user experience|user interface|product design|graphic design)\b',
        r'\b(?:marketing|branding|advertising|social media|content|digital marketing)\b',
        r'\b(?:healthcare|medical|pharmaceutical|biotech|research|clinical|medicine)\b',
        r'\b(?:education|teaching|training|academic|research|curriculum|learning)\b',
        r'\b(?:sustainability|environment|climate|green|renewable|energy)\b',
        r'\b(?:gaming|game development|entertainment|media|content creation)\b'
    ]
    
    interests = set()
    for pattern in interest_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        interests.update(matches)
    
    return list(interests)

def create_embedding_text(
    row,
    interests: List[str],
    education_items: List[Dict[str, Any]] = None,
    experience_items: List[Dict[str, Any]] = None,
    skills_list: List[str] = None,
    languages_data: Any = None,
    certifications_data: Any = None,
    volunteer_data: Any = None,
):
    """Create detailed embedding text containing all semantically relevant fields."""
    parts = []
    
    # basic info
    parts.append(f"Name: {clean_text(row['name'])}")
    parts.append(f"Current Position: {clean_text(row['position'])}")
    current_company = clean_text(row['current_company:name'])
    if current_company and current_company.lower() not in clean_text(row['position']).lower():
        parts.append(f"Current Company: {current_company}")
    parts.append(f"Location: {clean_text(row['city'])}, {clean_text(row['country_code'])}")
    
    # about section
    if clean_text(row['about']):
        parts.append(f"About: {clean_text(row['about'])}")
        
    # interests and skills
    if interests:
        parts.append(f"Interests: {', '.join(interests)}")
    if skills_list:
        parts.append(f"Skills: {', '.join(skills_list)}")

    # education entries (institution-coupled)
    if education_items:
        edu_lines = []
        for e in education_items[:5]:
            bits = [b for b in [e.get('degree'), e.get('field')] if b]
            deg_field = ' in '.join(bits) if bits else ''
            inst = e.get('institution')
            suffix = f" from {inst}" if inst else ''
            mm = []
            if e.get('major'):
                mm.append(f"Major: {e['major']}")
            if e.get('minor'):
                mm.append(f"Minor: {e['minor']}")
            year_span = None
            if e.get('start_year') or e.get('end_year'):
                year_span = f"({e.get('start_year','?')}–{e.get('end_year','?')})"
            line = ' '.join([s for s in [deg_field + suffix, ', '.join(mm) if mm else None, year_span] if s])
            if line:
                edu_lines.append(line)
        if edu_lines:
            parts.append(f"Education Details: {' | '.join(edu_lines)}")

    # experience entries (company-coupled)
    if experience_items:
        exp_lines = []
        current_position_lower = clean_text(row['position']).lower()
        for x in experience_items[:6]:
            comp = x.get('company')
            title = x.get('title')
            industry = x.get('industry')
            dates = None
            if x.get('start_date') or x.get('end_date'):
                dates = f"({x.get('start_date','?')}–{x.get('end_date','?')})"
            rdesc = x.get('description')
            
            # skip if this is the current role (already mentioned in position)
            if comp and title and comp.lower() in current_position_lower and title.lower() in current_position_lower:
                continue
                
            parts_list = [p for p in [title, f"at {comp}" if comp else None, f"[{industry}]" if industry else None, dates, rdesc] if p]
            line = ' '.join(parts_list)
            if line:
                exp_lines.append(line)
        if exp_lines:
            parts.append(f"Experience Details: {' | '.join(exp_lines)}")

    # languages
    lang_list = normalize_named_list(languages_data, ['title', 'name', 'language'])
    if lang_list:
        parts.append(f"Languages: {', '.join(lang_list)}")

    # certifications
    cert_list = normalize_named_list(certifications_data, ['title', 'name', 'certification'])
    if cert_list:
        parts.append(f"Certifications: {', '.join(cert_list)}")

    # volunteer experience
    vol_list = normalize_volunteer_list(volunteer_data)
    if vol_list:
        parts.append(f"Volunteer: {' | '.join(vol_list)}")
    
    return "\n".join(parts)

# load CSV
df = pd.read_csv(RAW_CSV)
df = df.fillna('')

processed_profiles = []

for _, row in df.iterrows():
    # parse JSON fields
    experience_data = parse_json_field(row['experience'])
    education_data = parse_json_field(row['education'])
    languages_data = parse_json_field(row['languages'])
    certifications_data = parse_json_field(row['certifications'])
    volunteer_data = parse_json_field(row['volunteer_experience'])
    groups_data = parse_json_field(row['groups'])
    posts_data = parse_json_field(row['posts'])
    people_viewed_data = parse_json_field(row['people_also_viewed'])
    
    # build semantic inputs
    all_text = f"{row['about']} {row['position']} {row['experience']} {row['education']}"
    interests = extract_interests(all_text)
    education_items = build_education_items(education_data)
    experience_items = build_experience_items(experience_data)
    skills_list = extract_skills(all_text)

    # create detailed embedding text
    embedding_text = create_embedding_text(
        row,
        skills_list=skills_list,
        interests=interests,
        education_items=education_items,
        experience_items=experience_items,
        languages_data=languages_data,
        certifications_data=certifications_data,
        volunteer_data=volunteer_data,
    )
    
    # build lightweight profile (only essential fields and embedding_text)
    profile = {
        # basic info
        "name": clean_text(row['name']),
        "position": clean_text(row['position']),
        "about": clean_text(row['about']),
        "profile_url": clean_text(row['url']),
        "avatar": clean_text(row['avatar']),
        
        # location
        "city": clean_text(row['city']),
        "country_code": clean_text(row['country_code']),
        "region": clean_text(row['region']),
        
        # company info
        "current_company": clean_text(row['current_company:name']),
        "company_id": clean_text(row['current_company:company_id']),
        
        # embedding text (semantic content here)
        "embedding_text": embedding_text,
        
        # metadata
        "timestamp": clean_text(row['timestamp']),
        "profile_id": clean_text(row['id'])
    }
    
    processed_profiles.append(profile)

# save
os.makedirs(os.path.dirname(PROCESSED_JSON), exist_ok=True)
with open(PROCESSED_JSON, 'w', encoding='utf-8') as f:
    json.dump(processed_profiles, f, ensure_ascii=False, indent=2)

print(f"profiles saved to {PROCESSED_JSON}")
print(f"total profiles processed: {len(processed_profiles)}")