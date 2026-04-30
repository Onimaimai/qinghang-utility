# 水电费查询面板

多用户水电费查询系统，支持自动爬取公寓管理系统数据、数据可视化、余额不足提醒。

演示地址：https://qinghang-utility-production.up.railway.app/

## 功能特性

- 用户注册登录系统
- 安全存储公寓系统凭证
- 自动爬取水电费余额、余额明细、能耗记录
- ECharts图表可视化
- PushPlus微信余额不足提醒

<img width="353" height="720" alt="lQDPKIMNqH6n8aHNCjPNBQCwv5ue9UZ14IcJyLX3xC6tAA_1280_2611 jpg_720x720" src="https://github.com/user-attachments/assets/e29e78c7-67e8-4546-87e9-27242683e54d" />
<img width="353" height="720" alt="lQDPKG7U0ISD86HNCjTNBQCwVl0X6ERyC1wJyLX4yNsvAA_1280_2612 jpg_720x720" src="https://github.com/user-attachments/assets/5fb6813b-b6fc-43e3-a4e3-d1b29f52b7cc" />
<img width="353" height="720" alt="lQDPJxXCgO4gY6HNCjPNBQCwuPQTLAO1tJQJyLX5xo6HAA_1280_2611 jpg_720x720" src="https://github.com/user-attachments/assets/37fdd740-f319-4ba0-828c-6567e1ae9f2d" />


## 技术栈

- 后端: FastAPI + SQLite + Playwright
- 前端: Vue 3 + Element Plus + ECharts
- 通知: PushPlus API

## 快速开始

### 使用Docker部署（推荐）

1. 克隆项目
```bash
cd /opt/qinghang
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，修改SECRET_KEY
```

3. 启动服务
```bash
docker-compose up -d --build
```

4. 访问应用
打开浏览器访问 http://localhost

### 手动部署

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

## 配置说明

### PushPlus微信推送

1. 访问 https://www.pushplus.plus/ 注册账号
2. 获取Token
3. 在设置页面填入Token

### 爬虫调试

如果爬虫无法正常工作，可能需要根据实际网站结构调整选择器。
可以修改 `backend/crawler/__init__.py` 中的选择器配置。

## 项目结构

```
/opt/qinghang/
├── backend/                 # 后端服务
│   ├── main.py             # FastAPI入口
│   ├── models.py           # 数据库模型
│   ├── crawler/            # 爬虫模块
│   ├── routers/            # API路由
│   └── services/           # 服务模块
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # 状态管理
│   │   └── api/            # API调用
│   └── ...
├── docker-compose.yml      # Docker编排
└── README.md
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看Swagger API文档。

## 注意事项

1. 生产环境请务必修改SECRET_KEY
2. 建议配置HTTPS
3. 定期备份data目录
