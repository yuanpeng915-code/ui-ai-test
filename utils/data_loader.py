import json
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent

# 测试
ACCOUNTS = json.loads((ROOT_PATH / "env/test.json").read_text(encoding="utf-8"))

# 路由
ROUTERS = json.loads((ROOT_PATH / "configs/router.json").read_text(encoding="utf-8"))

# 测试资产
ASSETS = json.loads((ROOT_PATH / "data/assets.json").read_text(encoding="utf-8"))

# driver配置文件
CONFIG = json.loads((ROOT_PATH / "configs/driver.json").read_text(encoding="utf-8"))