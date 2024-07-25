from fastapi import FastAPI
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, set_global_handler
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.core.node_parser import SentenceSplitter
from src.constants import MONGO_URI, LLM_BASE_URL, RE_INDEX, REQUIRED_EXTS, INPUT_DIR, qa_prompt_str, refine_prompt_str
import phoenix as px
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate


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

    llm = Ollama(model="llama3", request_timeout=600.0,
                 temperature=0, base_url=LLM_BASE_URL)
    Settings.llm = llm

    reader = SimpleDirectoryReader(
        recursive=True,
        input_dir=INPUT_DIR,
        required_exts=REQUIRED_EXTS
    )

    storage_context = StorageContext.from_defaults(
        docstore=MongoDocumentStore.from_uri(uri=MONGO_URI),
        index_store=MongoIndexStore.from_uri(uri=MONGO_URI)
    )

    if RE_INDEX:
        all_docs = []
        for docs in reader.iter_data():
            for doc in docs:
                all_docs.append(doc)

        documents = reader.load_data(show_progress=True, num_workers=4)

        parser = SentenceSplitter()
        nodes = parser.get_nodes_from_documents(documents, show_progress=True)

        vector_index = VectorStoreIndex(
            nodes=nodes, storage_context=storage_context)
        storage_context.persist()
    else:
        storage_context = StorageContext.from_defaults(
            docstore=MongoDocumentStore.from_uri(uri=MONGO_URI),
            index_store=MongoIndexStore.from_uri(uri=MONGO_URI)
        )
        vector_index = load_index_from_storage(storage_context=storage_context)

    (text_qa_template, refine_template) = setup_prompts()

    query_engine = vector_index.as_query_engine(
        text_qa_template=text_qa_template,
        refine_template=refine_template,
        streaming=True, similarity_top_k=3)

    app.state.llm = llm
    app.state.query_engine = query_engine

    # View the traces in the Phoenix UI
    # px.active_session().url
