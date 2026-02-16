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
    compute_top_terms,
    compute_emerging_terms,
)

router = APIRouter()

import os
import re

def _safe_name(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9_\-]+", "_", s)
    return s[:80] or "query"

def generate_mock_analysis(query: str) -> AnalyzeResponse:
    mock_stats = AnalysisStatistics(
        total_papers=432,
        yearly_counts={
            2020: 50,
            2021: 80,
            2022: 110,
            2023: 120,
            2024: 72,
        },
        top_terms=["optimization", "neural networks", "distributed systems"],
        growing_terms=["federated learning", "edge intelligence", "privacy"],
    )

    mock_literature = LiteratureBlock(
        basic=[
            LiteratureItem(
                title=f"Survey on {query}",
                year=2018,
                source="arXiv",
                url="https://arxiv.org/abs/1234.5678",
                doi=None,
            )
        ],
        review=[
            LiteratureItem(
                title=f"Recent Advances in {query}",
                year=2022,
                source="Semantic Scholar",
                url="https://example.com/review",
                doi="10.1000/example",
            )
        ],
        advanced=[
            LiteratureItem(
                title=f"Cutting-edge Research in {query}",
                year=2024,
                source="Crossref",
                url="https://example.com/advanced",
                doi="10.1000/advanced",
            )
        ],
    )

    return AnalyzeResponse(
        query=query,
        summary=f"Direction '{query}' demonstrates steady growth with increasing publication activity.",
        statistics=mock_stats,
        clusters=[
            "Distributed Training",
            "Privacy-preserving Methods",
            "System Optimization",
        ],
        literature=mock_literature,
    )

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_topic(request: AnalyzeRequest):

    years = request.years or settings.DEFAULT_YEARS

    result = fetch_arxiv_monthly_corpus(
        query=request.query,
        years=years,
        max_per_month=300,
    )

    papers = load_corpus(result["file_path"])

    top_terms = compute_top_terms(papers, top_n=20)
    emerging_terms = compute_emerging_terms(papers, recent_years=2, top_n=10)

    stats = AnalysisStatistics(
        total_papers=result["total"],
        yearly_counts=result["yearly_counts"],
        top_terms=top_terms,
        growing_terms=emerging_terms,
    )

    return AnalyzeResponse(
        query=request.query,
        summary=f"Corpus saved to {result['file_path']}",
        statistics=stats,
        clusters=[],
        literature=LiteratureBlock(basic=[], review=[], advanced=[]),
    )



@router.post("/compare", response_model=CompareResponse)
def compare_topics(request: CompareRequest):
    analysis_a = generate_mock_analysis(request.topic_a)
    analysis_b = generate_mock_analysis(request.topic_b)

    recommendation = (
        f"Based on publication growth, '{request.topic_a}' appears "
        f"slightly more dynamic than '{request.topic_b}'."
    )

    return CompareResponse(
        topic_a=analysis_a,
        topic_b=analysis_b,
        recommendation=recommendation,
    )
