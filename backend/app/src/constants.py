import os
from typing import Optional


HF_TOKEN: Optional[str] = os.getenv("HUGGING_FACE_TOKEN", "your_huggingface_token")
END_POINT_URL = "https://t8vw8vnwh9jwyf7r.us-east-1.aws.endpoints.huggingface.cloud"

RE_INDEX = False
REQUIRED_EXTS = [".md", ".txt", ".html", ".htm", ".pdf", ".doc"]
INPUT_DIR = "./app/data/sample"

qa_prompt_str = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the question: {query_str}\n"
)

refine_prompt_str = (
    "We have the opportunity to refine the original answer "
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "Given the new context, refine the original answer to better "
    "answer the question: {query_str}. "
    "If the context isn't useful, output the original answer again.\n"
    "Original Answer: {existing_answer}"
)

