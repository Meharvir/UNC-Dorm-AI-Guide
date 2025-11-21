"""Simple RAG retriever that loads TF-IDF index and returns top-k passages."""
import os
import pickle
import numpy as np
from sklearn.metrics.pairwise import linear_kernel

INDEX_PATH = os.path.join(os.path.dirname(__file__), 'rag_index.pkl')


def load_index(index_path=INDEX_PATH):
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index not found at {index_path}. Run rag_index.build_index()")
    with open(index_path, 'rb') as f:
        payload = pickle.load(f)
    return payload['vectorizer'], payload['matrix'], payload['docs'], payload['meta']


def retrieve(query, k=3):
    vectorizer, X, docs, meta = load_index()
    qv = vectorizer.transform([query])
    # cosine similarities between q and docs (linear_kernel on tf-idf gives dot product ~= cosine)
    sims = linear_kernel(qv, X).flatten()
    idx = np.argsort(-sims)[:k]
    results = []
    for i in idx:
        results.append({'score': float(sims[i]), 'text': docs[i], 'meta': meta[i]})
    return results


def build_context(query, k=3):
    hits = retrieve(query, k=k)
    parts = []
    for i, h in enumerate(hits, 1):
        meta = h.get('meta', {})
        src = meta.get('source', f'doc{i}')
        # turn filename into friendly source name: hinton_james.txt -> Source: RAG Knowledge - Hinton James
        friendly = src
        try:
            friendly = src.replace('.txt', '').replace('.TXT', '')
            friendly = friendly.replace('_', ' ').title()
            friendly = f"Source: RAG Knowledge — {friendly}"
        except Exception:
            friendly = src
        parts.append(f"[{friendly}] {h['text']}")
    return '\n\n'.join(parts)


if __name__ == '__main__':
    # quick demo
    try:
        print(retrieve('best dorms for studying', k=2))
    except Exception as e:
        print('Index missing - run rag_index.py to build index:', e)
