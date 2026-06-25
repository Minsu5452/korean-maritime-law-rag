"""질의당 토큰·비용 실측.

사용: OPENAI_API_KEY=<키> uv run python scripts/measure_cost.py [--per-type single=6,multihop=8,definition=4]
사전 조건: make up && make index (인덱스 필요)

RAG 에이전트를 골드셋 표본에 돌려 질의당 입력/출력 토큰을 실측하고,
공개 단가 기준으로 질의당 비용을 추정해 reports/cost.md에 저장한다.
"""
import argparse
import json
from pathlib import Path

from langchain_core.callbacks import get_usage_metadata_callback

from korean_maritime_law_rag.agent.graph import Agent
from korean_maritime_law_rag.bootstrap import build_live_fallback, build_retriever
from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.evaluation.cost import Price, summarize
from korean_maritime_law_rag.evaluation.harness import GoldItem, load_gold
from korean_maritime_law_rag.llm import get_chat_model

# OpenAI 공개 단가 기준 추정(USD per 1M tokens). 단가가 바뀌면 이 값만 갱신해 재계산한다.
PRICE = Price(input_per_1m=0.15, output_per_1m=0.60)  # gpt-4o-mini


def select(gold: list[GoldItem], per_type: dict[str, int]) -> list[GoldItem]:
    """유형별 앞에서부터 정해진 수만큼 답변 가능 문항을 고른다(결정적)."""
    picked: list[GoldItem] = []
    taken: dict[str, int] = {}
    for item in gold:
        if item.type == "unanswerable":
            continue
        if taken.get(item.type, 0) < per_type.get(item.type, 0):
            picked.append(item)
            taken[item.type] = taken.get(item.type, 0) + 1
    return picked


def parse_per_type(spec: str) -> dict[str, int]:
    return {k: int(v) for k, v in (kv.split("=") for kv in spec.split(","))}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--per-type", default="single=6,multihop=8,definition=4")
    p.add_argument("--top-k", type=int, default=5)
    args = p.parse_args()

    s = load_settings(Path("configs/demo.yaml"))
    gold = load_gold(Path("tests/qa_pairs.yaml"))
    sample = select(gold, parse_per_type(args.per_type))

    retriever = build_retriever(s)
    agent = Agent(retriever, get_chat_model(s), top_k=args.top_k,
                  live_fallback=build_live_fallback(s))

    usages: list[tuple[int, int]] = []
    records: list[dict] = []
    for item in sample:
        with get_usage_metadata_callback() as cb:
            resp = agent.answer(item.question)
        inp = sum(v.get("input_tokens", 0) for v in cb.usage_metadata.values())
        out = sum(v.get("output_tokens", 0) for v in cb.usage_metadata.values())
        usages.append((inp, out))
        records.append({
            "id": item.id, "type": item.type, "question": item.question,
            "input_tokens": inp, "output_tokens": out,
            "strategy": resp.strategy, "query_type": resp.query_type,
            "refused": resp.refused, "citations": resp.citations,
            "retrieval_attempts": resp.retrieval_attempts,
            "generation_attempts": resp.generation_attempts,
            "answer": resp.answer,
        })
        print(f"{item.id} {item.type:10s} in={inp:5d} out={out:4d} "
              f"strat={resp.strategy} cites={len(resp.citations)}")

    summary = summarize(usages, PRICE)
    out_json = {
        "model": s.llm_model,
        "price_usd_per_1m": {"input": PRICE.input_per_1m, "output": PRICE.output_per_1m},
        "summary": summary,
        "records": records,
    }
    Path("reports/cost.json").write_text(
        json.dumps(out_json, ensure_ascii=False, indent=2), encoding="utf-8")

    md = _render_md(s.llm_model, summary)
    Path("reports/cost.md").write_text(md, encoding="utf-8")
    print("\n" + md)


def _render_md(model: str, summary: dict) -> str:
    won = summary["mean_cost_usd"] * 1400  # 참고용 환율(원), 대략치
    return (
        "# 질의당 토큰·비용\n\n"
        f"에이전트 모델 `{model}` 기준, 골드셋 답변 가능 문항 {summary['n']}건을 실제로 "
        "실행해 측정했습니다.\n"
        "비용은 OpenAI 공개 단가(입력 $0.15 / 출력 $0.60 per 1M tokens) 기준 추정이며, "
        "단가가 바뀌면 `scripts/measure_cost.py`의 `PRICE`를 갱신해 재계산합니다.\n\n"
        "| 지표 | 수치 |\n|---|---:|\n"
        f"| 측정 문항 | {summary['n']} |\n"
        f"| 질의당 입력 토큰(평균) | {summary['mean_input']:.0f} |\n"
        f"| 질의당 출력 토큰(평균) | {summary['mean_output']:.0f} |\n"
        f"| 질의당 비용(추정) | ${summary['mean_cost_usd']:.5f} (약 {won:.1f}원) |\n\n"
        "재현: `OPENAI_API_KEY=... uv run python scripts/measure_cost.py`\n"
    )


if __name__ == "__main__":
    main()
