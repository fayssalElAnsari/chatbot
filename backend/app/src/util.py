from typing import Generator
from src.model.chunk import Chunk, ChunkType


def chat_streamer(streaming_response) -> Generator[str, None, None]:
    response_sources = set()
    for response_source in streaming_response.source_nodes:
        if response_source.score >= 0.7:
            response_sources.add(response_source.node.metadata['file_name'])
    if response_sources:
        sources_chunk = Chunk(type=ChunkType.RELEVANT_SOURCES,
                              content=list(response_sources), is_stream_end=False)
        yield f"data: {str(sources_chunk)}\n\n"

    token = None
    for token in streaming_response.response_gen:
        chunk = Chunk(type=ChunkType.PARTIAL_ANSWER,
                      content=token, is_stream_end=False)
        yield f"data: {str(chunk)}\n\n"
    end_chunk = Chunk(type=ChunkType.PARTIAL_ANSWER,
                      content=token, is_stream_end=True)
    yield f"data: {str(end_chunk)}\n\n"
