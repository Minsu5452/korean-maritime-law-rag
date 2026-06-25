import json
import logging
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)
BASE = "https://www.law.go.kr/DRF"


class LawNotCurrentError(Exception):
    """검색 결과에 '현행' 법령이 없음 — 폐지·전부개정(예: 해사안전법 분리) 신호."""


def subordinate_names(base_law: str) -> list[str]:
    """기본 법률명으로부터 하위법령(시행령·시행규칙) 검색명을 만든다."""
    return [f"{base_law} 시행령", f"{base_law} 시행규칙"]


def is_amended(cached_raw: dict, search_entry: dict) -> bool:
    """캐시된 법령 원문과 최신 검색결과의 공포번호를 비교해 개정 여부를 판단한다.

    최신 공포번호가 비어 있으면(정보 없음) 보수적으로 변경 아님(False)으로 본다.
    """
    cached = str(cached_raw.get("법령", {}).get("기본정보", {}).get("공포번호", "")).strip()
    latest = str(search_entry.get("공포번호", "")).strip()
    return bool(latest) and latest != cached


class LawApiClient:
    def __init__(self, oc: str, client: httpx.Client | None = None):
        self.oc = oc
        self.client = client or httpx.Client(timeout=30)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )
    def _get(self, endpoint: str, **params) -> dict:
        resp = self.client.get(f"{BASE}/{endpoint}", params={"OC": self.oc, "type": "JSON", **params})
        resp.raise_for_status()
        if resp.headers.get("content-type", "").startswith("text/html"):
            raise ValueError("law.go.kr이 HTML을 반환 — OC 키 등록 여부를 확인하세요")
        return resp.json()

    def search_law(self, name: str) -> dict:
        data = self._get("lawSearch.do", target="law", query=name)
        entries = data.get("LawSearch", {}).get("law", [])
        if isinstance(entries, dict):  # 단일 결과는 dict(응답 변형)
            entries = [entries]
        current = [e for e in entries if e.get("현행연혁코드") == "현행"]
        exact = [e for e in current if e.get("법령명한글", "").strip() == name]
        if not (exact or current):
            raise LawNotCurrentError(f"'{name}': 현행 법령 없음 — 법령명 변경/폐지 확인 필요")
        if not exact:
            logger.warning("'%s': 정확 일치 없음 — 현행 첫 항목 '%s' 사용", name, current[0].get("법령명한글"))
        return (exact or current)[0]

    def fetch_law(self, mst: str) -> dict:
        return self._get("lawService.do", target="law", MST=mst)

    def collect(self, law_names: list[str], cache_dir: Path) -> list[Path]:
        """법령명 목록을 수집한다. 현행본이 없는 항목(없는 시행규칙 등)은 건너뛰고 계속한다."""
        cache_dir.mkdir(parents=True, exist_ok=True)
        saved: list[Path] = []
        for name in law_names:
            try:
                entry = self.search_law(name)
            except LawNotCurrentError:
                logger.info("스킵(현행 없음): %s", name)
                continue
            raw = self.fetch_law(entry["법령일련번호"])
            path = cache_dir / f"{entry['법령ID']}.json"
            path.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
            logger.info("수집: %s -> %s", name, path.name)
            saved.append(path)
        return saved
