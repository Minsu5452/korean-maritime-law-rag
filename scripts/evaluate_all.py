"""에이전트를 골드셋에 1회 실행해 응답 품질과 지연 시간을 측정한다.

RAGAS rows(reports/ragas_rows.json)도 저장해 격리 venv에서 별도 채점한다(의존성 충돌 회피).
사전 조건: make up && make index, OPENAI_API_KEY. 모델은 env로 주입:
  MLR_LLM_MODEL=openai:gpt-4o-mini MLR_JUDGE_MODEL=openai:gpt-4o MLR_RERANK=true
"""
import json
import time
from pathlib import Path

from korean_maritime_law_rag.agent.graph import Agent
from korean_maritime_law_rag.agent.router import route
from korean_maritime_law_rag.bootstrap import build_retriever
from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.evaluation.faithfulness import faithfulness_metrics, judge_faithfulness
from korean_maritime_law_rag.evaluation.harness import agent_metrics, load_gold
from korean_maritime_law_rag.evaluation.latency import percentiles
from korean_maritime_law_rag.evaluation.ragas_eval import build_ragas_rows
from korean_maritime_law_rag.llm import get_chat_model, get_judge_model


def _hit1(retriever, q: str, strat: str, gold: list[str], top_k: int) -> int:
    r = retriever.search(q, strat, top_k=top_k)
    return int(bool(r) and r[0].doc_id in set(gold))


def main() -> None:
    s = load_settings(Path("configs/demo.yaml"))
    retriever = build_retriever(s)
    agent = Agent(retriever, get_chat_model(s), top_k=s.top_k)
    judge = get_judge_model(s)
    gold = load_gold(Path("tests/qa_pairs.yaml"))
    meta = retriever.meta

    def text_of(d: str) -> str:
        a = meta.get(d)
        return f"{a.law_name} {a.article_no}: {a.text}" if a else ""

    records, ragas_records, lat = [], [], []
    oracle_hits = llm_hits = answerable = 0
    for g in gold:
        t0 = time.perf_counter()
        resp = agent.answer(g.question)
        lat.append((time.perf_counter() - t0) * 1000)
        records.append({"id": g.id, "gold_type": g.type, "pred_type": resp.query_type,
                        "gold_docs": g.gold, "cited_docs": resp.citations, "refused": resp.refused})
        if g.type != "unanswerable":
            answerable += 1
            oracle_hits += _hit1(retriever, g.question, route(g.type), g.gold, s.top_k)
            llm_strategy = "hybrid" if resp.refused else route(resp.query_type)
            llm_hits += _hit1(retriever, g.question, llm_strategy, g.gold, s.top_k)
            ragas_records.append({
                "question": g.question, "answer": resp.answer,
                "contexts": [text_of(d) for d in resp.citations if d in meta],
                "reference": " / ".join(text_of(d) for d in g.gold)})

    am = agent_metrics(records)
    am["oracle_routing_hit1"] = oracle_hits / answerable if answerable else 0.0
    am["llm_routing_hit1"] = llm_hits / answerable if answerable else 0.0

    verdicts = [judge_faithfulness(r["answer"], "\n\n".join(r["contexts"]) or "(인용 없음)", judge)
                for r in ragas_records]
    fm = faithfulness_metrics(verdicts)
    latm = percentiles(lat)
    rows = build_ragas_rows(ragas_records)

    out = Path("reports")
    out.mkdir(exist_ok=True)
    (out / "agent_eval.json").write_text(
        json.dumps({"metrics": am, "records": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "faithfulness_eval.json").write_text(
        json.dumps({"metrics": fm, "judge": s.judge_model}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "ragas_rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "latency.json").write_text(json.dumps(latm, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# 에이전트 평가", "",
          "이 파일은 `scripts/evaluate_all.py`로 생성한 마지막 저장 결과입니다.",
          "현재 기본 모델과 실행 설정은 `.env.example`과 `src/korean_maritime_law_rag/config.py`를 기준으로 확인하고,",
          "모델이나 검색 설정을 바꾼 뒤에는 `OPENAI_API_KEY=... uv run python scripts/evaluate_all.py`로 다시 생성해야 합니다.", "",
          "| 지표 | 값 |", "|---|---|",
          f"| 분류 정확도 | {am['classification_accuracy']:.3f} |",
          f"| 답변 가능 질문의 인용 정확도 | {am['citation_hit_rate']:.3f} |",
          f"| 근거 없는 질문의 거절 정확도 | {am['refusal_accuracy']:.3f} |",
          f"| 정답 유형 기준 라우팅 hit@1 | {am['oracle_routing_hit1']:.3f} |",
          f"| 모델 라우팅 hit@1 | {am['llm_routing_hit1']:.3f} |",
          f"| 근거성 | {fm['faithfulness_rate']:.3f} ({fm['grounded']}/{fm['n']}) |",
          f"| 응답 시간 p50 / p95 (ms) | {latm['p50']:.0f} / {latm['p95']:.0f} |", "",
          "모델 라우팅 hit@1은 답변 가능 문항에서 모델이 고른 전략으로 rank-1 정답을 맞힌 비율입니다.",
          "모델이 답변 가능 문항을 거절한 경우에는 hybrid로 검색해 검색 품질만 따로 계산했습니다.", ""]
    (out / "agent_eval.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
