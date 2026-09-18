from app.services.embedding_service import generate_embeddings


chunks = [
    "Ritesh is pursuing B.Tech in Electronics and Communication Engineering at IIIT Ranchi.",
    "Ritesh has a CGPA of 8.47 out of 10.",
    "Ritesh has experience with Python, FastAPI, Flask, Docker and AWS.",
    "Ritesh has solved 500+ programming problems on CodeChef.",
]


embeddings = generate_embeddings(chunks)


print("EMBEDDING GENERATION SUCCESSFUL!")
print("-" * 60)

print(f"Total chunks: {len(chunks)}")
print(f"Total embeddings: {len(embeddings)}")

print(f"Embedding dimension: {len(embeddings[0])}")

print("-" * 60)

print("First embedding:")
print(embeddings[0][:10])