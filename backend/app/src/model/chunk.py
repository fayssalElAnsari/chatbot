import json
from enum import Enum

class ChunkType(Enum):
    RELEVANT_SOURCES = 1
    PARTIAL_ANSWER = 2
    IDENTIFIERS = 3

class Chunk:
    """
    A class representing a chunk of data with type, content, and a flag indicating if it is the end of the stream.
    """
    def __init__(self, type: ChunkType, content, is_stream_end: bool):
        self.type = type
        self.content = content
        self.is_stream_end = is_stream_end

    def __str__(self):
        # Create a dictionary with the instance's attributes
        chunk_dict = {
            "type": self.type.name,  # Use the name of the enum member
            "content": self.content,
            "is_stream_end": self.is_stream_end
        }
        # Convert the dictionary to a JSON string + u'\u241e'
        return json.dumps(chunk_dict) 