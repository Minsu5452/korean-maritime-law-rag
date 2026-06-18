import re
from typing import Literal

from korean_maritime_law_rag.models import CrossRef

_EXTERNAL = re.compile(
    r"「(?P<law>[^」]+)」(?:\s*\(이하[^)]*\))?\s*제(?P<num>\d+)조(?P<sub>의\d+)?(?:제(?P<clause>\d+)항)?"
)
_INTERNAL = re.compile(r"제(?P<num>\d+)조(?P<sub>의\d+)?(?:제(?P<clause>\d+)항)?")
# 시행령/규칙 본문의 '법 제N조' 약식 상위법 참조. 앞 글자가 한글이면(예: '선박안전법 제5조')
# 명명참조이므로 제외한다.
_PARENT = re.compile(r"(?<![가-힣])법\s*제(?P<num>\d+)조(?P<sub>의\d+)?")
_APPLY_WINDOW = 30  # 참조 직후 이 범위 안에 '준용'이 있으면 rel=apply


def _rel(text: str, end: int) -> Literal["cite", "apply"]:
    return "apply" if "준용" in text[end : end + _APPLY_WINDOW] else "cite"


def extract_cross_refs(text: str) -> list[CrossRef]:
    refs: list[CrossRef] = []
    spans: list[tuple[int, int]] = []

    for m in _EXTERNAL.finditer(text):
        spans.append(m.span())
        refs.append(CrossRef(
            ref_type="external",
            target_law=m.group("law").strip(),
            target_article=f"제{m.group('num')}조" + (m.group("sub") or ""),
            target_clause=f"제{m.group('clause')}항" if m.group("clause") else None,
            rel=_rel(text, m.end()),
        ))

    for m in _INTERNAL.finditer(text):
        if any(s <= m.start() < e for s, e in spans):  # external 매치 내부면 스킵
            continue
        refs.append(CrossRef(
            ref_type="internal",
            target_article=f"제{m.group('num')}조" + (m.group("sub") or ""),
            target_clause=f"제{m.group('clause')}항" if m.group("clause") else None,
            rel=_rel(text, m.end()),
        ))
    return refs


def extract_parent_refs(text: str) -> list[str]:
    """시행령/규칙 본문의 '법 제N조' 약식 상위법 참조에서 조문번호를 추출한다(순서 보존·중복 제거)."""
    seen: set[str] = set()
    out: list[str] = []
    for m in _PARENT.finditer(text):
        art = f"제{m.group('num')}조" + (m.group("sub") or "")
        if art not in seen:
            seen.add(art)
            out.append(art)
    return out
