"""로컬 실행 준비 상태 빠른 점검. 사용: make smoke"""
from pathlib import Path

from korean_maritime_law_rag.config import load_settings
from korean_maritime_law_rag.diagnostics import check_local_artifacts


def main() -> None:
    settings = load_settings(Path("configs/demo.yaml"))
    checks = check_local_artifacts(settings)
    failed = False
    for check in checks:
        status = "OK" if check.ok else "FAIL"
        print(f"{status:4} {check.name}: {check.detail}")
        failed = failed or not check.ok
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
