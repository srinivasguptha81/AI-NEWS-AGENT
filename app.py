import datetime
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/get_news/"
CATEGORIES = [
    "Custom", "General", "World", "Nation", "Business",
    "Technology", "Entertainment", "Sports", "Science", "Health"
]
SENTIMENT_COLORS = {
    "POSITIVE": "#22c55e",
    "NEGATIVE": "#ef4444",
    "NEUTRAL": "#64748b",
}

st.set_page_config(page_title="AI News Agent", page_icon="🧠", layout="wide")

# ---------------- STATE ----------------
if "news" not in st.session_state:
    st.session_state.news = []
if "loading" not in st.session_state:
    st.session_state.loading = False

# ---------------- UI STYLES ----------------
# Added some basic CSS to support your custom HTML below
st.markdown("""
    <style>
    .card { padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e2e8f0; background-color: #f8fafc; color: #0f172a;}
    .sentiment { padding: 4px 10px; border-radius: 4px; color: white; font-weight: 600; font-size: 0.8em; display: inline-block; margin-bottom: 8px; }
    .title { font-size: 1.1em; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🧠 AI News Agent")
st.markdown("---")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Filters")
    location = st.text_input("Location", "USA")
    category = st.selectbox("Category", CATEGORIES)

    custom_query = ""
    if category == "Custom":
        custom_query = st.text_input("Custom Topic")

    today = datetime.date.today()
    start_date = st.date_input("Start Date", today - datetime.timedelta(days=1))
    end_date = st.date_input("End Date", today)

    fetch_btn = st.button("🚀 Fetch News", use_container_width=True)

# ---------------- FETCH FUNCTION ----------------
def fetch_news():
    try:
        res = requests.get(
            API_URL,
            params={
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "category": category,
                "custom_query": custom_query
            },
            timeout=120  # Increased from 20 to 120 seconds
        )
        # Raise an error if the HTTP request returned an unsuccessful status code
        res.raise_for_status() 
        return res.json()
    except Exception as e:
        st.error(f"Backend Error: {e}")
        return {}

# ---------------- FETCH ACTION ----------------
if fetch_btn:
    st.session_state.loading = True
    with st.spinner("⚡ Fetching & summarizing news..."):
        data = fetch_news()
        st.session_state.news = data.get("news", [])
    
    st.session_state.loading = False

# ---------------- MAIN DISPLAY ----------------
if st.session_state.loading:
    st.warning("Still loading...")
elif st.session_state.news:

    col1, col2, col3 = st.columns(3)

    col1.metric("Articles", len(st.session_state.news))
    col2.metric(
        "Positive",
        sum(1 for n in st.session_state.news if n.get("sentiment") == "POSITIVE")
    )
    col3.metric(
        "Negative",
        sum(1 for n in st.session_state.news if n.get("sentiment") == "NEGATIVE")
    )

    st.divider()

    for i, news in enumerate(st.session_state.news):

        sentiment = news.get("sentiment", "NEUTRAL")
        color = SENTIMENT_COLORS.get(sentiment, "#64748b")

        st.markdown(f"""
        <div class="card">
            <div class="sentiment" style="background:{color}">
                {sentiment}
            </div>
            <div class="title">{i+1}. {news.get("title", "Untitled Article")}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📖 Read Summary"):
            st.write(news.get("summary", "No summary available"))
            if news.get("url"):
                st.link_button("🔗 Read Full Article", news["url"])
else:
    st.info("👈 Use filters and click 'Fetch News' to start")