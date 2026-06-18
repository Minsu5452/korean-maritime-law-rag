import json
from collections.abc import Iterator
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from korean_maritime_law_rag.agent.graph import Agent
from korean_maritime_law_rag.agent.state import AgentResponse
from korean_maritime_law_rag.bootstrap import build_live_fallback, build_retriever
from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.llm import get_chat_model
from korean_maritime_law_rag.observability import build_langfuse_callbacks

app = FastAPI(title="korean-maritime-law-rag")
_agent: Agent | None = None


class QueryRequest(BaseModel):
    query: str


def get_agent() -> Agent:
    """지연 초기화된 Agent 싱글턴. 테스트는 app.dependency_overrides로 교체."""
    global _agent
    if _agent is None:
        s = load_settings(Path("configs/demo.yaml"))
        _agent = Agent(build_retriever(s), get_chat_model(s), top_k=s.top_k,
                       live_fallback=build_live_fallback(s),
                       callbacks=build_langfuse_callbacks(s))
    return _agent


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready(_agent: Agent = Depends(get_agent)) -> dict:
    return {"status": "ready"}


@app.post("/query")
def query(req: QueryRequest, agent: Agent = Depends(get_agent)) -> AgentResponse:
    return agent.answer(req.query)


@app.post("/query/stream")
def query_stream(req: QueryRequest, agent: Agent = Depends(get_agent)) -> StreamingResponse:
    """LangGraph 노드 진행을 SSE로 스트리밍한다(classify→retrieve→…→final).
    멀티 LLM 라운드트립 동안 사용자가 진행 상황을 즉시 보도록 한다."""
    def events() -> Iterator[str]:
        for event in agent.stream(req.query):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
