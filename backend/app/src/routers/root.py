from fastapi import APIRouter, Depends
from src.dependencies import get_llm

router = APIRouter()

@router.get("/")
def read_root(llm = Depends(get_llm)):
    response = llm.complete("hello world!")
    return {"response": response}
