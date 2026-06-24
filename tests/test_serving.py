from fastapi.testclient import TestClient

from korean_maritime_law_rag.agent.state import AgentResponse
from korean_maritime_law_rag.serving.app import app, get_agent


class FakeAgent:
    def answer(self, query: str) -> AgentResponse:
        return AgentResponse(answer="3년 이하의 징역.", citations=["100::제83조"],
                             query_type="multihop", strategy="graph", refused=False)

    def stream(self, query: str):
        yield {"step": "classify", "label": "질문 유형 분류",
               "query_type": "multihop", "strategy": None}
        yield {"step": "final", "response": self.answer(query).model_dump()}


def test_health():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"


def test_ready_uses_agent_dependency():
    app.dependency_overrides[get_agent] = lambda: FakeAgent()
    try:
        client = TestClient(app)
        r = client.get("/ready")
        assert r.status_code == 200
        assert r.json() == {"status": "ready"}
    finally:
        app.dependency_overrides.clear()


def test_query_endpoint_returns_agent_response():
    app.dependency_overrides[get_agent] = lambda: FakeAgent()
    try:
        client = TestClient(app)
        r = client.post("/query", json={"query": "건조검사 위반 처벌은?"})
        assert r.status_code == 200
        body = r.json()
        assert body["citations"] == ["100::제83조"]
        assert body["strategy"] == "graph"
    finally:
        app.dependency_overrides.clear()


def test_query_stream_emits_sse_events():
    app.dependency_overrides[get_agent] = lambda: FakeAgent()
    try:
        client = TestClient(app)
        r = client.post("/query/stream", json={"query": "건조검사 위반 처벌은?"})
        assert r.status_code == 200
        assert "text/event-stream" in r.headers["content-type"]
        assert "data:" in r.text
        assert '"step": "final"' in r.text
        assert "100::제83조" in r.text
    finally:
        app.dependency_overrides.clear()


def test_cors_allows_local_frontend_origin():
    client = TestClient(app)
    r = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
