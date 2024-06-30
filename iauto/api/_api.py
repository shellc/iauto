from fastapi import FastAPI

CURRENT_API_VERSION = "v1"

# FastAPI
api = FastAPI(
    title="docread API",
    version=CURRENT_API_VERSION,
    docs_url="/swagger",
    redoc_url='/docs'
)
