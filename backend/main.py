from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import init_db
from routers import auth, user, data
from services.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="水电费查询面板",
    description="多用户水电费查询系统API",
    version="1.0.0"
)

# CORS配置
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# 从环境变量获取前端域名
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(data.router)


@app.on_event("startup")
async def startup():
    """应用启动时初始化数据库和定时任务"""
    init_db()
    start_scheduler()


@app.on_event("shutdown")
async def shutdown():
    """应用关闭时停止定时任务"""
    stop_scheduler()


@app.get("/health")
async def health():
    return {"status": "ok"}


# 服务前端静态文件
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    # 挂载静态资源目录
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    # 所有非API路由返回index.html（支持Vue Router）
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # 如果请求的是文件且存在，返回文件
        file_path = os.path.join(FRONTEND_DIST, path)
        if path and os.path.isfile(file_path):
            return FileResponse(file_path)
        # 否则返回index.html
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
