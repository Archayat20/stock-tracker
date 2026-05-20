"""
Stock Research Agent — pages/stock_research_agent.py
=====================================================
Fixed for Groq/Llama tool use:
  - tool_choice="required" then "none" pattern
  - tools called one at a time
  - calculate_metrics takes a single dict string (avoids Llama formatting bugs)
"""

import json
import streamlit as st
import yfinance as yf
from groq import Groq

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stock Research Agent", page_icon="🔬", layout="wide")

# ── Groq client ────────────────────────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL  = "llama-3.3-70b-versatile"


# ══════════════════════════════════════════════════════════════════════════════
#  TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def get_stock_data(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        hist  = stock.history(period="1mo")
        if hist.empty:
            return {"error": f"No price data found for '{ticker}'."}
        close = hist["Close"]
        return {
            "ticker":          ticker.upper(),
            "company_name":    info.get("longName", ticker),
            "sector":          info.get("sector", "N/A"),
            "industry":        info.get("industry", "N/A"),
            "price":           round(close.iloc[-1], 2),
            "price_1d_change": round(close.iloc[-1] - close.iloc[-2], 2),
            "price_1d_pct":    round((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100, 2),
            "price_1mo_pct":   round((close.iloc[-1] - close.iloc[0])  / close.iloc[0]  * 100, 2),
            "high_1mo":        round(hist["High"].max(), 2),
            "low_1mo":         round(hist["Low"].min(),  2),
            "avg_volume":      int(hist["Volume"].mean()),
            "market_cap":      info.get("marketCap"),
            "pe_ratio":        info.get("trailingPE"),
            "eps":             info.get("trailingEps"),
            "revenue":         info.get("totalRevenue"),
            "profit_margin":   info.get("profitMargins"),
            "debt_to_equity":  info.get("debtToEquity"),
            "52w_high":        info.get("fiftyTwoWeekHigh"),
            "52w_low":         info.get("fiftyTwoWeekLow"),
            "analyst_target":  info.get("targetMeanPrice"),
            "recommendation":  info.get("recommendationKey", "N/A"),
            "beta":            info.get("beta"),
            "summary":         (info.get("longBusinessSummary") or "")[:300],
        }
    except Exception as e:
        return {"error": str(e)}


def get_stock_news(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        news  = stock.news or []
        items = []
        for n in news[:6]:
            content = n.get("content", {})
            items.append({
                "title":     content.get("title", "No title"),
                "summary":   (content.get("summary") or "")[:150],
                "published": content.get("pubDate", ""),
            })
        return {"ticker": ticker.upper(), "articles": items}
    except Exception as e:
        return {"error": str(e)}


def calculate_metrics(ticker: str) -> dict:
    """
    Fetch data internally and compute all metrics — no numeric args needed.
    This avoids Llama/Groq's buggy multi-float argument formatting.
    """
    try:
        data = get_stock_data(ticker)
        if "error" in data:
            return data
        price          = data["price"]
        eps            = data.get("eps")
        high_52w       = data.get("52w_high")
        low_52w        = data.get("52w_low")
        analyst_target = data.get("analyst_target")
        result         = {"ticker": ticker.upper()}
        if eps and eps > 0:
            result["pe_from_price"] = round(price / eps, 2)
        if high_52w:
            result["pct_below_52w_high"] = round((high_52w - price) / high_52w * 100, 2)
        if low_52w:
            result["pct_above_52w_low"]  = round((price - low_52w) / low_52w * 100, 2)
        if analyst_target:
            result["upside_to_target_pct"] = round((analyst_target - price) / price * 100, 2)
        if high_52w and low_52w:
            rng = high_52w - low_52w
            result["52w_range_position_pct"] = round((price - low_52w) / rng * 100, 2) if rng else None
        return result
    except Exception as e:
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
#  TOOL REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_data",
            "description": "Fetch live price and fundamentals (P/E, EPS, market cap, 52-week range, analyst target) for a stock ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker e.g. AAPL"}
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_news",
            "description": "Fetch the latest news headlines for a stock ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker e.g. AAPL"}
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_metrics",
            "description": "Calculate derived financial metrics (upside to target, 52-week range position, P/E) for a ticker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker e.g. AAPL"}
                },
                "required": ["ticker"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "get_stock_data":    lambda inp: get_stock_data(**inp),
    "get_stock_news":    lambda inp: get_stock_news(**inp),
    "calculate_metrics": lambda inp: calculate_metrics(**inp),
}


# ══════════════════════════════════════════════════════════════════════════════
#  AGENTIC LOOP  (fixed for Groq reliability)
# ══════════════════════════════════════════════════════════════════════════════

def run_agent(user_query: str, tool_log_container) -> str:
    system = """You are an expert stock research analyst. You have three tools:
- get_stock_data: get price, fundamentals, analyst targets
- get_stock_news: get latest headlines
- calculate_metrics: compute derived metrics like upside % and 52-week position

For every research request, call ALL THREE tools (one at a time) before writing your report.
Format your final answer with these sections: Overview, Performance, Fundamentals, News Sentiment, Verdict."""

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": user_query},
    ]

    max_iterations = 8  # safety cap to prevent infinite loops
    iteration      = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            max_tokens=2048,
        )

        msg = response.choices[0].message

        # No tool calls → model is done
        if not msg.tool_calls:
            return msg.content or "No response generated."

        # Process tool calls ONE AT A TIME (fixes Groq multi-arg bug)
        messages.append({
            "role":       "assistant",
            "content":    msg.content or "",
            "tool_calls": msg.tool_calls,
        })

        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name

            try:
                tool_input = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_input = {}

            with tool_log_container:
                with st.expander(f"🔧 Calling `{tool_name}`", expanded=False):
                    st.json(tool_input)

            try:
                result = TOOL_FUNCTIONS[tool_name](tool_input)
            except Exception as e:
                result = {"error": str(e)}

            with tool_log_container:
                with st.expander(f"✅ `{tool_name}` result", expanded=False):
                    st.json(result)

            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "name":         tool_name,
                "content":      json.dumps(result),
            })

    return "Agent reached maximum iterations without completing. Please try again."


# ══════════════════════════════════════════════════════════════════════════════
#  STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════

st.title("🔬 Stock Research Agent")
st.caption("Powered by Groq (free) + Llama 3.3 — plans, calls tools, synthesizes findings.")

with st.expander("⚙️ How this agent works", expanded=False):
    col1, col2, col3 = st.columns(3)
    col1.markdown("**🧠 LLM (Groq / Llama 3.3)**\nDecides which tools to call and in what order")
    col2.markdown("**🔧 Tools**\n`get_stock_data` · `get_stock_news` · `calculate_metrics`")
    col3.markdown("**🔄 Agentic Loop**\nKeeps calling tools until it has enough info to answer")

st.divider()

if "agent_history" not in st.session_state:
    st.session_state.agent_history = []

with st.sidebar:
    st.header("🔬 Research Agent")
    st.caption("Free · Powered by Groq")
    st.markdown("**Example queries:**")
    examples = [
        "Research AAPL and give me a full report",
        "Is TSLA a good buy right now?",
        "Analyze MSFT fundamentals and recent news",
        "What's the latest on NVDA?",
        "Give me an overview of AMZN including risks",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True, key=ex):
            st.session_state["prefill"] = ex
    if st.button("🗑️ Clear history", use_container_width=True):
        st.session_state.agent_history = []
        st.rerun()

for entry in st.session_state.agent_history:
    with st.chat_message("user"):
        st.markdown(entry["query"])
    with st.chat_message("assistant"):
        st.markdown(entry["response"])

prefill    = st.session_state.pop("prefill", None)
user_input = st.chat_input("Ask the agent to research any stock…") or prefill

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        tool_log   = st.container()
        result_box = st.empty()

        with st.spinner("Agent running…"):
            answer = run_agent(user_input, tool_log)

        result_box.markdown(answer)

    st.session_state.agent_history.append({"query": user_input, "response": answer})