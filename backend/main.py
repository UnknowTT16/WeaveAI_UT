# backend/main.py

import io
import pandas as pd
import uuid
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# >>> 新增/调整：为 PDF 导出做准备
import asyncio
from pyppeteer import launch
import shutil
import platform
# <<<

from WAIapp_core import (
    generate_full_report_stream,
    agent_action_planner,
    generate_review_summary_report,
    clean_sales_data,
    perform_lstm_forecast,
    perform_product_clustering,
    perform_sentiment_analysis,
    generate_final_html_report,
    perform_basket_analysis
)

app = FastAPI(
    title="WeaveAI Backend API",
    description="为 WeaveAI 前端提供所有AI分析和数据处理能力的API服务。",
    version="1.0.0",
)

REPORTS_DIR = Path("static/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://172.20.10.6:3000",
    "http://8.134.84.154:3000",
    "http://8.134.100.38:3000",
    "http://192.168.43.4:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserProfile(BaseModel):
    target_market: str
    supply_chain: str
    seller_type: str
    min_price: int
    max_price: int
    use_websearch: bool = False

class ActionPlanRequest(BaseModel):
    market_report: str
    validation_summary: str

class ReviewAnalysisRequest(BaseModel):
    positive_reviews: str
    negative_reviews: str

class FinalReportRequest(BaseModel):
    market_report: str
    validation_summary: str
    action_plan: str
    sentiment_report: Optional[str] = None
    forecast_chart_json: Optional[str] = None
    clustering_data: Optional[dict] = None
    elbow_chart_json: Optional[str] = None
    scatter_3d_chart_json: Optional[str] = None
    basket_analysis_data: Optional[list] = None

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Welcome to WeaveAI Backend! API is running."}

# --- AI Reports ---
@app.post("/api/v1/reports/market-insight", tags=["AI Reports"])
async def api_generate_report(profile: UserProfile):
    try:
        return StreamingResponse(
            generate_full_report_stream(user_profile=profile.dict()),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/reports/action-plan", tags=["AI Reports"])
async def api_action_plan(request: ActionPlanRequest):
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

@app.post("/api/v1/reports/generate-and-save-report", tags=["AI Reports"])
async def api_generate_and_save_report(payload: FinalReportRequest, request: Request):
    try:
        html_content = generate_final_html_report(
            market_report=payload.market_report,
            validation_summary=payload.validation_summary,
            action_plan=payload.action_plan,
            sentiment_report=payload.sentiment_report,
            forecast_chart_json=payload.forecast_chart_json,
            clustering_data=payload.clustering_data,
            elbow_chart_json=payload.elbow_chart_json,
            scatter_3d_chart_json=payload.scatter_3d_chart_json,
            basket_analysis_data=payload.basket_analysis_data
        )
        report_filename = f"report_{uuid.uuid4()}.html"
        report_path = REPORTS_DIR / report_filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        report_url = f"{request.base_url}reports/{report_filename}"
        return {"report_url": report_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")

# --- Data Analysis ---
async def process_uploaded_file(file: UploadFile, allowed_extensions: list) -> pd.DataFrame:
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
    try:
        df = await process_uploaded_file(file, ['.csv', '.parquet'])
        from WAIapp_core import clean_sales_data, perform_lstm_forecast
        cleaned_df = clean_sales_data(df)
        fig = perform_lstm_forecast(cleaned_df)
        return JSONResponse(content=fig.to_json())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/api/v1/data/product-clustering", tags=["Data Analysis"])
async def api_product_clustering(file: UploadFile = File(...)):
    try:
        df = await process_uploaded_file(file, ['.csv', '.parquet'])
        from WAIapp_core import clean_sales_data, perform_product_clustering, perform_basket_analysis
        cleaned_df = clean_sales_data(df)
        clustering_result = perform_product_clustering(cleaned_df)
        basket_analysis_result = perform_basket_analysis(cleaned_df)
        return JSONResponse(content={
            "clustering_results": clustering_result,
            "basket_analysis_results": basket_analysis_result
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/api/v1/data/sentiment-analysis", tags=["Data Analysis"])
async def api_sentiment_analysis(file: UploadFile = File(...)):
    try:
        df = await process_uploaded_file(file, ['.csv', '.parquet'])
        from WAIapp_core import perform_sentiment_analysis
        result = perform_sentiment_analysis(df)
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# =========================
# 导出 PDF （改为优先使用本机浏览器）
# =========================

class ExportPdfRequest(BaseModel):
    report_url: str

def _guess_local_chrome_path() -> Optional[str]:
    """
    优先读取 CHROME_PATH，其次在常见安装目录中查找 Chrome / Edge。
    兼容 Windows / macOS / Linux。
    """
    # 环境变量优先
    env_path = os.environ.get("CHROME_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    system = platform.system().lower()

    candidates = []
    if system == "windows":
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
    elif system == "darwin":  # macOS
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    else:  # linux
        for bin_name in ["google-chrome", "chrome", "chromium", "chromium-browser", "microsoft-edge", "msedge"]:
            path = shutil.which(bin_name)
            if path:
                candidates.append(path)

        # 常见发行版路径
        candidates += [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/microsoft-edge",
        ]

    for p in candidates:
        if Path(p).exists():
            return p
    return None

async def _export_url_to_pdf(report_url: str, output_path: Path):
    """
    使用本机 Chrome/Edge（若找到）导出 PDF；否则回退到 pyppeteer 默认 Chromium。
    """
    exec_path = _guess_local_chrome_path()

    launch_kwargs = {
        "headless": True,
        "args": [
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
        ],
    }
    if exec_path:
        launch_kwargs["executablePath"] = exec_path

    try:
        browser = await launch(**launch_kwargs)
    except Exception as e:
        # 如果用本地浏览器失败，最后再尝试无 executablePath（可能触发下载）
        if launch_kwargs.get("executablePath"):
            del launch_kwargs["executablePath"]
            browser = await launch(**launch_kwargs)
        else:
            raise

    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(report_url)
    effective_url = report_url
    if parsed.hostname and parsed.hostname not in {"127.0.0.1", "localhost", "backend"}:
        internal_port = f":{parsed.port}" if parsed.port else ""
        effective_url = urlunparse(parsed._replace(netloc=f"127.0.0.1{internal_port}"))

    page = await browser.newPage()
    await page.goto(effective_url, {"waitUntil": "networkidle2", "timeout": 60000})
    await page.pdf({
        "path": str(output_path),
        "format": "A4",
        "printBackground": True,
        # "margin": {"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"},
    })
    await browser.close()

@app.post("/api/v1/reports/export-pdf", tags=["AI Reports"])
async def api_export_pdf(payload: ExportPdfRequest, request: Request):
    try:
        base_name = Path(payload.report_url).stem or f"report_{uuid.uuid4()}"
        pdf_filename = f"{base_name}.pdf"
        pdf_path = REPORTS_DIR / pdf_filename

        await _export_url_to_pdf(payload.report_url, pdf_path)

        pdf_url = f"{request.base_url}reports/{pdf_filename}"
        return {"pdf_url": pdf_url}
    except Exception as e:
        # 给出更友好的提示，告诉用户如何指定本机浏览器路径
        hint = ("请在系统环境变量中设置 CHROME_PATH 指向本机 Chrome/Edge 可执行文件，"
                "例如：C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        raise HTTPException(status_code=500, detail=f"导出 PDF 失败: {e}. {hint}")
