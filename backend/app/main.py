from fastapi import FastAPI


app = FastAPI(
    title="DocuMind API",
    description="AI-powered document intelligence platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "documind-api",
        "version": "0.1.0",
    }


@app.get("/")
def root():
    return {
        "message": "DocuMind API is running",
    }