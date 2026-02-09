import random
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

from ai_client import generate_ai_response


st.set_page_config(page_title="AI Chat + Data Visualization", layout="wide")

st.title("AI Chat + Data Visualization")
st.caption("Streamlit dashboard for chat insights and analytics.")

DB_PATH = Path(__file__).resolve().parent / "sample_chat.db"

SAMPLE_LOGS = [
    {
        "role": "assistant",
        "text": "Welcome! Ask a question to generate AI insights from your data.",
        "timestamp": "09:00:00",
        "topic": "General",
        "response_seconds": 1.2,
    },
    {
        "role": "user",
        "text": "Show me trends in support tickets over the last month.",
        "timestamp": "09:01:14",
        "topic": "Support",
        "response_seconds": None,
    },
    {
        "role": "assistant",
        "text": "Support volume peaked mid-month, with 18% more tickets than average.",
        "timestamp": "09:01:18",
        "topic": "Support",
        "response_seconds": 2.1,
    },
    {
        "role": "user",
        "text": "How does billing compare to operations this quarter?",
        "timestamp": "09:03:02",
        "topic": "Billing",
        "response_seconds": None,
    },
    {
        "role": "assistant",
        "text": "Billing requests are up 12%, while operations inquiries are flat.",
        "timestamp": "09:03:07",
        "topic": "Billing",
        "response_seconds": 2.6,
    },
    {
        "role": "user",
        "text": "Summarize product feedback themes.",
        "timestamp": "09:05:11",
        "topic": "Product",
        "response_seconds": None,
    },
    {
        "role": "assistant",
        "text": "Feedback centers on onboarding clarity and export performance.",
        "timestamp": "09:05:15",
        "topic": "Product",
        "response_seconds": 1.9,
    },
]


def init_sample_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                topic TEXT,
                response_seconds REAL
            )
            """
        )
        existing = conn.execute("SELECT COUNT(*) FROM chat_logs").fetchone()
        if existing and existing[0] == 0:
            conn.executemany(
                """
                INSERT INTO chat_logs (role, text, timestamp, topic, response_seconds)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        log["role"],
                        log["text"],
                        log["timestamp"],
                        log.get("topic"),
                        log.get("response_seconds"),
                    )
                    for log in SAMPLE_LOGS
                ],
            )
            conn.commit()
    finally:
        conn.close()


def load_logs_from_db() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(
            """
            SELECT role, text, timestamp, topic, response_seconds
            FROM chat_logs
            ORDER BY id ASC
            """,
            conn,
        )
    finally:
        conn.close()

init_sample_db()
log_df = load_logs_from_db()
log_records = log_df.to_dict(orient="records")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": log["role"], "text": log["text"], "timestamp": log["timestamp"]}
        for log in log_records
    ]
    st.session_state["sample_logs"] = log_records

if "live_logs" not in st.session_state:
    st.session_state["live_logs"] = [log.copy() for log in log_records]

with st.sidebar:
    st.header("Controls")
    theme = st.selectbox("Visualization theme", ["Daily", "Weekly", "Monthly"])
    st.checkbox("Enable advanced analytics", value=False)
    data_source = st.radio(
        "Insights data source",
        ["Database (sample_chat.db)", "Live session"],
        horizontal=True,
    )

chat_col, viz_col = st.columns([1.2, 1])

with chat_col:
    st.subheader("Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f"**{message['timestamp']}** — {message['text']}")

    if prompt := st.chat_input("Type a message"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append(
            {"role": "user", "text": prompt, "timestamp": timestamp}
        )
        st.session_state["live_logs"].append(
            {
                "role": "user",
                "text": prompt,
                "timestamp": timestamp,
                "topic": "General",
                "response_seconds": None,
            }
        )

        ai_response = generate_ai_response(prompt)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "text": ai_response.message,
                "timestamp": ai_response.created_at
            }
        )
        st.session_state["live_logs"].append(
            {
                "role": "assistant",
                "text": ai_response.message,
                "timestamp": ai_response.created_at,
                "topic": "General",
                "response_seconds": round(random.uniform(1.2, 3.2), 2),
            }
        )
        st.experimental_rerun()

with viz_col:
    st.subheader("Live Insights")

    if data_source == "Database (sample_chat.db)":
        active_logs = log_records
    else:
        active_logs = st.session_state["live_logs"]
    active_df = pd.DataFrame(active_logs)

    message_lengths = [len(message["text"]) for message in st.session_state.messages]
    chart_data = pd.DataFrame(
        {
            "Message": list(range(1, len(message_lengths) + 1)),
            "Length": message_lengths
        }
    )
    st.line_chart(chart_data.set_index("Message"))

    st.markdown("#### Topic Mix")
    if not active_df.empty and "topic" in active_df.columns:
        topic_df = (
            active_df.fillna({"topic": "General"})
            .groupby("topic", as_index=False)
            .size()
            .rename(columns={"topic": "Topic", "size": "Volume"})
        )
    else:
        topics = ["Support", "Operations", "Billing", "Product", "General"]
        values = [random.randint(10, 40) for _ in topics]
        topic_df = pd.DataFrame({"Topic": topics, "Volume": values})
    st.bar_chart(topic_df.set_index("Topic"))

    st.markdown("#### Response Time Snapshot")
    if not active_df.empty and "response_seconds" in active_df.columns:
        response_times = [
            value for value in active_df["response_seconds"].dropna().tolist()
        ]
    else:
        response_times = [random.gauss(2.4, 0.6) for _ in range(20)]
    response_df = pd.DataFrame({"Seconds": response_times})
    st.area_chart(response_df)

    st.markdown("### Data Tables")
    if active_df.empty:
        st.info("No records available for the selected data source.")
    else:
        st.dataframe(
            active_df[["timestamp", "role", "topic", "text", "response_seconds"]],
            use_container_width=True,
        )
        summary_df = (
            active_df.fillna({"topic": "General"})
            .groupby("topic", as_index=False)
            .agg(
                message_count=("text", "count"),
                avg_response_seconds=("response_seconds", "mean"),
            )
            .rename(columns={"topic": "Topic"})
        )
        st.dataframe(summary_df, use_container_width=True)
