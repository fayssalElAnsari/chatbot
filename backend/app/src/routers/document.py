from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from src.dependencies import get_vector_store
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import nest_asyncio

nest_asyncio.apply()  # This line is crucial for avoiding nested event loop errors

router = APIRouter()

@router.post("/document/v1/ingest")
async def document_v1_ingest(file: UploadFile = File(...), vector_store=Depends(get_vector_store)):
    if file.content_type != "text/markdown":
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a markdown file.")

    file_content = await file.read()
    content_str = file_content.decode("utf-8")

    document = Document(text=content_str, metadata={"file_name": file.filename})

    # Create the ingestion pipeline with transformations
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(),
            TitleExtractor(),
            HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        ],
        vector_store=vector_store
    )

    nodes = pipeline.run(documents=[document])

    if not nodes:
        raise HTTPException(
            status_code=503, detail="Failed to ingest the document. Please check the ingestion process."
        )

    return JSONResponse(content={"message": "Document ingested successfully", "nodes": len(nodes)})
