# backend/WAIapp_core.py

import os
import pandas as pd
import numpy as np
import warnings
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark
import markdown2
import json
from pandarallel import pandarallel

# 分析库
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pandas.errors import SettingWithCopyWarning, DtypeWarning
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth

# 可视化库
import plotly.graph_objects as go
import plotly.express as px

# 加载环境变量
load_dotenv()

# (关键) 解决 KMeans 内存泄漏警告
os.environ['OMP_NUM_THREADS'] = '1'

# 初始化 pandarallel，禁用进度条以保持日志清洁
pandarallel.initialize(progress_bar=False) 

# 抑制特定的Pandas警告
warnings.filterwarnings('ignore', category=SettingWithCopyWarning)
warnings.filterwarnings('ignore', category=DtypeWarning)

# ==============================================================================
# AI Agent 模块
# ==============================================================================

def get_ark_client():
    """获取并返回一个配置好的 Ark 客户端实例"""
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise ValueError("ARK_API_KEY not found in environment variables.")
    return Ark(api_key=api_key)

def generate_full_report_stream(user_profile: dict):
    """【核心】生成主市场分析报告的流式函数"""
    ark_client = get_ark_client()
    market = user_profile['target_market']
    categories = user_profile['supply_chain']
    seller = user_profile['seller_type']
    price_range = f"${user_profile['min_price']} - ${user_profile['max_price']}"

    system_prompt = f"""
    你是 "WeaveAI" 应用内的一位高级战略顾问，你的报告是为一位计划进入'{market}'市场的'{seller}'，他/她专注于'{categories}'品类，目标售价在'{price_range}'。
    你的报告必须专业、详尽、数据驱动，并使用精美的Markdown格式。

    **第一阶段：输出思考过程**
    在正式开始报告前，你必须先输出你的思考过程。这部分内容必须以 "我需要..." 或 "首先..." 开始，概述你将如何为用户分析。不要使用任何Markdown标题。
    
    **重要指令 1：** 在思考过程结束后，你必须另起一行，并只输出 `<<<<THINKING_ENDS>>>>` 这个特殊标记。
    
    **重要指令 2：** 在上一个标记之后，你必须立即另起一行并输出 `<<<<REPORT_STARTS>>>>`，然后才能开始生成严格按照以下Markdown格式的正式报告，中间不能有任何其他文字。

    **第二阶段：输出正式报告**
    ---
    
    ## 报告摘要 (Executive Summary)
    *   在此处用2-3个要点，**加粗**核心关键词，高度概括整个报告的核心发现和最终建议。
    
    ---
    
    ## 🎯 市场机遇洞察 (Market Opportunities)
    
    ### 一、 宏观环境分析
    1.  **市场潜力与趋势**: 结合**量化数据**解释增长空间 (必须注明来源和年份)。
    2.  **文化与消费习惯**: 【核心】深入分析当地文化、节假日、生活方式如何影响'{categories}'品类的消费偏好。
    3.  **法律法规与关税**: 【核心】明确指出进口限制、所需**具体认证** (如CE, RoHS) 和大致的关税税率。
    
    ### 二、 高潜力细分品类机会点
    *   你必须利用网络搜索，识别出3个最符合用户画像的细分机会。
    *   对于每一个机会点，必须严格按照以下模板进行分析：
    
    #### 机会点 1: [在此处填写具体品类名称]
    *   **产品定义:** 清晰描述这个品类的核心功能、形态和目标用户。
    *   **需求驱动与市场规模:** 解释为什么当地市场需要这个产品。**必须包含量化数据，并注明来源和年份** (例如: 市场规模预计在2025年达到 **€5000万**，年增长率 **15%** [来源: Statista, 2023])。
    *   **SWOT 分析:**
        *   **优势 (Strength):** 
        *   **劣势 (Weakness):** 
        *   **机会 (Opportunity):** 
        *   **威胁 (Threat):** 

    ---
    
    ## ⚔️ 核心竞争格局 (Competitive Landscape)
    
    ### 竞争分析: [机会点1的品类名称]
    *   **竞争格局概述:** 简要说明该品类是蓝海还是红海，主要由哪些类型的品牌主导。
    *   **主要竞争对手分析:** 你的表格必须严格遵守Markdown语法，**并且表格本身必须另起新的一行开始**，其前后不能有任何文字。请参考以下完美范例：
    
*主要竞争对手分析表*
| 代表性竞品品牌 | 主流定价 | 核心卖点 | 主要用户痛点 |
| :--- | :--- | :--- | :--- |
| Anker | €45-€60 | GaN技术, 多口快充 | 部分型号体积较大 |
| Belkin | €50-€75 | 苹果官方认证, 设计简约 | 性价比不高 |

    *   **竞争策略建议:** 基于以上分析，提出1-3条针对性的、可操作的竞争策略建议。

    ### 竞争分析: [机会点2的品类名称]
    *   **竞争格局概述:** 简要说明该品类是蓝海还是红海，主要由哪些类型的品牌主导。
    *   **主要竞争对手分析:** 你的表格必须严格遵守Markdown语法，**并且表格本身必须另起新的一行开始**，其前后不能有任何文字。请参考以下完美范例：
    
*主要竞争对手分析表*
| 代表性竞品品牌 | 主流定价 | 核心卖点 | 主要用户痛点 |
| :--- | :--- | :--- | :--- |
| Anker | €45-€60 | GaN技术, 多口快充 | 部分型号体积较大 |
| Belkin | €50-€75 | 苹果官方认证, 设计简约 | 性价比不高 |

    *   **竞争策略建议:** 基于以上分析，提出1-3条针对性的、可操作的竞争策略建议。

    ### 竞争分析: [机会点3的品类名称]
    *   **竞争格局概述:** 简要说明该品类是蓝海还是红海，主要由哪些类型的品牌主导。
    *   **主要竞争对手分析:** 你的表格必须严格遵守Markdown语法，**并且表格本身必须另起新的一行开始**，其前后不能有任何文字。请参考以下完美范例：
    
*主要竞争对手分析表*
| 代表性竞品品牌 | 主流定价 | 核心卖点 | 主要用户痛点 |
| :--- | :--- | :--- | :--- |
| Anker | €45-€60 | GaN技术, 多口快充 | 部分型号体积较大 |
| Belkin | €50-€75 | 苹果官方认证, 设计简约 | 性价比不高 |

    *   **竞争策略建议:** 基于以上分析，提出1-3条针对性的、可操作的竞争策略建议。
    """
    user_input = f"请基于我的画像，为我生成一份关于'{market}'市场的机会识别与竞争分析报告，重点关注'{categories}'品类。"

    use_websearch = user_profile.get("use_websearch", False)
    request_params = {
        "model": "doubao-seed-1-6-250615",
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}]
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_input}]
            }
        ],
        "stream": True
    }
    if use_websearch:
        request_params["tools"] = [{"type": "web_search", "limit": 15}]
    
    try:
        response = ark_client.responses.create(**request_params)
        for chunk in response:
            delta_content = getattr(chunk, 'delta', None)
            if isinstance(delta_content, str):
                yield delta_content
    except Exception as e:
        yield f"❌ AI Agent请求失败: {e}"


def agent_action_planner(market_report: str, validation_summary: str):
    """生成行动计划的流式函数"""
    ark_client = get_ark_client()
    system_prompt = f"""
    你是 "WeaveAI" 应用内的一位顶级的 **首席运营官(COO)兼首席营销官(CMO)**，极其擅长将战略分析转化为一份**高度具体、可落地执行的季度行动路线图**。你的报告必须专业、结构化，并使用精美的Markdown格式。

    **第一阶段：输出思考过程**
    在正式开始报告前，你必须先输出你的思考过程。这部分内容必须以 "我需要..." 或 "首先..." 开始，概述你将如何整合市场报告和内部数据，并制定行动计划。不要使用任何Markdown标题。
    
    **重要指令 1：** 在思考过程结束后，你必须另起一行，并只输出 `<<<<THINKING_ENDS>>>>` 这个特殊标记。
    
    **重要指令 2：** 在上一个标记之后，你必须立即另起一行并输出 `<<<<REPORT_STARTS>>>>`，然后才能开始生成严格按照以下Markdown格式的正式报告，中间不能有任何其他文字。

    **第二阶段：输出正式报告**
    ---

    ## 📋 您的专属季度行动计划

    基于市场机会洞察与内部数据验证，我们为您制定了以下行动路线图：

    ### 🚀 产品与研发 (Product & R&D)
    
    *   **核心目标:** [此处基于市场报告的机会点，凝练出1-2个最关键的产品目标。例如：针对XX市场的XX痛点，开发一款具有差异化优势的新品。]
    
    *   **关键行动项 (Key Actions):**
        1.  **[行动项1 - 例如：新品定义与设计]:** [详细描述，必须具体。例如：完成对标竞品A和B功能差异分析，输出包含**智能温控**和**便携设计**两个核心卖点的产品需求文档(PRD)。 **负责人：产品经理**]
        2.  **[行动项2 - 例如：原型开发与测试]:** [详细描述。例如：与供应商合作，在**30天**内完成首版手板原型制作，并招募**20名**目标用户进行内测，收集反馈。 **负责人：项目经理**]
        3.  **[行动项3 - 例如：产品迭代与优化]:** [详细描述。例如：根据内测反馈，在**2周**内完成产品迭代，并确保在**3个月**内完成至少**3轮**优化。 **负责人：研发团队**] 

    *   **预期关键结果 (KPIs):**
        *   [例如：季度末完成最终产品定版。]
        *   [例如：内测用户满意度评分达到 **4.5/5**。]

    ---

    ### 📢 市场与营销 (Marketing & Sales)
    
    *   **核心目标:** [此处基于市场报告的竞争格局，设定一个具体的营销目标。例如：新品上市首月，在XX渠道达成XX销量，建立初步的品牌认知。]
    
    *   **关键行动项 (Key Actions):**
        1.  **[行动项1 - 例如：内容营销预热]:** [详细描述。例如：与**3位**德国本地的科技类KOL合作，发布产品预热视频，重点突出**环保材质**和**长续航**卖点。 **负责人：市场部**]
        2.  **[行动项2 - 例如：渠道建设]:** [详细描述。例如：完成Amazon DE站点的Listing优化，**埋入关键词A, B, C**，并准备启动**CPC广告**，初步预算为 **€2000/月**。 **负责人：运营部**]
        3.  **[行动项3 - 例如：促销活动策划]:** [详细描述。例如：策划新品首发促销活动，包括**限时折扣**和**买赠活动**，并通过邮件营销触达现有客户群。 **负责人：销售部**]

    *   **预期关键结果 (KPIs):**
        *   [例如：首月实现 **500+** 订单。]
        *   [例如：KOL合作视频总曝光量达到 **100万**。]
        *   [例如：邮件营销点击率（CTR）达到 **10%**。]

    ---

    ### 🏭 供应链与运营 (Supply Chain & Operations)
    
    *   **核心目标:** [此处设定一个清晰的供应链目标。例如：确保新品的稳定量产，并将单件综合成本控制在$XX以内。]
    
    *   **关键行动项 (Key Actions):**
        1.  **[行动项1 - 例如：供应商审核与认证]:** [详细描述。例如：审核**3家**备选供应商的生产资质，确保其拥有**BSCI认证**。同时，将产品送检以获取进入德国市场必需的**CE和RoHS认证**。 **负责人：供应链**]
        2.  **[行动项2 - 例如：物流与仓储]:** [详细描述。例如：选择一家提供**德国海外仓**服务的头程物流商，制定首批**1000件**产品的发货计划，确保在上市前**2周**完成入仓。 **负责人：物流部**]
        3.  **[行动项3 - 例如：生产计划]:** [详细描述。例如：与工厂签订**首批1000件**产品的生产合同，并制定详细的**生产进度表**，确保按期交付。 **负责人：生产部**]

    *   **预期关键结果 (KPIs):**
        *   [例如：最终产品采购成本（含物流）不高于 **$XX.XX**。]
        *   [例如：季度内完成所有必要的合规认证。]
        *   [例如：首批1000件产品按时交付，无质量问题。]
    """
    user_input = f"以下是我的决策依据：\n--- [市场机会报告] ---\n{market_report}\n--- [内部数据验证摘要] ---\n{validation_summary}\n---\n请基于以上信息，为我生成一份具体的行动计划。"
    try:
        request_params = {"model": "doubao-seed-1-6-250615", "input": [{"role": "system", "content": [{"type": "input_text", "text": system_prompt}]}, {"role": "user", "content": [{"type": "input_text", "text": user_input}]}], "stream": True}
        response = ark_client.responses.create(**request_params)
        for chunk in response:
            delta_content = getattr(chunk, 'delta', None)
            if isinstance(delta_content, str):
                yield delta_content
    except Exception as e:
        yield f"❌ 行动规划师Agent请求失败: {e}"


def generate_review_summary_report(positive_reviews_sample: str, negative_reviews_sample: str):
    """分析评论的流式函数"""
    ark_client = get_ark_client()
    system_prompt = f"""
    你是 "WeaveAI" 应用内的一位高级用户洞察分析师，专注于从用户评论中提炼出深刻的商业洞见。你的报告必须专业、结构清晰、富有洞察力，并使用精美的Markdown格式，大量使用Emoji来增强可读性。

    **第一阶段：输出思考过程**
    在正式开始报告前，你必须先输出你的思考过程。这部分内容必须以 "我需要..." 或 "首先..." 开始，概述你将如何分析这些评论。不要使用任何Markdown标题。
    
    **重要指令 1：** 在思考过程结束后，你必须另起一行，并只输出 `<<<<THINKING_ENDS>>>>` 这个特殊标记。
    
    **重要指令 2：** 在上一个标记之后，你必须立即另起一行并输出 `<<<<REPORT_STARTS>>>>`，然后才能开始生成严格按照以下Markdown格式的正式报告，中间不能有任何其他文字。

    **第二阶段：输出正式报告**
    ---

    ### 📝 评论总体情绪概述
    *   基于你看到的所有评论，用一两句话，**精炼地总结**产品的整体市场反响和用户情绪的核心。

    ---

    ### 👍 产品核心优势 (用户喜爱点)
    
    *   **任务**: 从正面评论中，提炼出用户最常称赞的**2-3个核心优点**。
    *   **格式要求**:
        1.  每个优点前使用一个合适的Emoji。
        2.  用**加粗**的短语概括优点。
        3.  在优点下方，必须使用 **blockquote (`>`) 格式**，并**加粗**引用一句最能代表该观点的**原始评论**。

    *   **完美范例**:
        *   🎨 **设计与美学**: 产品的外观设计和颜色搭配得到了用户的高度赞扬。
            > **"The color is much lighter but I don't mind, it's beautiful!"**
        *   💪 **材质与耐用性**: 用户普遍认为产品的材质坚固、做工精良。
            > **"The leather is sturdy, but not overly rough or stiff. Not one stitch was crooked."**

    ---

    ### 👎 产品主要痛点 (用户抱怨点)

    *   **任务**: 从负面评论中，提炼出用户抱怨最多的**2-3个核心问题或缺点**。
    *   **格式要求**: (同上)

    *   **完美范例**:
        *   📏 **尺寸与描述不符**: 很多用户反映，产品的实际尺寸比预期的要小。
            > **"it is too small to carry a laptop (regular sized)."**
        *   🧵 **质量稳定性不足**: 部分用户遇到了使用早期就出现损坏的问题。
            > **"after two nights the cording on the sleeve came out leaving the casing that enclosed the cord completely frayed."**

    ---
    
    ### 💡 可执行的改进建议 (Actionable Insights)

    *   **任务**: 基于以上所有分析，为产品经理或运营团队提供**2-3条具体的、可落地的改进建议**。
    *   **要求**: 每条建议都必须清晰地说明 **“问题是什么”、“为什么重要”** 以及 **“我们应该怎么做”**。

    *   **完美范例**:
        1.  **优化尺寸描述，增加对比图**: 针对“尺寸与描述不符”的普遍痛点，建议在产品详情页**增加生活场景对比图**（例如，将产品与MacBook Pro 14寸并排摆放的照片），并明确标注可容纳的笔记本电脑型号。这将有效管理用户预期，降低因此产生的差评和退货率。
        2.  **加强出厂质检流程**: 针对“质量稳定性不足”的问题，建议对特定批次的产品（特别是缝合处）**增加一道出厂前的拉力测试**。虽然这会略微增加成本，但对于提升品牌口碑、降低长期售后成本至关重要。
    """
    user_input = f"以下是关于某款产品的用户评论样本。\n--- [正面评论样本] ---\n{positive_reviews_sample}\n--- [正面评论样本结束] ---\n--- [负面评论样本] ---\n{negative_reviews_sample}\n--- [负面评论样本结束] ---\n请根据以上评论，为我生成一份用户洞察分析报告。"
    try:
        request_params = {"model": "doubao-seed-1-6-250615", "input": [{"role": "system", "content": [{"type": "input_text", "text": system_prompt}]}, {"role": "user", "content": [{"type": "input_text", "text": user_input}]}], "stream": True}
        response = ark_client.responses.create(**request_params)
        for chunk in response:
            delta_content = getattr(chunk, 'delta', None)
            if isinstance(delta_content, str):
                yield delta_content
    except Exception as e:
        yield f"❌ AI评论分析请求失败: {e}"


# ==============================================================================
# 数据处理与分析模块 (优化版)
# ==============================================================================

def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """封装的数据清洗逻辑"""
    for old, new in {'Total Sales':'Amount','Product':'SKU','Quantity':'Qty','Order_ID':'Order ID'}.items():
        if old in df.columns: df.rename(columns={old:new}, inplace=True)
    
    req_cols = ["Amount","Category","Date","Status","SKU","Order ID","Qty"]
    if missing := [c for c in req_cols if c not in df.columns]:
        raise ValueError(f"文件中缺少关键列: {', '.join(missing)}")

    df.dropna(subset=["Amount", "Category", "Date"], inplace=True)
    try:
        df["Date"] = pd.to_datetime(df["Date"], format='%m-%d-%y')
    except ValueError:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    
    df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce')
    df = df[df["Status"].isin(["Shipped","Shipped - Delivered to Buyer","Completed","Pending","Cancelled"])]
    df.dropna(subset=['Date','Amount','SKU','Order ID','Qty'], inplace=True)
    return df

def perform_lstm_forecast(df: pd.DataFrame) -> go.Figure:
    """LSTM 预测函数，返回 Plotly Figure 对象"""
    sales_ts = df.groupby('Date')['Amount'].sum().asfreq('D', fill_value=0)
    sales_values = sales_ts.values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_values = scaler.fit_transform(sales_values)
    
    def create_dataset(data, look_back=7):
        X, y = [], []
        for i in range(len(data) - look_back):
            X.append(data[i:(i + look_back), 0])
            y.append(data[i + look_back, 0])
        return np.array(X), np.array(y)

    look_back = 7
    X, y = create_dataset(scaled_values, look_back)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    model = Sequential([Input(shape=(look_back, 1)), LSTM(50), Dense(1)])
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X, y, epochs=20, batch_size=32, verbose=0)

    last_days_scaled = scaled_values[-look_back:]
    current_input = np.reshape(last_days_scaled, (1, look_back, 1))
    future_predictions_scaled = []
    for _ in range(30):
        next_pred_scaled = model.predict(current_input, verbose=0)
        future_predictions_scaled.append(next_pred_scaled[0, 0])
        new_pred_reshaped = np.reshape(next_pred_scaled, (1, 1, 1))
        current_input = np.append(current_input[:, 1:, :], new_pred_reshaped, axis=1)

    future_predictions = scaler.inverse_transform(np.array(future_predictions_scaled).reshape(-1, 1))
    last_date = sales_ts.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sales_ts.index, y=sales_ts.values, name='历史销售额', line=dict(color='royalblue', width=2), fill='tozeroy', fillcolor='rgba(65, 105, 225, 0.2)'))
    fig.add_trace(go.Scatter(x=future_dates, y=future_predictions.flatten(), name='LSTM 预测销售额', line=dict(color='darkorange', dash='dash', width=2), fill='tozeroy', fillcolor='rgba(255, 140, 0, 0.2)'))
    fig.update_layout(title='未来30天销售额深度学习预测 (LSTM模型)', xaxis_title='日期', yaxis_title='销售额', template='plotly_white')
    return fig

def calculate_wcss_for_elbow(scaled_data, max_k=6):
    """
    为手肘法计算不同K值下的WCSS (簇内平方差)。
    默认仅计算到 K=6，并在数据量过大时自动抽样，以避免内存占用过高。
    """
    sample = scaled_data
    if sample.shape[0] > 2000:
        rng = np.random.default_rng(42)
        idx = rng.choice(sample.shape[0], 2000, replace=False)
        sample = sample[idx]

    max_k = max(1, min(max_k, sample.shape[0]))

    wcss = []
    for k in range(1, max_k + 1):
        kmeans = MiniBatchKMeans(
            n_clusters=k,
            batch_size=512,
            n_init=10,
            random_state=42
        )
        kmeans.fit(sample)
        wcss.append(kmeans.inertia_)

    return [{"k": i + 1, "wcss": val} for i, val in enumerate(wcss)]


def perform_basket_analysis(df: pd.DataFrame):
    """
    执行购物篮分析（默认采用 FP-Growth），并在数据规模过大时自动裁剪。
    """
    basket_df = df[['Order ID', 'SKU', 'Qty']].copy()
    basket_df = basket_df[basket_df['Qty'] > 0]

    if basket_df.empty:
        return []

    order_count = basket_df['Order ID'].nunique()
    if order_count > 5000:
        sampled_orders = basket_df['Order ID'].drop_duplicates().sample(5000, random_state=42)
        basket_df = basket_df[basket_df['Order ID'].isin(sampled_orders)]

    sku_totals = basket_df.groupby('SKU')['Qty'].sum()
    keep_skus = sku_totals[sku_totals >= 5].index
    basket_df = basket_df[basket_df['SKU'].isin(keep_skus)]

    if basket_df.empty:
        return []

    basket = (basket_df.groupby(['Order ID', 'SKU'])['Qty']
              .sum().unstack().reset_index().fillna(0)
              .set_index('Order ID'))

    basket_sets = basket.gt(0)

    frequent_itemsets = fpgrowth(
        basket_sets,
        min_support=0.02,
        use_colnames=True
    )
    if frequent_itemsets.empty:
        return []

    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.05)

    if rules.empty:
        return []

    rules["antecedents"] = rules["antecedents"].apply(lambda x: ', '.join(list(x)))
    rules["consequents"] = rules["consequents"].apply(lambda x: ', '.join(list(x)))

    result = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
    result = result.sort_values(by='lift', ascending=False).head(20)

    result['support'] = result['support'].map('{:.2%}'.format)
    result['confidence'] = result['confidence'].map('{:.2%}'.format)
    result['lift'] = result['lift'].map('{:.2f}'.format)

    return result.to_dict(orient='records')


def perform_product_clustering(df: pd.DataFrame) -> dict:
    """
    【最终修正版】产品聚类函数，修正了图表JSON生成的bug，并加入数据裁剪以降低内存占用。
    """
    required_cols = ['SKU', 'Amount', 'Qty', 'Order ID']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("聚类分析失败：缺少必要的列")

    product_agg_df = df.groupby('SKU').agg(
        total_amount=('Amount', 'sum'),
        total_qty=('Qty', 'sum'),
        order_count=('Order ID', 'nunique')
    ).reset_index()

    if product_agg_df.empty:
        return {
            "cluster_summary": [],
            "product_points": [],
            "elbow_data": [],
            "elbow_chart_json": go.Figure().to_json(),
            "scatter_3d_chart_json": go.Figure().to_json()
        }

    product_agg_df.sort_values('total_amount', ascending=False, inplace=True)

    top_k = min(len(product_agg_df), 5000)
    df_for_clustering = product_agg_df.head(top_k).copy()

    features_for_fit = df_for_clustering[['total_amount', 'total_qty', 'order_count']].astype(np.float32)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_for_fit)

    if features_scaled.shape[0] < 2:
        elbow_data = []
        product_agg_df['cluster'] = 0
    else:
        elbow_data = calculate_wcss_for_elbow(features_scaled)
        n_clusters = min(3, features_scaled.shape[0])
        kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            batch_size=512,
            n_init=10,
            random_state=42
        )
        kmeans.fit(features_scaled)

        all_features = product_agg_df[['total_amount', 'total_qty', 'order_count']].astype(np.float32)
        all_features_scaled = scaler.transform(all_features)
        product_agg_df['cluster'] = kmeans.predict(all_features_scaled)

    cluster_summary_df = product_agg_df.groupby('cluster')[['total_amount', 'total_qty', 'order_count']].mean().sort_values(by='total_amount', ascending=False).reset_index()

    if not cluster_summary_df.empty:
        hot_cluster_id = cluster_summary_df.iloc[0]['cluster']
        cluster_summary_df['is_hot_cluster'] = cluster_summary_df['cluster'] == hot_cluster_id
    else:
        cluster_summary_df['is_hot_cluster'] = False

    # --- 生成图表对象 ---
    fig_elbow = go.Figure()
    if elbow_data:
        fig_elbow.add_trace(go.Scatter(
            x=[d['k'] for d in elbow_data],
            y=[d['wcss'] for d in elbow_data],
            mode='lines+markers'
        ))
    fig_elbow.update_layout(
        title='手肘法确定最佳聚类数',
        xaxis_title='聚类数量 K',
        yaxis_title='簇内平方差 (WCSS)',
        template='plotly_dark'
    )

    fig_3d = go.Figure()
    fig_3d.add_trace(go.Scatter3d(
        x=product_agg_df['total_amount'],
        y=product_agg_df['total_qty'],
        z=product_agg_df['order_count'],
        text=product_agg_df['SKU'],
        hoverinfo='x+y+z+text',
        mode='markers',
        marker=dict(
            size=5,
            color=product_agg_df['cluster'],
            colorscale='Viridis',
            opacity=0.8
        )
    ))
    fig_3d.update_layout(
        title='3D聚类结果可视化',
        template='plotly_dark',
        scene=dict(
            xaxis_title='总销售额',
            yaxis_title='总销量',
            zaxis_title='订单数'
        )
    )

    return {
        "cluster_summary": cluster_summary_df.to_dict(orient='records'),
        "product_points": product_agg_df.to_dict(orient='records'),
        "elbow_data": elbow_data,
        "elbow_chart_json": fig_elbow.to_json(),
        "scatter_3d_chart_json": fig_3d.to_json()
    }


def perform_sentiment_analysis(df: pd.DataFrame) -> dict:
    """
    【优化版】情感分析函数，使用并行处理
    """
    def find_review_column(df_to_check: pd.DataFrame) -> str | None:
        priority_cols = ['reviews.text', 'review_text', 'content', 'comment', 'review']
        for p_col in priority_cols:
            if p_col in df_to_check.columns and df_to_check[p_col].dropna().astype(str).str.strip().any():
                return p_col
        
        possible_cols = [col for col in df_to_check.columns if any(key in str(col).lower() for key in ['text', 'review', 'content', 'comment'])]
        if possible_cols:
            string_cols = [col for col in possible_cols if df_to_check[col].dtype == 'object']
            if string_cols:
                return max(string_cols, key=lambda col: df_to_check[col].dropna().astype(str).str.len().mean())
        
        object_cols = df_to_check.select_dtypes(include=['object']).columns
        if not object_cols.empty:
            for col in object_cols:
                if df_to_check[col].dropna().astype(str).str.strip().any():
                    return col
        return None

    review_column_name = find_review_column(df)
    if review_column_name is None:
        raise ValueError("错误: 未能在评论文件中找到有效的文本列。")
        
    df[review_column_name] = df[review_column_name].astype(str).dropna()
    df = df[df[review_column_name].str.strip() != 'None'].copy()
    
    analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df[review_column_name].parallel_apply(lambda text: analyzer.polarity_scores(text)['compound'])
    
    def sentiment_to_rating(sentiment):
        if sentiment >= 0.5: return 5
        elif sentiment >= 0.05: return 4
        elif sentiment > -0.05: return 3
        elif sentiment > -0.5: return 2
        else: return 1
        
    if 'rating' not in df.columns:
        df['rating'] = df['sentiment'].apply(sentiment_to_rating)
        
    df.rename(columns={review_column_name: 'review_text'}, inplace=True)
    
    return {
        "reviews": df[['rating','review_text','sentiment']].to_dict(orient='records'),
        "average_sentiment": df['sentiment'].mean()
    }

# ==============================================================================
# Final Report Generation 模块
# ==============================================================================

def generate_final_html_report(
    market_report: str,
    validation_summary: str,
    action_plan: str,
    sentiment_report: str | None = None,
    forecast_chart_json: str | None = None,
    clustering_data: dict | None = None,
    elbow_chart_json: str | None = None,
    scatter_3d_chart_json: str | None = None,
    basket_analysis_data: list | None = None
) -> str:
    """
    【最终升级版】将所有分析内容（包括购物篮分析）整合成HTML报告。
    """

    css_styles = """
    <style>
        body {
            font-family: 'Noto Sans CJK SC', 'Noto Sans SC', 'WenQuanYi Micro Hei', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #111827;
            color: #d1d5db;
        }
        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 20px;
            background-color: #1f2937;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            border-bottom: 1px solid #374151;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #ffffff;
            font-size: 2.5em;
            margin: 0;
        }
        .header p {
            color: #9ca3af;
            font-size: 1.1em;
        }
        .section {
            background-color: #374151;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .section h2 {
            font-size: 1.8em;
            color: #ffffff;
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .markdown-content h3 { font-size: 1.5em; color: #e5e7eb; }
        .markdown-content h4 { font-size: 1.2em; color: #d1d5db; }
        .markdown-content p, .markdown-content li { line-height: 1.7; }
        .markdown-content a { color: #818cf8; text-decoration: none; }
        .markdown-content a:hover { text-decoration: underline; }
        .markdown-content blockquote {
            border-left: 4px solid #4f46e5;
            padding-left: 15px;
            margin-left: 0;
            color: #9ca3af;
            font-style: italic;
        }
        .markdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .markdown-content th, .markdown-content td {
            border: 1px solid #4b5563;
            padding: 12px;
            text-align: left;
        }
        .markdown-content th {
            background-color: #4b5563;
            color: #ffffff;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 0.9em;
            color: #6b7280;
        }
    </style>
    """

    md_converter = markdown2.Markdown(extras=["tables", "fenced-code-blocks"])
    market_report_html = md_converter.convert(market_report)
    action_plan_html = md_converter.convert(action_plan)
    sentiment_report_html = md_converter.convert(sentiment_report) if sentiment_report else ""

    forecast_chart_html = ""
    if forecast_chart_json:
        try:
            fig = go.Figure(json.loads(forecast_chart_json))
            forecast_chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except Exception:
            forecast_chart_html = "<p><i>销售预测图表生成失败。</i></p>"
    
    # 手肘图：白底
    elbow_chart_html = ""
    if elbow_chart_json:
        try:
            fig = go.Figure(json.loads(elbow_chart_json))
            fig.update_layout(
                template='plotly_white',
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#111827")
            )
            elbow_chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except Exception:
            elbow_chart_html = "<p><i>手肘法图表生成失败。</i></p>"
    
    # 3D 图：强制白底（更强覆盖）
    scatter_3d_chart_html = ""
    if scatter_3d_chart_json:
        try:
            fig = go.Figure(json.loads(scatter_3d_chart_json))
            # 覆盖模板和颜色，确保不受 plotly_dark 影响
            fig.update_layout(template='plotly_white')
            fig.layout.template = 'plotly_white'  # 再次显式指定
            fig.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(color="#111827"),
                scene=dict(
                    bgcolor="#ffffff",
                    xaxis=dict(
                        backgroundcolor="#ffffff",
                        gridcolor="#e5e7eb",
                        zerolinecolor="#9ca3af",
                        showbackground=True
                    ),
                    yaxis=dict(
                        backgroundcolor="#ffffff",
                        gridcolor="#e5e7eb",
                        zerolinecolor="#9ca3af",
                        showbackground=True
                    ),
                    zaxis=dict(
                        backgroundcolor="#ffffff",
                        gridcolor="#e5e7eb",
                        zerolinecolor="#9ca3af",
                        showbackground=True
                    ),
                ),
            )
            scatter_3d_chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        except Exception:
            scatter_3d_chart_html = "<p><i>3D聚类图表生成失败。</i></p>"

    clustering_tables_html = ""
    if clustering_data:
        try:
            summary_df = pd.DataFrame(clustering_data.get('cluster_summary', []))
            all_products_df = pd.DataFrame(clustering_data.get('product_points', []))
            
            if not summary_df.empty:
                clustering_tables_html += "<h4>各商品簇特征均值</h4>"
                clustering_tables_html += summary_df.to_html(classes="markdown-content", border=0, index=False)

                hot_cluster = summary_df[summary_df['is_hot_cluster'] == True]
                if not hot_cluster.empty and not all_products_df.empty:
                    hot_cluster_id = hot_cluster.iloc[0]['cluster']
                    hot_products_df = all_products_df[all_products_df['cluster'] == hot_cluster_id].sort_values(by='total_amount', ascending=False)
                    
                    clustering_tables_html += f"<h4 style='margin-top: 20px;'>热销商品列表 (簇 {int(hot_cluster_id)})</h4>"
                    clustering_tables_html += hot_products_df[['SKU', 'total_amount', 'total_qty', 'order_count', 'cluster']].to_html(classes="markdown-content", border=0, index=False)
        except Exception:
            clustering_tables_html = "<p><i>聚类分析表格生成失败。</i></p>"
            
    basket_analysis_html = ""
    if basket_analysis_data:
        try:
            basket_df = pd.DataFrame(basket_analysis_data)
            if not basket_df.empty:
                basket_analysis_html += "<h4 style='margin-top: 20px;'>购物篮分析 (关联规则)</h4>"
                basket_analysis_html += "<p>提升度(lift) > 1 表示强关联性，是捆绑销售或交叉营销的绝佳机会。</p>"
                basket_analysis_html += basket_df.to_html(classes="markdown-content", border=0, index=False)
        except Exception:
            basket_analysis_html = "<p><i>购物篮分析表格生成失败。</i></p>"

    final_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WeaveAI 综合分析报告</title>
        {css_styles}
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 WeaveAI 综合分析报告</h1>
                <p>数据驱动决策，洞见商业未来</p>
            </div>

            <div class="section">
                <h2>第一部分：市场机会洞察 (Insight)</h2>
                <div class="markdown-content">
                    {market_report_html}
                </div>
            </div>

            <div class="section">
                <h2>第二部分：内部数据验证 (Validation)</h2>
                <div class="markdown-content">
                    <h4>验证摘要</h4>
                    <p>{validation_summary or "<i>未提供验证摘要。</i>"}</p>
                    
                    {forecast_chart_html}
                    
                    {'<hr style="border-color: #4b5563; margin: 30px 0;">' if (elbow_chart_html or scatter_3d_chart_html or clustering_tables_html or basket_analysis_html) else ''}
                    {elbow_chart_html}
                    {scatter_3d_chart_html}
                    {clustering_tables_html}
                    {basket_analysis_html}
                    
                    {'<hr style="border-color: #4b5563; margin: 30px 0;">' if sentiment_report_html else ''}
                    {f'<h4>AI 评论深度分析报告</h4>{sentiment_report_html}' if sentiment_report_html else ''}
                </div>
            </div>

            <div class="section">
                <h2>第三部分：季度行动计划 (Action Plan)</h2>
                <div class="markdown-content">
                    {action_plan_html}
                </div>
            </div>
            
            <div class="footer">
                <p>报告生成于 {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>&copy; WeaveAI智能分析助手</p>
            </div>
        </div>
    </body>
    </html>
    """
    return final_html
