import streamlit as st
import pandas as pd
import hmac
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# 1. Page configuration
# -----------------------------

st.set_page_config(
    page_title="ABC Coaching - Live Database",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# 2. Password protection
# -----------------------------

st.title("ABC Coaching - Live Database")
st.caption("Live student inquiry records")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    password = st.text_input(
        "Enter viewer password",
        type="password"
    )

    if st.button("Login"):
        correct_password = st.secrets["VIEWER_PASSWORD"]

        if hmac.compare_digest(password, correct_password):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")

    st.stop()

# -----------------------------
# 3. Connect to Supabase
# -----------------------------

@st.cache_resource
def init_supabase():

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SECRET_KEY"]

    return create_client(url, key)


supabase = init_supabase()

# -----------------------------
# 4. Automatically refresh
# -----------------------------

st_autorefresh(
    interval=5000,
    key="database_refresh"
)

# -----------------------------
# 5. Fetch database records
# -----------------------------

@st.cache_data(ttl=3)
def get_leads():

    response = (
        supabase
        .table("leads")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


# -----------------------------
# 6. Display records
# -----------------------------

try:

    leads = get_leads()

    st.success("Database connected")
    st.write("Connected Supabase project:",
         st.secrets["SUPABASE_URL"].split("//")[-1].split(".")[0])

    st.write("Records received from database:", len(leads))
        total = len(leads)

    col1, col2 = st.columns(2)

    col1.metric("Total inquiries", total)
    col2.metric("Auto refresh", "Every 5 seconds")

    st.divider()

    st.subheader("Student inquiries")

    if leads:

        df = pd.DataFrame(leads)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No inquiries have been submitted yet.")

    st.caption("Database refreshes automatically every 5 seconds.")

except Exception as e:

    st.error(f"Could not fetch database records: {e}")
