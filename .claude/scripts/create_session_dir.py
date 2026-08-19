import json
import sys
from datetime import datetime
from pathlib import Path


def create_session_dir(payload: dict[str, str]) -> Path:
    """根据会话 id 在 workspace 下创建本次会话的工作目录"""
    project_root = Path(__file__).resolve().parents[2]
    session_id = payload.get("session_id", "unknown")
    date_str = datetime.now().strftime("%Y%m%d")
    session_dir = project_root / "workspace" / f"session_{date_str}_{session_id[:8]}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def main() -> None:
    payload = json.loads(sys.stdin.read())
    session_dir = create_session_dir(payload)
    print(f"当前会话工作目录: {session_dir} (所有临时文件、探索脚本都放在此目录)")


if __name__ == "__main__":
    main()
