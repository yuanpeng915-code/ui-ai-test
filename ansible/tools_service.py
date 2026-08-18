"""ponytail: single-file Flask ping-pong verification service."""
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, request

app = Flask(__name__)
_last_ping: Optional[int] = None

ANSIBLE_DIR: Path = Path(__file__).parent
INVENTORY: Path = ANSIBLE_DIR / "inventory.ini"

# 架构名 -> 安装包 URL 后缀
ARCH_SUFFIX_MAP: Dict[str, str] = {
    "arm_64": "arm",
    "aarch64": "arm",
    "x86_64": "x86",
    "amd64": "x86",
}


@app.route("/sshCheck/ping")
def ping():
    global _last_ping
    print(request.headers)
    _last_ping = int(time.time())
    return {"code": "ok", "data":{"time": _last_ping}}

@app.route("/sshCheck/pong")
def pong():
    return {
        "code": "error" if _last_ping is None else "ok",
        "data":{
            "last_time": _last_ping,
            "current_time": int(time.time()),
        }
    }

@app.route("/sshCheck/clear")
def clear():
    global _last_ping
    _last_ping = None
    return {"code": "ok", "data": None}

@app.route("/ftp/getFileNum")
def get_file_num():
    p = Path(request.args.get("path", "."))
    count = sum(1 for f in p.iterdir() if f.is_file()) if p.is_dir() else 0
    return {"code": "ok", "data": {"path": str(p), "count": count}}


def _run_ansible_playbook(playbook: str, extra_vars: Dict[str, Any]) -> Dict[str, Any]:
    """调用 ansible-playbook 执行部署，返回执行结果。"""
    cmd: List[str] = [
        "ansible-playbook",
        str(ANSIBLE_DIR / playbook),
        "-i", str(INVENTORY),
        "--extra-vars", json.dumps(extra_vars),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as e:
        return {
            "returncode": -1,
            "stdout": e.stdout or "",
            "stderr": f"ansible-playbook 执行超时: {e}",
        }
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@app.route("/appServer/deploy", methods=["POST"])
def appserver_deploy() -> Tuple[Dict[str, Any], int]:
    """通过 ansible 对远端应用服务器执行 usmdriver 部署。

    请求体 JSON 参数:
        platform:    linux | windows
        architecture: 架构，如 arm_64（组名取大写 ARM_64，URL 后缀映射为 arm）
        server_ip:   下载服务器地址，如 10.113.56.224:443
        ak:          接入 ak（必填）
        sk:          接入 sk（必填）
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    platform: str = data.get("platform", "linux")
    architecture: str = data.get("architecture", "arm_64")
    server_ip: str = data.get("server_ip", "10.113.56.224:443")
    ak: Optional[str] = data.get("ak")
    sk: Optional[str] = data.get("sk")

    if platform not in ("linux", "windows"):
        return {"code": "error", "msg": "platform 必须为 linux 或 windows"}, 400
    if not ak or not sk:
        return {"code": "error", "msg": "ak 和 sk 为必填参数"}, 400
    if not server_ip:
        return {"code": "error", "msg": "server_ip 为必填参数"}, 400

    arch_suffix: str = ARCH_SUFFIX_MAP.get(architecture, architecture)
    target_group: str = f"{platform}_{architecture.upper()}"
    playbook: str = "appserver_deploy_linux.yml" if platform == "linux" else "appserver_deploy_windows.yml"
    extra_vars: Dict[str, Any] = {
        "target_group": target_group,
        "server_ip": server_ip,
        "arch_suffix": arch_suffix,
        "ak": ak,
        "sk": sk,
    }
    ansible_result: Dict[str, Any] = _run_ansible_playbook(playbook, extra_vars)
    ok: bool = ansible_result["returncode"] == 0
    return {"code": "ok" if ok else "error", "data": ansible_result}, 200 if ok else 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
