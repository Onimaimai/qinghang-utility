#!/bin/bash

# 水电费查询面板启动脚本

cd /opt/qinghang/backend

echo "启动水电费查询面板..."
echo "访问地址: http://localhost:8000"
echo "按 Ctrl+C 停止服务"
echo ""

# 初始化数据库
python3 -c "from database import init_db; init_db()" 2>/dev/null

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
