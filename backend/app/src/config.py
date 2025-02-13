from fastapi import FastAPI
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext, set_global_handler
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.node_parser import SentenceSplitter
from src.constants import RE_INDEX, REQUIRED_EXTS, INPUT_DIR, qa_prompt_str, refine_prompt_str
import phoenix as px
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate
from llama_index.llms.openai import OpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch


class Config(BaseSettings):
    env:str = os.getenv("ENV", "development")
    env_file_path:str = ".env.development" 
    
    match env:
        case "development":
            env_file_path = ".env.development"
        case "production":
            env_file_path = ".env.production"
    model_config = SettingsConfigDict(extra='allow', env_file=env_file_path)

config = Config()
config.mongo_atlas_uri = f"mongodb+srv://{config.mongodb_atlas_username}:{config.mongodb_atlas_password}@{config.mongodb_atlas_host}?retryWrites=true&w=majority"

def setup_prompts():
    # Text QA Prompt
    chat_text_qa_msgs = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=(
                "Only answer the question if it's related to BeNomad and its products such as BeMap"
            ),
        ),
        ChatMessage(role=MessageRole.USER, content=qa_prompt_str),
    ]
    text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)

    # Refine Prompt
    chat_refine_msgs = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=(
                "Only answer the question if it's related to BeNomad and its products such as BeMap"
            ),
        ),
        ChatMessage(role=MessageRole.USER, content=refine_prompt_str),
    ]
    refine_template = ChatPromptTemplate(chat_refine_msgs)

    return (text_qa_template, refine_template)


def setup_app(app: FastAPI):
    # To view traces in Phoenix, you will first have to start a Phoenix server. You can do this by running the following:
    px.launch_app()

    endpoint = "http://127.0.0.1:6006/v1/traces"
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

    LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

    set_global_handler("arize_phoenix")

    # LLM & Embedding model choice
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    match config.inference:
        case "openai":
            os.environ["OPENAI_API_KEY"] = config.openai_api_key
            llm = OpenAI(model="gpt-4o-mini", request_timeout=600.0, temperature=0)
        case "ollama":
            llm = Ollama(model="llama3", request_timeout=600.0, temperature=0, base_url=config.llm_base_url)
        case _:
            raise ValueError("Unsupported inference model specified")
        
    Settings.llm = llm

    reader = SimpleDirectoryReader(
        recursive=True,
        input_dir=INPUT_DIR,
        required_exts=REQUIRED_EXTS
    )
    
    mongodb_client = pymongo.MongoClient(config.mongo_atlas_uri)

    # Create an instance of MongoDBAtlasVectorSearch
    vector_store = MongoDBAtlasVectorSearch(mongodb_client, db_name = config.mongodb_atlas_db_name,
    collection_name = config.mongodb_atlas_collection_name, index_name = config.mongodb_atlas_index_name)
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if RE_INDEX:
        all_docs = []
        for docs in reader.iter_data():
            for doc in docs:
                all_docs.append(doc)

        documents = reader.load_data(show_progress=True, num_workers=4)

        parser = SentenceSplitter()
        nodes = parser.get_nodes_from_documents(documents, show_progress=True)

        vector_index = VectorStoreIndex(
            nodes=nodes, storage_context=storage_context, show_progress=True)
    else:
        vector_index = VectorStoreIndex.from_vector_store(vector_store)


    (text_qa_template, refine_template) = setup_prompts()
    query_engine = vector_index.as_query_engine(
        text_qa_template=text_qa_template,
        refine_template=refine_template,
        streaming=True, similarity_top_k=3)

    app.state.llm = llm
    app.state.query_engine = query_engine
    app.state.vector_store = vector_store
