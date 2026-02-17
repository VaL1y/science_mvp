import json
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from pathlib import Path
import datetime


# ===============================
# Loading
# ===============================

def load_corpus(path: str) -> List[Dict]:
    papers = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            papers.append(json.loads(line))
    return papers


# ===============================
# Plot monthly trend
# ===============================

def plot_monthly_trend(monthly_counts: dict, query: str) -> str:
    if not monthly_counts:
        return ""

    dates = []
    values = []

    for year in sorted(monthly_counts.keys()):
        for month in sorted(monthly_counts[year].keys()):
            dates.append(datetime.date(year, month, 1))
            values.append(monthly_counts[year][month])

    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker="o")
    plt.title(f"Monthly Publication Trend: {query}")
    plt.xlabel("Month")
    plt.ylabel("Number of Papers")
    plt.xticks(rotation=45)
    plt.grid(True)

    Path("data").mkdir(exist_ok=True)
    file_path = f"data/monthly_trend_{query.replace(' ', '_')}.png"
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

    return file_path


# ===============================
# Semantic clustering
# ===============================

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def compute_topics(papers: List[Dict], n_clusters: int = 4):

    if len(papers) < n_clusters:
        return []

    model = get_embedding_model()

    texts = [p["title"] for p in papers if p.get("title")]

    if not texts:
        return []

    embeddings = model.encode(texts, show_progress_bar=False)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    clusters = {}
    for idx, label in enumerate(labels):
        clusters.setdefault(label, []).append((texts[idx], embeddings[idx]))

    results = []

    for topic_id, items in clusters.items():

        titles = [t for t, _ in items]
        embs = np.array([e for _, e in items])

        centroid = embs.mean(axis=0)
        distances = np.linalg.norm(embs - centroid, axis=1)
        closest_idx = distances.argsort()[:3]

        representative_titles = [titles[i] for i in closest_idx]

        results.append({
            "topic_id": int(topic_id),
            "size": len(titles),
            "representative_titles": representative_titles
        })

    return sorted(results, key=lambda x: x["size"], reverse=True)


# ===============================
# Emerging topics
# ===============================

def compute_emerging_topics(papers: List[Dict], years_window: int = 1, n_clusters: int = 4):

    if not papers:
        return []

    years = sorted({p["year"] for p in papers})
    if len(years) < 2:
        return []

    split_year = years[-years_window]

    old_papers = [p for p in papers if p["year"] < split_year]
    new_papers = [p for p in papers if p["year"] >= split_year]

    old_topics = compute_topics(old_papers, n_clusters)
    new_topics = compute_topics(new_papers, n_clusters)

    if not old_topics or not new_topics:
        return []

    # сравнение по размеру
    emerging = []

    for new_topic in new_topics:
        new_size = new_topic["size"]

        # ищем максимально похожий старый по representative_titles
        old_size = 1

        for old_topic in old_topics:
            old_size = max(old_size, old_topic["size"])

        growth = new_size / old_size

        if growth > 1.3 and new_size > 5:
            emerging.append(new_topic)

    return emerging
