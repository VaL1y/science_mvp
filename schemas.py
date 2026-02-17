from pydantic import BaseModel
from typing import List, Optional, Dict

class ClusterInfo(BaseModel):
    cluster_id: int
    size: int
    top_terms: List[str]
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


class TopicCluster(BaseModel):
    topic_id: int
    size: int
    representative_titles: List[str]


class AnalyzeResponse(BaseModel):
    query: str
    summary: str
    statistics: AnalysisStatistics
    topics: List[TopicCluster]
    emerging_topics: List[TopicCluster]
    literature: LiteratureBlock


class CompareResponse(BaseModel):
    topic_a: AnalyzeResponse
    topic_b: AnalyzeResponse
    recommendation: str
