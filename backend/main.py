# backend/main.py

import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 从我们的核心逻辑文件中导入所有需要的函数
from WAIapp_core import (
    generate_full_report_stream,
    agent_action_planner,
    generate_review_summary_report,
    clean_sales_data,
    perform_lstm_forecast,
    perform_product_clustering,
    perform_sentiment_analysis
)

# --- 1. 初始化和配置 FastAPI 应用 ---

app = FastAPI(
    title="WeaveAI Backend API",
    description="为 WeaveAI 前端提供所有AI分析和数据处理能力的API服务。",
    version="1.0.0",
)

# 配置 CORS (跨源资源共享)，允许您的前端(localhost:3000)访问后端
origins = [
    "http://localhost:3000",
    "http://10.174.241.218:3000", # 也允许通过IP地址访问
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"], # 明确加入 OPTIONS
    allow_headers=["*"],
)


# --- 2. 定义数据模型 (用于请求和响应) ---

class UserProfile(BaseModel):
    """用于接收前端发送的用户档案信息"""
    target_market: str
    supply_chain: str
    seller_type: str
    min_price: int
    max_price: int

class ActionPlanRequest(BaseModel):
    """用于接收生成行动计划所需的数据"""
    market_report: str
    validation_summary: str

class ReviewAnalysisRequest(BaseModel):
    """用于接收生成评论分析所需的数据"""
    positive_reviews: str
    negative_reviews: str


# --- 3. 创建 API Endpoints (API接口) ---

@app.get("/", tags=["General"])
def read_root():
    """根路径，用于测试API服务是否正常运行"""
    return {"message": "Welcome to WeaveAI Backend! API is running."}


# --- AI Reports Endpoints ---

@app.post("/api/v1/reports/market-insight", tags=["AI Reports"])
async def api_generate_report(profile: UserProfile):
    """接收用户档案，流式返回主市场分析报告。"""
    try:
        return StreamingResponse(
            generate_full_report_stream(user_profile=profile.dict()),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/reports/action-plan", tags=["AI Reports"])
async def api_action_plan(request: ActionPlanRequest):
    """接收市场报告和验证摘要，流式返回行动计划。"""
    try:
        return StreamingResponse(
            agent_action_planner(
                market_report=request.market_report,
                validation_summary=request.validation_summary
            ),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/reports/review-summary", tags=["AI Reports"])
async def api_review_summary(request: ReviewAnalysisRequest):
    """接收正负评论样本，流式返回评论洞察报告。"""
    try:
        return StreamingResponse(
            generate_review_summary_report(
                positive_reviews_sample=request.positive_reviews,
                negative_reviews_sample=request.negative_reviews
            ),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Data Analysis Endpoints ---

async def process_uploaded_file(file: UploadFile, allowed_extensions: list) -> pd.DataFrame:
    """辅助函数，用于读取和验证上传的文件"""
    filename = file.filename
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail=f"Invalid file type. Please upload one of {allowed_extensions}.")
    
    try:
        contents = await file.read()
        if filename.endswith('.csv'):
            return pd.read_csv(io.BytesIO(contents))
        elif filename.endswith('.parquet'):
            return pd.read_parquet(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading or parsing file: {e}")


@app.post("/api/v1/data/forecast-sales", tags=["Data Analysis"])
async def api_forecast_sales(file: UploadFile = File(...)):
    """接收销售数据文件，返回LSTM预测图表的JSON数据。"""
    try:
        df = await process_uploaded_file(file, ['.csv', '.parquet'])
        cleaned_df = clean_sales_data(df)
        fig = perform_lstm_forecast(cleaned_df)
        return JSONResponse(content=fig.to_json())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.post("/api/v1/data/product-clustering", tags=["Data Analysis"])
async def api_product_clustering(file: UploadFile = File(...)):
    """接收销售数据文件，返回聚类分析结果的JSON数据。"""
    try:
        df = await process_uploaded_file(file, ['.csv', '.parquet'])
        cleaned_df = clean_sales_data(df)
        result = perform_product_clustering(cleaned_df)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.post("/api/v1/data/sentiment-analysis", tags=["Data Analysis"])
async def api_sentiment_analysis(file: UploadFile = File(...)):
    """接收评论数据文件，返回情感分析结果的JSON数据。"""
    try:
        df = await process_uploaded_file(file, ['.csv', '.parquet'])
        result = perform_sentiment_analysis(df)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")