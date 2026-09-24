from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(
    name="zepto_policies",
    metadata={"hnsw:space": "cosine"}
)

documents = []
ids = []
metadatas = []

for file_path in sorted(DOCS_DIR.glob("doc_*.txt")):
    text = file_path.read_text(encoding="utf-8").strip()

    documents.append(text)
    ids.append(file_path.stem)

    metadatas.append({
        "source": file_path.name
    })


print(f"Documents loaded: {len(documents)}")

print("Generating embeddings...")
embeddings = model.encode(documents).tolist()

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)


print("\nChromaDB ingestion complete.")
print("Collection:", collection.name)
print("Total documents:", collection.count())

test_query = "How long does Zepto take to deliver an order?"

query_embedding = model.encode([test_query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=3
)


print("\nTest query:")
print(test_query)

print("\nRetrieved documents:")

for i, doc_id in enumerate(results["ids"][0]):
    print(f"{i + 1}. {doc_id}")