# 📈 WeaveAI 智能分析助手

> 告别感觉，让数据与AI为您引航

WeaveAI 是一个全栈 AI 驱动的 Web 应用，旨在为跨境电商卖家和品牌方提供从市场机会洞察、内部数据验证到生成可执行行动计划的端到端战略支持。

## ✨ 核心功能

本项目通过一个引导式的三步工作流，将复杂的战略分析流程化、自动化：

1.  **🤖 第一步：机会洞察 (Insight)**

      * 用户提交一个“战略档案”，包括目标市场、核心品类、卖家类型和定价区间。
      * AI Agent（基于 Volcengine Ark）会接收此档案，并流式（Streaming）生成一份包含宏观环境、细分品类机会点和竞争格局分析的深度市场报告。
      * 前端使用 `react-markdown` 实时渲染AI的“思考过程”和“正式报告”。

2.  **📊 第二步：自我验证 (Validation)**

      * 用户上传自己的历史销售数据和（可选的）评论数据（支持 `.csv` 和 `.parquet` 格式）。
      * 应用提供一个交互式仪表盘，执行三种核心的数据分析：
          * **销售预测**：使用 Keras/TensorFlow 构建的 **LSTM** 模型预测未来30天的销售额，并使用 `Plotly.js` 进行可视化。
          * **热销品聚类**：使用 **KMeans** 算法对商品进行聚类，识别出“热销商品簇”和“潜力商品簇”。
          * **情感分析**：使用 `vaderSentiment` 分析评论，并允许用户通过滑块筛选特定星级的评论。
      * **嵌套 AI 功能**：用户可以基于筛选后的评论，再次调用 AI 生成一份深入的“用户洞察分析报告”。
      * 完成后，此步骤会生成一份“内部数据验证摘要”。

3.  **🚀 第三步：行动计划 (Action)**

      * 应用将\*\*第一步的“市场洞察报告”**和**第二步的“验证摘要”\*\*作为上下文，提交给专职“行动规划”的 AI Agent。
      * AI Agent 会生成一份高度具体、可落地的季度行动路线图，涵盖产品研发、市场营销和供应链运营。

## 🛠️ 技术栈

本项目采用前后端分离的架构。

### **Frontend** (Next.js)

  * **框架**: Next.js 15.5.6, React 19.1.0 (App Router)
  * **状态管理**: React Hooks (`useState`, `useMemo`, `useEffect`)
  * **UI / 样式**: TailwindCSS, `@tailwindcss/typography` (用于渲染 Markdown)
  * **数据可视化**: `Plotly.js`, `react-plotly.js`
  * **UI 组件**: `rc-slider` (用于价格/星级筛选)
  * **Markdown 渲染**: `react-markdown`, `remark-gfm`

### **Backend** (FastAPI)

  * [cite\_start]**框架**: FastAPI [cite: 1][cite\_start], Uvicorn [cite: 1]
  * [cite\_start]**AI Agent**: `volcengine-python-sdk[ark]` (调用 `doubao-seed` 模型) [cite: 1]
  * [cite\_start]**机器学习 (预测)**: TensorFlow / Keras (LSTM) [cite: 1]
  * [cite\_start]**机器学习 (聚类)**: Scikit-learn (KMeans) [cite: 1]
  * [cite\_start]**机器学习 (情感)**: `vaderSentiment` [cite: 1]
  * [cite\_start]**数据处理**: Pandas [cite: 1][cite\_start], Numpy [cite: 1][cite\_start], Openpyxl [cite: 1][cite\_start], Pyarrow [cite: 1]
  * [cite\_start]**环境变量**: `python-dotenv` [cite: 1]

## 📁 项目结构

```
WeaveAI_迭代/
├── backend/                 
│   ├── .env                  # ◀ 存储 ARK_API_KEY
│   ├── main.py               # ◀ FastAPI 路由定义
│   ├── WAIapp_core.py        # ◀ 核心 AI Agent 和数据分析逻辑
[cite_start]│   └── requirements.txt      # ◀ Python 依赖 [cite: 1]
└── frontend/                
    ├── .env.local            # ◀ 存储 NEXT_PUBLIC_API_BASE_URL
    ├── app/
    │   ├── components/       # ◀ React UI 组件
    │   │   ├── ProfileForm.js       
    │   │   ├── ReportDisplay.js     
    │   │   ├── ValidationDashboard.js 
    │   │   ├── ActionPlanner.js     
    │   │   ├── SentimentAnalysis.js 
    │   │   ├── StepsIndicator.js  
    │   │   └── ...
    │   ├── page.js           # ◀ 核心页面和状态管理"大脑"
    │   ├── layout.js         # ◀ 根布局和字体
    │   └── globals.css       # ◀ Tailwind CSS 基础样式
    ├── package.json          # ◀ Node.js 依赖
    ├── tailwind.config.mjs   # ◀ Tailwind 配置
    └── next.config.mjs       # ◀ Next.js 配置
```

## 🚀 本地开发与运行

您需要分别启动后端服务和前端应用。

### 1\. 启动 Backend (FastAPI)

```bash
# 1. 进入后端目录
cd backend

# 2. (推荐) 创建并激活虚拟环境
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# 3. 安装 Python 依赖
[cite_start]pip install -r requirements.txt [cite: 1]

# 4. 创建环境变量文件
# 在 backend 目录下新建一个 .env 文件
# 并添加您的 Volcengine Ark API 密钥
echo "ARK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx" > .env

# 5. 启动 FastAPI 服务
# (服务将运行在 http://127.0.0.1:8000)
uvicorn main:app --reload
```

### 2\. 启动 Frontend (Next.js)

```bash
# 1. (在新的终端中) 进入前端目录
cd frontend

# 2. 安装 Node.js 依赖
npm install

# 3. 创建环境变量文件
# 在 frontend 目录下新建一个 .env.local 文件
# 指向您本地的 FastAPI 服务地址
echo "NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000" > .env.local

# 4. 启动 Next.js 开发服务器
npm run dev

# 5. 在浏览器中打开 http://localhost:3000
```

## 🔑 环境变量

### `backend/.env`

  * `ARK_API_KEY`: **[必需]** 您的 Volcengine Ark API 密钥，用于驱动所有 AI Agent 功能。

### `frontend/.env.local`

  * `NEXT_PUBLIC_API_BASE_URL`: **[必需]** 您的后端 FastAPI 服务地址。默认为 `http://127.0.0.1:8000`。

## 📡 API Endpoints

所有 API 均由 `backend/main.py` 提供。

### AI 报告 (流式响应)

  * `POST /api/v1/reports/market-insight`
      * **Body**: `UserProfile` JSON 对象 (市场, 品类, 价格等)。
      * **Response**: `StreamingResponse` (text/plain) - 流式返回市场洞察 Markdown 报告。
  * `POST /api/v1/reports/action-plan`
      * **Body**: `ActionPlanRequest` JSON 对象 (包含 `market_report` 和 `validation_summary`)。
      * **Response**: `StreamingResponse` (text/plain) - 流式返回行动计划 Markdown 报告。
  * `POST /api/v1/reports/review-summary`
      * **Body**: `ReviewAnalysisRequest` JSON 对象 (包含正/负评论样本)。
      * **Response**: `StreamingResponse` (text/plain) - 流式返回评论洞察 Markdown 报告。

### 数据分析 (JSON 响应)

  * `POST /api/v1/data/forecast-sales`
      * **Body**: `UploadFile` (销售数据 .csv/.parquet)。
      * **Response**: `JSONResponse` - 包含 Plotly 图表 JSON 数据的 LSTM 预测结果。
  * `POST /api/v1/data/product-clustering`
      * **Body**: `UploadFile` (销售数据 .csv/.parquet)。
      * **Response**: `JSONResponse` - 包含聚类摘要和热销品列表的 KMeans 分析结果。
  * `POST /api/v1/data/sentiment-analysis`
      * **Body**: `UploadFile` (评论数据 .csv/.parquet)。
      * **Response**: `JSONResponse` - 包含情感分析结果（平均分、评论列表）。