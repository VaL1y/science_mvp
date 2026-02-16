from pydantic import BaseModel
from typing import List, Optional, Dict


# ===== Requests =====

class AnalyzeRequest(BaseModel):
    query: str
    years: Optional[int] = None
    limit: Optional[int] = None


class CompareRequest(BaseModel):
    topic_a: str
    topic_b: str
    years: Optional[int] = None
    limit: Optional[int] = None


# ===== Literature Models =====

class LiteratureItem(BaseModel):
    title: str
    year: int
    source: str
    url: str
    doi: Optional[str] = None


class LiteratureBlock(BaseModel):
    basic: List[LiteratureItem]
    review: List[LiteratureItem]
    advanced: List[LiteratureItem]


# ===== Analysis Models =====

class AnalysisStatistics(BaseModel):
    total_papers: int
    yearly_counts: Dict[int, int]
    top_terms: List[str]
    growing_terms: List[str]


class AnalyzeResponse(BaseModel):
    query: str
    summary: str
    statistics: AnalysisStatistics
    clusters: List[str]
    literature: LiteratureBlock


class CompareResponse(BaseModel):
    topic_a: AnalyzeResponse
    topic_b: AnalyzeResponse
    recommendation: str
