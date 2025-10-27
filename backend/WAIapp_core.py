# backend/WAIapp_core.py

import os
import pandas as pd
import numpy as np
import warnings
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

# 分析库
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pandas.errors import SettingWithCopyWarning, DtypeWarning

# 可视化库
import plotly.graph_objects as go
import plotly.express as px

# 加载环境变量
load_dotenv()

# (关键) 解决 KMeans 内存泄漏警告
os.environ['OMP_NUM_THREADS'] = '1'

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

    request_params = {"model": "doubao-seed-1-6-250615", "input": [{"role": "system", "content": [{"type": "input_text", "text": system_prompt}]}, {"role": "user", "content": [{"type": "input_text", "text": user_input}]}], "tools": [{"type": "web_search", "limit": 15}], "stream": True}
    
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
# 数据处理模块
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

def perform_product_clustering(df: pd.DataFrame) -> dict:
    """产品聚类函数，返回包含多个DataFrame的字典"""
    required_cols = ['SKU', 'Amount', 'Qty', 'Order ID']
    if not all(col in df.columns for col in df.columns):
        raise ValueError("聚类分析失败：缺少必要的列。")
    
    product_agg_df = df.groupby('SKU').agg(total_amount=('Amount', 'sum'), total_qty=('Qty', 'sum'), order_count=('Order ID', 'nunique')).reset_index()
    features = product_agg_df[['total_amount', 'total_qty', 'order_count']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    kmeans = KMeans(n_clusters=3, n_init=10, random_state=42)
    product_agg_df['cluster'] = kmeans.fit_predict(features_scaled)
    
    cluster_summary = product_agg_df.groupby('cluster')[['total_amount', 'total_qty', 'order_count']].mean().sort_values(by='total_amount', ascending=False)
    
    hot_product_cluster_id = cluster_summary.index[0]
    hot_products = product_agg_df[product_agg_df['cluster'] == hot_product_cluster_id].sort_values(by='total_amount', ascending=False)
    
    # 将DataFrame转为JSON兼容的格式(字典列表)
    return {
        "cluster_summary": cluster_summary.reset_index().to_dict(orient='records'),
        "hot_products": hot_products.to_dict(orient='records')
    }

def perform_sentiment_analysis(df: pd.DataFrame) -> dict:
    """情感分析函数，返回包含分析结果的字典"""
    
    def find_review_column(df_to_check: pd.DataFrame) -> str | None:
        """在 DataFrame 中智能查找最可能包含评论文本的列名。"""
        # 1. 最高优先级：检查常见的标准列名
        priority_cols = ['reviews.text', 'review_text', 'content', 'comment', 'review']
        for p_col in priority_cols:
            if p_col in df_to_check.columns and df_to_check[p_col].dropna().astype(str).str.strip().any():
                return p_col
        
        # 2. 次高优先级：模糊匹配列名中包含关键词的列
        possible_cols = [col for col in df_to_check.columns if any(key in str(col).lower() for key in ['text', 'review', 'content', 'comment'])]
        if possible_cols:
            string_cols = [col for col in possible_cols if df_to_check[col].dtype == 'object']
            if string_cols:
                return max(string_cols, key=lambda col: df_to_check[col].dropna().astype(str).str.len().mean())
        
        # 3. 最低优先级：遍历所有字符串类型的列
        object_cols = df_to_check.select_dtypes(include=['object']).columns
        if not object_cols.empty:
            for col in object_cols:
                if df_to_check[col].dropna().astype(str).str.strip().any():
                    return col
                    
        # 4. 如果都找不到，返回 None
        return None

    review_column_name = find_review_column(df)
    if review_column_name is None:
        raise ValueError("错误: 未能在评论文件中找到有效的文本列。")
        
    df[review_column_name] = df[review_column_name].astype(str).dropna()
    df = df[df[review_column_name].str.strip() != 'None'].copy()
    
    analyzer = SentimentIntensityAnalyzer()
    df['sentiment'] = df[review_column_name].apply(lambda text: analyzer.polarity_scores(text)['compound'])
    
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