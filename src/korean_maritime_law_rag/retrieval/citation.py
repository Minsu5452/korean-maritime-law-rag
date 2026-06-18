import re

# 그룹 내 공백을 필수(\s)로 + 반복 제한({0,8})해 중첩 수량자 모호성(ReDoS) 제거.
# 이전 `(?:\s?[가-힣ㆍ]+)*`는 '법…제N조' 없는 긴 한글 입력에서 지수적 백트래킹을 유발.
_CITATION = re.compile(
    r"「?(?P<law>[가-힣ㆍ]+(?:\s[가-힣ㆍ]+){0,8}\s?법(?:률)?)」?\s*제(?P<num>\d+)조(?P<sub>의\d+)?"
)


def parse_citation(query: str) -> tuple[str, str] | None:
    """질의에서 '법령명 + 제N조' 패턴을 찾는다. 법령명이 없으면 None(모호)."""
    m = _CITATION.search(query)
    if not m:
        return None
    return m.group("law").strip(), f"제{m.group('num')}조" + (m.group("sub") or "")
