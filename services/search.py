import json
import time
from datetime import datetime
from typing import Dict, Iterator, Optional, List

import httpx
import xml.etree.ElementTree as ET

ARXIV_API_URL = "https://export.arxiv.org/api/query"

import os
import json


from calendar import monthrange


def get_arxiv_month_count(query: str, year: int, month: int) -> int:
    """
    Возвращает количество статей за конкретный месяц.
    """

    last_day = monthrange(year, month)[1]

    start_date = f"{year}{month:02d}01"
    end_date = f"{year}{month:02d}{last_day:02d}"

    safe_query = f'"{query}"'

    search_query = (
        f'((ti:{safe_query} OR abs:{safe_query}) '
        f'AND submittedDate:[{start_date} TO {end_date}])'
    )

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": 1,
    }

    try:
        r = httpx.get(ARXIV_API_URL, params=params, timeout=30.0)
        r.raise_for_status()
    except Exception as e:
        print(f"[arXiv] Failed {year}-{month:02d}: {e}")
        return 0

    root = ET.fromstring(r.text)
    ns = {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"}
    total_el = root.find("opensearch:totalResults", ns)

    if total_el is None:
        return 0

    return int(total_el.text)

def fetch_arxiv_month_papers(
    query: str,
    year: int,
    month: int,
    batch_size: int = 200,
    max_per_month: int = 500,
) -> List[Dict]:

    from calendar import monthrange

    last_day = monthrange(year, month)[1]

    start_date = f"{year}{month:02d}01"
    end_date = f"{year}{month:02d}{last_day:02d}"

    safe_query = f'"{query}"'

    search_query = (
        f'((ti:{safe_query} OR abs:{safe_query}) '
        f'AND submittedDate:[{start_date} TO {end_date}])'
    )

    papers = []
    start = 0

    while len(papers) < max_per_month:
        params = {
            "search_query": search_query,
            "start": start,
            "max_results": batch_size,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        try:
            r = httpx.get(ARXIV_API_URL, params=params, timeout=60.0)
            r.raise_for_status()
        except Exception as e:
            print(f"[arXiv] Failed {year}-{month:02d}: {e}")
            break

        root = ET.fromstring(r.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        if not entries:
            break

        for entry in entries:
            title = entry.find("atom:title", ns).text.strip()
            abstract = entry.find("atom:summary", ns).text.strip()
            published = entry.find("atom:published", ns).text
            url = entry.find("atom:id", ns).text

            papers.append(
                {
                    "title": title,
                    "abstract": abstract,
                    "year": year,
                    "month": month,
                    "source": "arXiv",
                    "url": url,
                    "doi": None,
                    "citation_count": None,
                }
            )

            if len(papers) >= max_per_month:
                break

        start += batch_size

    print(f"[arXiv] {year}-{month:02d}: fetched {len(papers)} papers")
    return papers

def fetch_arxiv_monthly_corpus(
    query: str,
    years: int = 5,
    max_per_month: int = 200,
) -> dict:

    from datetime import datetime
    import os
    import json

    current_year = datetime.utcnow().year
    start_year = current_year - years + 1

    os.makedirs("data", exist_ok=True)
    file_path = f"data/arxiv_{query.replace(' ', '_')}_{years}y.jsonl"

    monthly_counts = {}
    yearly_counts = {}
    total = 0

    with open(file_path, "w", encoding="utf-8") as f:

        for year in range(start_year, current_year + 1):

            monthly_counts[year] = {}
            yearly_counts[year] = 0

            for month in range(1, 13):

                if year == current_year and month > datetime.utcnow().month:
                    break

                # Считаем количество
                count = get_arxiv_month_count(query, year, month)
                monthly_counts[year][month] = count

                # Скачиваем статьи
                papers = fetch_arxiv_month_papers(
                    query=query,
                    year=year,
                    month=month,
                    max_per_month=max_per_month,
                )

                yearly_counts[year] += len(papers)
                total += len(papers)

                for p in papers:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")

    return {
        "file_path": file_path,
        "monthly_counts": monthly_counts,
        "yearly_counts": yearly_counts,
        "total": total,
    }

