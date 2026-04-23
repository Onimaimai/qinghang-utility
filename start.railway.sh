#!/bin/bash
set -e

# 启动后端服务
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 启动Nginx
nginx -g "daemon off;" &
# 等待任一进程退出
wait -n
