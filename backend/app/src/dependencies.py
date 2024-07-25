from fastapi import Request

def get_llm(request: Request):
    return request.app.state.llm

def get_query_engine(request: Request):
    return request.app.state.query_engine
