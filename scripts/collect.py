"""configs/laws.yaml의 법령과 그 시행령·시행규칙을 수집해 data/cache/raw/에 저장한다.

사용: MLR_LAW_OC=<키> make collect           (법률+시행령+시행규칙)
      MLR_LAW_OC=<키> python scripts/collect.py --statutes-only  (법률만)
"""
import argparse
import logging
from pathlib import Path

import yaml

from korean_maritime_law_rag.collectors.law_api import LawApiClient, subordinate_names
from korean_maritime_law_rag.config import load_settings

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)  # 요청 URL(OC 키 포함) 로그 노출 방지


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--statutes-only", action="store_true", help="시행령·시행규칙 제외")
    args = parser.parse_args()

    settings = load_settings(Path("configs/demo.yaml"))
    if not settings.law_oc:
        raise SystemExit("MLR_LAW_OC 환경변수에 OC 키를 설정하세요 (open.law.go.kr 발급)")

    base = yaml.safe_load(Path("configs/laws.yaml").read_text(encoding="utf-8"))["laws"]
    names: list[str] = []
    for law in base:
        names.append(law)
        if not args.statutes_only:
            names.extend(subordinate_names(law))

    paths = LawApiClient(oc=settings.law_oc).collect(names, settings.cache_dir)
    print(f"수집 완료: {len(paths)}/{len(names)}개 법령 -> {settings.cache_dir}")


if __name__ == "__main__":
    main()
