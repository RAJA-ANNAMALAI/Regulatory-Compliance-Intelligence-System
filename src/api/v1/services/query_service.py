import os
import re
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from src.core.db import get_vector_store

load_dotenv()

# Database connection setup for raw SQL (FTS)
_raw_conn_str = os.getenv("PG_CONNECTION_STRING", "").replace("postgresql+psycopg", "postgresql")

# vector search
def vector_search(query: str, k: int = 5):
    """Semantic search using LangChain VectorStore"""
    vector_store = get_vector_store()
    docs_and_scores = vector_store.similarity_search_with_score(query, k=k)

    results = []
    for doc, score in docs_and_scores:

        confidence = 1 / (1 + score)

        metadata = doc.metadata.copy()
        metadata["confidence"] = round(confidence, 4)

        results.append({
            "content": doc.page_content,
            "metadata": metadata
        })

    return results


# fts search
def fts_search(query: str, k: int = 5, collection_name: str = "hr_support_desk") -> list[dict]:
    """
    Keyword search against stored chunks using PostgreSQL tsvector / tsquery / ts_rank.
    """
    sql = """
        SELECT
            e.document                                               AS content,
            e.cmetadata                                              AS metadata,
            ts_rank(
                to_tsvector('english', e.document),
                plainto_tsquery('english', %(query)s)
            )                                                        AS fts_rank
        FROM  langchain_pg_embedding  e
        JOIN  langchain_pg_collection c ON c.uuid = e.collection_id
        WHERE c.name = %(collection)s
          AND to_tsvector('english', e.document)
              @@ plainto_tsquery('english', %(query)s)
        ORDER BY fts_rank DESC
        LIMIT %(k)s;
    """
    with psycopg.connect(_raw_conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"query": query, "collection": collection_name, "k": k})
            rows = cur.fetchall()

    return [
        {
            "content": row["content"],
            "metadata": {
                **row["metadata"],
                "confidence": round(min(1.0, float(row["fts_rank"])), 4)
            },
            "fts_rank": round(float(row["fts_rank"]), 4),
        }
        for row in rows
    ]


# hybrid search
def _hybrid_search(query: str, k: int = 5) -> list[dict]:
    """
    Merge vector and FTS results using Reciprocal Rank Fusion (RRF).
    """
    vector_store = get_vector_store()

    # ✅ use scores for vector
    vector_docs = vector_store.similarity_search_with_score(query, k=k)
    fts_docs    = fts_search(query, k=k)

    rrf_scores: dict[str, float] = {}
    chunk_map:  dict[str, dict]  = {}

    # vector contribution
    for rank, (doc, _) in enumerate(vector_docs):
        key = doc.page_content[:120]
        rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (60 + rank + 1)

        chunk_map[key] = {
            "content": doc.page_content,
            "metadata": doc.metadata.copy()
        }

    # fts contribution
    for rank, item in enumerate(fts_docs):
        key = item["content"][:120]
        rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (60 + rank + 1)

        chunk_map[key] = {
            "content": item["content"],
            "metadata": item["metadata"].copy()
        }

    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    scores = [score for _, score in ranked]
    min_score = min(scores)
    max_score = max(scores)

    def normalize(score):
        if max_score == min_score:
            return 1.0
        return (score - min_score) / (max_score - min_score)

    results = []
    for key, score in ranked[:k]:
        item = chunk_map[key]
        item["metadata"]["confidence"] = round(normalize(score), 4)

        results.append(item)

    return results