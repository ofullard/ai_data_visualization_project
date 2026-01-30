import random
from datetime import datetime

import pandas as pd
import streamlit as st

from ai_client import generate_ai_response


st.set_page_config(page_title="AI Chat + Data Visualization", layout="wide")

st.title("AI Chat + Data Visualization")
st.caption("Streamlit dashboard for chat insights and analytics.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "text": "Welcome! Ask a question to generate AI insights from your data.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    ]

with st.sidebar:
    st.header("Controls")
    theme = st.selectbox("Visualization theme", ["Daily", "Weekly", "Monthly"])
    st.checkbox("Enable advanced analytics", value=False)

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

        ai_response = generate_ai_response(prompt)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "text": ai_response.message,
                "timestamp": ai_response.created_at
            }
        )
        st.experimental_rerun()

with viz_col:
    st.subheader("Live Insights")

    message_lengths = [len(message["text"]) for message in st.session_state.messages]
    chart_data = pd.DataFrame(
        {
            "Message": list(range(1, len(message_lengths) + 1)),
            "Length": message_lengths
        }
    )
    st.line_chart(chart_data.set_index("Message"))

    st.markdown("#### Topic Mix")
    topics = ["Support", "Operations", "Billing", "Product", "General"]
    values = [random.randint(10, 40) for _ in topics]
    topic_df = pd.DataFrame({"Topic": topics, "Volume": values})
    st.bar_chart(topic_df.set_index("Topic"))

    st.markdown("#### Response Time Snapshot")
    response_times = [random.gauss(2.4, 0.6) for _ in range(20)]
    response_df = pd.DataFrame({"Seconds": response_times})
    st.area_chart(response_df)
