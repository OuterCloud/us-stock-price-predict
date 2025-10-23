import streamlit as st
from datetime import datetime
import pandas as pd
import altair as alt
from src.api_prices import get_prices
from src.data import write_parquet
from src.model import predict_next_prices

st.set_page_config(page_title="US Predict Dashboard")
st.title("美股预测仪表盘 - MVP")


def _ensure_state():
    if "query_state" not in st.session_state:
        st.session_state.query_state = "idle"  # idle, loading, done, error
    if "refresh_state" not in st.session_state:
        st.session_state.refresh_state = "idle"
    if "last_error" not in st.session_state:
        st.session_state.last_error = ""


_ensure_state()

ticker = st.text_input("股票代码", value="AAPL")

# 示例数据模式
sample_mode = st.checkbox("使用示例数据 (演示/编辑模式)")
if sample_mode:
    st.info("示例数据：可编辑，编辑后可保存为 data/stock_SAMPLE.parquet")
    # create a small sample dataframe
    sample_df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-09-01", "2025-09-02", "2025-09-03"]),
            "close": [11.0, 11.5, 12.0],
            "open": [10.5, 11.0, 11.6],
        }
    )
    edited = st.data_editor(sample_df, num_rows="dynamic")
    if not edited.empty:
        try:
            chart_df = edited.set_index("date")["close"]
            st.line_chart(chart_df)
        except Exception as e:
            st.error(f"绘图失败: {e}")
    if st.button("保存示例数据到 data/stock_SAMPLE.parquet"):
        try:
            # ensure date column is datetime
            edited["date"] = pd.to_datetime(edited["date"])
            write_parquet("SAMPLE", edited)
            st.success("已保存为 data/stock_SAMPLE.parquet")
        except Exception as e:
            st.error(f"保存失败: {e}")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    if st.button("查询", key="query_btn"):
        st.session_state.query_state = "loading"
        st.session_state.last_error = ""
        try:
            with st.spinner("查询中…"):
                result = get_prices(ticker)
            data = result["data"]
            if not data:
                st.session_state.query_state = "error"
                st.session_state.last_error = "暂无数据，请检查代码或稍后重试"
            else:
                st.session_state.query_state = "done"
                # convert list-of-dict to DataFrame and ensure date dtype
                df = pd.DataFrame(data)
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.sort_values("date")
                    # normalize to date-only (remove time) and format labels
                    df["date_only"] = df["date"].dt.normalize()
                    # try to use a no-leading-zero format; fallback if platform doesn't support %- directives
                    try:
                        axis_format = "%Y.%-m.%-d"
                        # test strftime support
                        _ = df["date_only"].dt.strftime(axis_format).iloc[0]
                    except Exception:
                        axis_format = "%Y.%m.%d"
                    base = alt.Chart(df).encode(
                        x=alt.X(
                            "date_only:T",
                            axis=alt.Axis(format=axis_format, labelAngle=-45),
                        )
                    )
                    price_line = base.mark_line(color="#1f77b4").encode(
                        y=alt.Y("close:Q", title="Close")
                    )
                    try:
                        prices = df["close"].tolist()
                        forecast_vals = predict_next_prices(prices, days=3, window=3)
                        last_date = df["date_only"].max()
                        future_dates = [
                            last_date + pd.Timedelta(days=i) for i in range(1, 4)
                        ]
                        forecast_df = pd.DataFrame(
                            {"date_only": future_dates, "close": forecast_vals}
                        )
                        forecast_line = (
                            alt.Chart(forecast_df)
                            .mark_line(color="#ff7f0e", strokeDash=[5, 5])
                            .encode(x=alt.X("date_only:T"), y=alt.Y("close:Q"))
                        )
                        chart = (price_line + forecast_line).properties(width=700)
                    except Exception:
                        chart = price_line.properties(width=700)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.line_chart(df["close"])
                st.write(f"最后更新时间：{datetime.utcnow().isoformat()}")
        except FileNotFoundError:
            st.session_state.query_state = "error"
            st.session_state.last_error = "数据文件不存在，请先运行数据抓取任务"
        except Exception as e:
            st.session_state.query_state = "error"
            st.session_state.last_error = str(e)

with col2:
    if st.button("刷新 (Fetch & Merge)", key="refresh_btn"):
        st.session_state.refresh_state = "loading"
        st.session_state.last_error = ""
        try:
            with st.spinner("刷新中（可能会触发网络请求 / 受限流影响）…"):
                result = get_prices(ticker, refresh=True)
            data = result["data"]
            if not data:
                st.session_state.refresh_state = "error"
                st.session_state.last_error = "刷新后仍无数据"
            else:
                st.session_state.refresh_state = "done"
                df = pd.DataFrame(data)
                st.success("刷新成功，已更新本地数据。")
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.sort_values("date")
                    df["date_only"] = df["date"].dt.normalize()
                    try:
                        axis_format = "%Y.%-m.%-d"
                        _ = df["date_only"].dt.strftime(axis_format).iloc[0]
                    except Exception:
                        axis_format = "%Y.%m.%d"
                    base = alt.Chart(df).encode(
                        x=alt.X(
                            "date_only:T",
                            axis=alt.Axis(format=axis_format, labelAngle=-45),
                        )
                    )
                    price_line = base.mark_line(color="#1f77b4").encode(
                        y=alt.Y("close:Q", title="Close")
                    )
                    try:
                        prices = df["close"].tolist()
                        forecast_vals = predict_next_prices(prices, days=3, window=3)
                        last_date = df["date_only"].max()
                        future_dates = [
                            last_date + pd.Timedelta(days=i) for i in range(1, 4)
                        ]
                        forecast_df = pd.DataFrame(
                            {"date_only": future_dates, "close": forecast_vals}
                        )
                        forecast_line = (
                            alt.Chart(forecast_df)
                            .mark_line(color="#ff7f0e", strokeDash=[5, 5])
                            .encode(x=alt.X("date_only:T"), y=alt.Y("close:Q"))
                        )
                        chart = (price_line + forecast_line).properties(width=700)
                    except Exception:
                        chart = price_line.properties(width=700)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.line_chart(df["close"])
                st.write(f"最后更新时间：{datetime.utcnow().isoformat()}")
        except Exception as e:
            st.session_state.refresh_state = "error"
            # present rate-limit friendly message if detected
            msg = str(e)
            if "rate limited" in msg.lower() or "429" in msg:
                st.session_state.last_error = "检测到服务端限流 (HTTP 429)。请稍后重试，或减少请求频率/使用代理或付费数据源。"
            else:
                st.session_state.last_error = msg


if st.session_state.last_error:
    st.error(st.session_state.last_error)

# Show simple state badges
st.markdown("---")
st.write(
    f"查询状态: {st.session_state.query_state}  |  刷新状态: {st.session_state.refresh_state}"
)
