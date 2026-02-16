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


router = APIRouter()


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
    limit = request.limit or settings.DEFAULT_LIMIT

    return generate_mock_analysis(request.query)


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
