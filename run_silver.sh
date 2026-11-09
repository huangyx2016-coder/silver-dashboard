#!/bin/bash
# 银饰看板：抓数据→生成页面→发布到 gh-pages→飞书通知
# 迁移自 GitHub Actions（2026-11-09），脚本不再公开到仓库
set -uo pipefail
cd /root/silver-dashboard || exit 1
LOG=/var/log/silver-dashboard.log
echo "===== $(date "+%F %T") start =====" >> "$LOG"

/usr/bin/python3 fetch_and_build.py >> "$LOG" 2>&1 || { echo "build FAILED" >> "$LOG"; exit 1; }

# 发布：gh-pages 仅保留静态文件
PUB=/tmp/silver-pub
rm -rf "$PUB"; mkdir -p "$PUB"
cp index.html silver_data.json "$PUB"/
touch "$PUB/.nojekyll"
cd "$PUB" || exit 1
git init -q -b gh-pages
git config user.name "Aliyun Bot"; git config user.email "bot@aliyun-server"
git add -A
git commit -qm "Deploy $(date +%FT%T)"
GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git push -qf git@github.com:huangyx2016-coder/silver-dashboard.git gh-pages >> "$LOG" 2>&1 || { echo "push FAILED" >> "$LOG"; exit 1; }
echo "published gh-pages" >> "$LOG"

cd /root/silver-dashboard || exit 1
set -a; . /root/silver-dashboard/.feishu.env; set +a
/usr/bin/python3 notify_silver.py >> "$LOG" 2>&1
echo "===== $(date "+%F %T") done =====" >> "$LOG"
