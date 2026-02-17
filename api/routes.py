from fastapi import APIRouter
from schemas import (
    AnalyzeRequest,
    CompareRequest,
    AnalyzeResponse,
    CompareResponse,
    AnalysisStatistics,
    LiteratureItem,
    LiteratureBlock,
)
from config import settings
from services.search import fetch_arxiv_monthly_corpus
from services.analysis import (
    load_corpus,
    plot_monthly_trend, compute_topics, compute_emerging_topics,
)

router = APIRouter()

import os
import re

def _safe_name(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9_\-]+", "_", s)
    return s[:80] or "query"

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_topic(request: AnalyzeRequest):

    years = request.years or settings.DEFAULT_YEARS

    result = fetch_arxiv_monthly_corpus(
        query=request.query,
        years=years,
        max_per_month=300,
    )

    papers = load_corpus(result["file_path"])

    plot_path = plot_monthly_trend(result["monthly_counts"], request.query)

    topics = compute_topics(papers, n_clusters=4)

    emerging_topics = compute_emerging_topics(
        papers,
        years_window=1,
        n_clusters=4,
    )

    stats = AnalysisStatistics(
        total_papers=result["total"],
        yearly_counts=result["yearly_counts"],
    )

    return AnalyzeResponse(
        query=request.query,
        summary=f"Semantic field analysis. Plot saved to {plot_path}",
        statistics=stats,
        topics=topics,
        emerging_topics=emerging_topics,
        literature=LiteratureBlock(basic=[], review=[], advanced=[]),
    )


#
# @router.post("/compare", response_model=CompareResponse)
# def compare_topics(request: CompareRequest):
#     analysis_a = generate_mock_analysis(request.topic_a)
#     analysis_b = generate_mock_analysis(request.topic_b)
#
#     recommendation = (
#         f"Based on publication growth, '{request.topic_a}' appears "
#         f"slightly more dynamic than '{request.topic_b}'."
#     )
#
#     return CompareResponse(
#         topic_a=analysis_a,
#         topic_b=analysis_b,
#         recommendation=recommendation,
#     )
