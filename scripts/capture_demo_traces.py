"""데모용 질의를 실제 에이전트로 실행해 web/public/demo/traces.json으로 저장한다.

각 질의를 agent.stream()으로 실행하고, 노드 진행 이벤트와 최종 응답을 그대로 녹화한다.
프론트엔드(web/)는 이 파일을 키 없이 재생하므로, 데모에 보이는 답변·근거 조문·검색 전략은
모두 실제 실행 결과다.

사전 조건: make up && make index, OPENAI_API_KEY.
실행:       OPENAI_API_KEY=... uv run python scripts/capture_demo_traces.py
"""
import json
from pathlib import Path

from korean_maritime_law_rag.agent.graph import Agent
from korean_maritime_law_rag.bootstrap import build_live_fallback, build_retriever
from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.llm import get_chat_model

# 골드셋(tests/qa_pairs.yaml)에서 유형별로 고른 질의. 검색이 잘 되는 검증된 문항이다.
QUESTIONS: list[tuple[str, str, str]] = [
    ("fishing-radio", "어선에 무선설비를 갖추지 않고 항행하면 어떤 벌칙이 적용되나요?", "멀티홉 · 그래프 확장"),
    ("build-inspection", "선박을 건조할 때 받아야 하는 건조검사를 받지 않으면 어떤 처벌을 받나요?", "멀티홉 · 위임 추적"),
    ("survey-validity", "선박검사증서의 유효기간은 최대 몇 년인가요?", "단일 조문"),
    ("fishing-def", "어선법에서 '어선'이란 어떤 선박을 말하나요?", "정의 조문"),
    ("stowaway", "외국 선박을 이용해 밀입국한 사람은 출입국관리법상 어떻게 처벌되나요?", "근거 없음 · 거절"),
]


def main() -> None:
    s = load_settings(Path("configs/demo.yaml"))
    agent = Agent(
        build_retriever(s),
        get_chat_model(s),
        top_k=s.top_k,
        live_fallback=build_live_fallback(s),
    )

    traces = []
    for trace_id, question, tag in QUESTIONS:
        events = []
        response = None
        for event in agent.stream(question):
            if event["step"] == "final":
                response = event["response"]
            else:
                events.append(event)
        assert response is not None, f"최종 응답 없음: {question}"
        traces.append(
            {"id": trace_id, "question": question, "tag": tag, "events": events, "response": response}
        )
        summary = "거절" if response["refused"] else f"근거 {len(response['evidence'])}건"
        print(f"  {trace_id}: {response['query_type']}/{response['strategy']} · {summary}")

    out = Path("web/public/demo/traces.json")
    out.write_text(json.dumps(traces, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {out} ({len(traces)}건)")


if __name__ == "__main__":
    main()
