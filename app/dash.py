import streamlit as st
import pandas as pd
import psycopg2
import plotly.graph_objects as go
import plotly.express as px
import time

st.set_page_config(
    page_title="NFC Fraud Guard | Live Edge Telemetry",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background-color: #111827;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #374151;
    }
    .status-approve { color: #10B981; font-weight: 700; }
    .status-challenge { color: #F59E0B; font-weight: 700; }
    .status-decline { color: #EF4444; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ Telemetry Controls")
refresh_rate = st.sidebar.slider("Polling Frequency (seconds)", 1, 10, 2)
anomaly_threshold = st.sidebar.slider("Reconstruction Threshold ($L_2$)", 0.10, 1.00, 0.70, 0.05)
auto_refresh = st.sidebar.toggle("Live Auto-Refresh", value=True)

st.title("Edge-NFC Fraud Inference Engine")
st.caption("Real-Time Telemetry Feed: Android Contactless Terminal -> FastAPI Backend")

def fetch_data():
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fraud_db",
            user="postgres",
            password="prince!71@post",
            port=5432
        )
        query = "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 25;"
        df = pd.read_sql(query, conn)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)
    finally:
        if conn:
            conn.close()

df, db_error = fetch_data()

if db_error:
    st.error(f"⚠️ PostgreSQL Connection Error: {db_error}")
    st.info("Ensure PostgreSQL is running on port 5432 with password 'postgrespassword' and database 'fraud_db'.")

elif not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    total_txns = len(df)
    declines = len(df[df["decision"] == "DECLINE"])
    challenges = len(df[df["decision"] == "CHALLENGE"])
    avg_loss = df["reconstruction_loss"].mean()

    col1.metric("Total Edge Events", total_txns)
    col2.metric("Declined (Outliers)", declines, delta=f"{declines} caught", delta_color="inverse")
    col3.metric("2FA Challenges", challenges)
    col4.metric("Mean L2 Loss", f"{avg_loss:.4f}")

    st.divider()

    latest = df.iloc[0]
    badge = "status-approve" if latest["decision"] == "APPROVE" else ("status-challenge" if latest["decision"] == "CHALLENGE" else "status-decline")
    st.subheader("Latest Live Tap Event")
    st.markdown(f"""
    <div class="metric-card">
        <h3>Card: <code>{latest['card_id']}</code> | User: <code>{latest['user_id']}</code></h3>
        <p>Amount: <b>₹{latest['amount']:,.2f}</b> | Category: <b>{latest['merchant_category']}</b> | Mode: <b>{latest['pos_entry_mode']}</b></p>
        <p>Reconstruction Loss: <code>{latest['reconstruction_loss']:.4f}</code> | Decision: <span class="{badge}">{latest['decision']}</span></p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Autoencoder Loss Curve")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["reconstruction_loss"], mode='lines+markers', name='L2 Loss'))
        fig.add_hline(y=anomaly_threshold, line_dash="dash", line_color="red", annotation_text="Decline Boundary")
        fig.add_hline(y=0.25, line_dash="dot", line_color="orange", annotation_text="Challenge Boundary")
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=25, b=10), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Decisions Breakdown")
        pie = px.pie(df, names="decision", color="decision",
                     color_discrete_map={"APPROVE": "#10B981", "CHALLENGE": "#F59E0B", "DECLINE": "#EF4444"}, hole=0.4)
        pie.update_layout(height=280, margin=dict(l=10, r=10, t=25, b=10), template="plotly_dark")
        st.plotly_chart(pie, use_container_width=True)

    st.subheader("Audit Log")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Awaiting incoming edge transactions from Android NFC terminal or test triggers...")

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()