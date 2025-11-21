"""Simple RAG indexer using TF-IDF for a quick local MVP.

Creates an index from text files in ../data/docs and saves a pickle at backend/rag_index.pkl
"""
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'docs')
INDEX_PATH = os.path.join(os.path.dirname(__file__), 'rag_index.pkl')


def load_docs(directory=DOCS_DIR):
    docs = []
    meta = []
    if not os.path.isdir(directory):
        return docs, meta
    for fn in sorted(os.listdir(directory)):
        if not fn.lower().endswith('.txt'):
            continue
        path = os.path.join(directory, fn)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
            if text:
                docs.append(text)
                meta.append({'source': fn, 'path': path})
    return docs, meta


def build_index(output_path=INDEX_PATH):
    docs, meta = load_docs()
    if not docs:
        print('No documents found in', DOCS_DIR)
        return

    vectorizer = TfidfVectorizer(stop_words='english', max_features=20000)
    X = vectorizer.fit_transform(docs)

    payload = {
        'vectorizer': vectorizer,
        'matrix': X,
        'docs': docs,
        'meta': meta,
    }

    with open(output_path, 'wb') as f:
        pickle.dump(payload, f)

    print(f'Index built with {len(docs)} docs, saved to {output_path}')


if __name__ == '__main__':
    build_index()
