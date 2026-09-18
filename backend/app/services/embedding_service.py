from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for a single text.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def generate_embeddings(
    chunks: list[str],
) -> list[list[float]]:
    """
    Generate embeddings for multiple text chunks.
    """

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
    )

    return embeddings.tolist()