from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    num_results: int = 10