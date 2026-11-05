from functools import lru_cache
from pinecone import Pinecone, ServerlessSpec
from openai import AzureOpenAI
from app.config import settings

@lru_cache()
def clients():
    if not settings.azure_openai_api_key or not settings.pinecone_api_key:
        raise ValueError("Azure OpenAI and Pinecone API keys must be set.")
    ai = AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,   # https://foundryrnd-pie.openai.azure.com/
        api_version=settings.azure_openai_api_version,   # e.g. 2024-10-21
    )
    return ai, Pinecone(api_key=settings.pinecone_api_key)


def ensure_index():
    _, pc = clients()
    if not pc.has_index(settings.pinecone_index):
        pc.create_index(name=settings.pinecone_index, dimension=1536, metric='cosine', spec=ServerlessSpec(cloud='aws', region='us-east-1'))
    return pc.Index(settings.pinecone_index)


def embed(texts):
    ai, _ = clients()
    res = ai.embeddings.create(
        model=settings.azure_embed_deployment,  # text-embedding-3-large
        input=texts,
        dimensions=1536,   # keeps your existing 1536-dim index
    )
    return [x.embedding for x in res.data]



def search_kb(query, top_k=5):
    index = ensure_index()
    vector = embed([query])[0]
    result = index.query(vector=vector, top_k=top_k, include_metadata=True)
    return [{'page': m.metadata.get('page'), 'text': m.metadata.get('text',''), 'score': round(m.score,3), 'source': 'Gale Encyclopedia (2002)'} for m in result.matches if m.score >= 0.30]