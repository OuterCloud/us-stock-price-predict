import streamlit as st
from datetime import datetime
from src.api_prices import get_prices

st.set_page_config(page_title="US Predict Dashboard")
st.title("美股预测仪表盘 - MVP")

ticker = st.text_input("股票代码", value="AAPL")
if st.button("查询"):
    try:
        result = get_prices(ticker)
        data = result["data"]
        if not data:
            st.error("暂无数据，请检查代码或稍后重试")
        else:
            df = data
            # quick render
            st.line_chart([row["close"] for row in df])
            st.write(f"最后更新时间：{datetime.utcnow().isoformat()}")
    except FileNotFoundError:
        st.error("数据文件不存在，请先运行数据抓取任务")
    except Exception as e:
        st.error(str(e))
