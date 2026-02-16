import json
import re
from collections import Counter, defaultdict
from typing import List, Dict


STOP_WORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "for",
    "to", "with", "using", "based", "from", "via",
    "approach", "method", "analysis", "study",
    "new", "towards", "framework",
}


def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]
    return tokens

def load_corpus(path: str) -> List[Dict]:
    papers = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            papers.append(json.loads(line))
    return papers

def compute_top_terms(papers: List[Dict], top_n: int = 20) -> List[str]:
    counter = Counter()

    for p in papers:
        tokens = tokenize(p["title"])
        counter.update(tokens)

    return [term for term, _ in counter.most_common(top_n)]

def compute_emerging_terms(
    papers: List[Dict],
    recent_years: int = 2,
    top_n: int = 10,
) -> List[str]:

    if not papers:
        return []

    years = sorted({p["year"] for p in papers})
    if len(years) < recent_years:
        return []

    split_year = years[-recent_years]

    old_counter = Counter()
    new_counter = Counter()

    for p in papers:
        tokens = tokenize(p["title"])
        if p["year"] < split_year:
            old_counter.update(tokens)
        else:
            new_counter.update(tokens)

    growth_scores = {}

    for term in new_counter:
        old_freq = old_counter.get(term, 0)
        new_freq = new_counter[term]

        if new_freq >= 3:  # минимальный порог
            growth = new_freq - old_freq
            growth_scores[term] = growth

    sorted_terms = sorted(
        growth_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    return [term for term, _ in sorted_terms[:top_n]]

