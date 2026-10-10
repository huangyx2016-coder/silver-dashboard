"""Send silver dashboard update notification to 邓子平."""
import json, os, requests

APP_ID = os.environ["FEISHU_APP_ID"]
APP_SECRET = os.environ["FEISHU_APP_SECRET"]
OPEN_ID = "ou_744c1351a6b58ac8b8e259184cd1dbc8"

token = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=30
).json()["tenant_access_token"]

resp = requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={
        "receive_id": OPEN_ID,
        "msg_type": "text",
        "content": json.dumps({"text": "银饰仪表盘已更新\nhttps://huangyx2016-coder.github.io/silver-dashboard/"}, ensure_ascii=False),
    },
    timeout=30,
).json()

if resp.get("code") == 0:
    print("邓子平: OK")
else:
    print(f"Failed: {resp}")
    exit(1)
