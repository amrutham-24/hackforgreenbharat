"""
RAG (Retrieval-Augmented Generation) service for ESG chat.

- Stores document embeddings in Pinecone (or local mock)
- Retrieves top-K evidence docs filtered by tenant_id + company_id
- Generates answers with citations
"""
import json
import logging
import hashlib
from typing import List, Optional, Tuple
from datetime import datetime
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.db.models import RAGDocument, ESGEvent, ESGScore

logger = logging.getLogger(__name__)

_local_vectors: dict = {}


async def create_embedding(text: str) -> List[float]:
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return _mock_embedding(text)
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text[:8000],
        )
        return response.data[0].embedding
    except Exception as e:
        logger.warning(f"Embedding creation failed, using mock: {e}")
        return _mock_embedding(text)


def _mock_embedding(text: str) -> List[float]:
    h = hashlib.md5(text.encode()).hexdigest()
    return [int(c, 16) / 15.0 for c in h] * 96  # 1536-dim mock


async def upsert_document(doc_id: str, text: str, metadata: dict):
    settings = get_settings()
    embedding = await create_embedding(text)

    if settings.PINECONE_API_KEY:
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            index = pc.Index(settings.PINECONE_INDEX)
            index.upsert(vectors=[{"id": doc_id, "values": embedding, "metadata": metadata}])
            return
        except Exception as e:
            logger.warning(f"Pinecone upsert failed, using local: {e}")

    _local_vectors[doc_id] = {"values": embedding, "metadata": metadata, "text": text}


async def query_similar(
    query: str, tenant_id: str, company_id: str, top_k: int = 5
) -> List[dict]:
    settings = get_settings()
    query_embedding = await create_embedding(query)

    if settings.PINECONE_API_KEY:
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            index = pc.Index(settings.PINECONE_INDEX)
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                filter={"tenant_id": tenant_id, "company_id": company_id},
                include_metadata=True,
            )
            return [
                {
                    "id": m.id,
                    "score": m.score,
                    "metadata": m.metadata,
                }
                for m in results.matches
            ]
        except Exception as e:
            logger.warning(f"Pinecone query failed, using local: {e}")

    return _local_query(query_embedding, tenant_id, company_id, top_k)


def _cosine_sim(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)


def _local_query(query_emb: List[float], tenant_id: str, company_id: str, top_k: int) -> List[dict]:
    scored = []
    for doc_id, doc in _local_vectors.items():
        meta = doc["metadata"]
        if meta.get("tenant_id") == tenant_id and meta.get("company_id") == company_id:
            sim = _cosine_sim(query_emb, doc["values"])
            scored.append({"id": doc_id, "score": sim, "metadata": meta, "text": doc.get("text", "")})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


async def generate_chat_answer(
    query: str,
    evidence_docs: List[dict],
    db: AsyncSession,
    company_id: str,
    tenant_id: str,
) -> dict:
    settings = get_settings()

    citations = []
    context_parts = []
    for i, doc in enumerate(evidence_docs):
        meta = doc.get("metadata", {})
        title = meta.get("title", f"Document {i+1}")
        url = meta.get("source_url", "")
        ts = meta.get("ts", "")
        citations.append({"idx": i + 1, "title": title, "url": url, "ts": ts})
        text = doc.get("text", meta.get("text", ""))
        context_parts.append(f"[{i+1}] {title}: {text[:500]}")

    context = "\n\n".join(context_parts) if context_parts else "No evidence documents found."

    score_result = await db.execute(
        select(ESGScore)
        .where(ESGScore.company_id == company_id, ESGScore.tenant_id == tenant_id)
        .order_by(ESGScore.recorded_at.desc())
        .limit(2)
    )
    recent_scores = score_result.scalars().all()
    score_context = ""
    if len(recent_scores) >= 2:
        delta = recent_scores[0].overall - recent_scores[1].overall
        score_context = f"\nLatest score: {recent_scores[0].overall} (delta: {delta:+.2f}). Risk level: {recent_scores[0].risk_level}."
    elif recent_scores:
        score_context = f"\nLatest score: {recent_scores[0].overall}. Risk level: {recent_scores[0].risk_level}."

    if not settings.OPENAI_API_KEY:
        answer = f"Based on the available evidence, here is what I found regarding your query about this company.{score_context}\n\n"
        if citations:
            answer += "Key findings from recent events:\n"
            for c in citations[:3]:
                answer += f"- [{c['idx']}] {c['title']}\n"
        else:
            answer += "No specific evidence documents were found for this query."
        return {"answer": answer, "citations": citations, "used_company_id": company_id}

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        system_prompt = (
            "You are an ESG risk intelligence assistant. Answer questions about company ESG performance "
            "using the provided evidence documents. Always cite sources using [1], [2], etc. "
            "Be concise and factual."
        )
        user_prompt = f"""Question: {query}
{score_context}

Evidence:
{context}

Answer the question using the evidence above. Cite sources with [1], [2], etc."""

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        answer = response.choices[0].message.content.strip()
        return {"answer": answer, "citations": citations, "used_company_id": company_id}
    except Exception as e:
        logger.error(f"Chat generation failed: {e}")
        return {
            "answer": f"I encountered an error generating a response. {score_context}",
            "citations": citations,
            "used_company_id": company_id,
        }
