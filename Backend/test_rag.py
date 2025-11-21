"""Small test script to build index and run a test query for the local RAG MVP."""
from rag_index import build_index
from rag_query import retrieve, build_context


def run_demo():
    print('Building index...')
    build_index()
    q = 'Best dorms for studying?'
    print('\nQuery:', q)
    hits = retrieve(q, k=3)
    for h in hits:
        print('\nSource:', h['meta']['source'])
        print(h['text'][:300])

    print('\nContext snippet:')
    print(build_context(q, k=2)[:800])


if __name__ == '__main__':
    run_demo()
