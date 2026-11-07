""" 
Day 22(SPRINT4): Streamlit app scaffold: main entry point. 

Run with: streamlit run src/dashboard/app.py 
        -> Streamlit auto-discovers the 8 screens from the sibling pages/ directory 
        -> (src/dashboard/pages/) and builds the sidebar nav from them automatically 
        -- no manual nav wiring!.. 

MODIFY APP.py - BY REPLACING PLACEHOLDER AND CHANGE IN STYLING.. 
    NOW: The entrypoint owns the shared application configuration and navigation. 
        Individual screens remain in `src/dashboard/pages/ so their existing 
        analytics/UI logic can stay isolated from the app shell.
"""

from pathlib import Path
import time
import streamlit as st
from utils.api_client import APIClientError, health

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Nifty 100 Financial Intelligence",
    page_icon="./assets/graph.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Shared visual polish for the application shell. The analytical pages keep
# their own content/UI logic; these rules only make Streamlit's native shell
# and status messages fit the Deep Navy + Teal theme.

# Custom CSS targeting the Bloomberg Deep Slate layout rules
st.markdown(
    """
    <style>
        /* 1. Electric Cyan coloring to Sidebar */
        [data-testid="stSidebarNav"] span[data-testid="stIconMaterial"], 
        header [data-testid="stIconMaterial"] {
            color: #38BDF8 !important;
        }
        
        /* 2. Softened sidebar dividing boundary line */
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        /* Keep sidebar content in its own scrollable layer. */
        [data-testid="stSidebarContent"] {
            overflow-y: auto !important;
            overscroll-behavior: contain;
        }
        
        /* 3. Native Streamlit status messages */
        [data-testid="stAlert"] {
            background: rgba(15, 23, 42, 0.75) !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-left: 3px solid rgba(56, 189, 248, 0.8) !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            padding: 0.55rem 0.8rem !important;
            margin: 0.5rem 0 0.75rem 0 !important;
        }

        [data-testid="stAlert"] p {
            color: #E2E8F0 !important;
            font-size: 0.88rem !important;
        }

        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
            color: #E2E8F0 !important;
        }

        /* Keep the message icon visually aligned with the text. */
        [data-testid="stAlert"] svg {
            margin-top: 0.05rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit's st.navigation/st.Page API gives us explicit control over labels,
# icons, URL paths, and section grouping while preserving the existing page files.
HOME = st.Page(
    str(BASE_DIR / "pages" / "01_home.py"),
    title="Home",
    icon=":material/home:",
    url_path="home",
    default=True,
)
PROFILE = st.Page(
    str(BASE_DIR / "pages" / "02_profile.py"),
    title="Company Profile",
    icon=":material/business:",
    url_path="profile",
)
SCREENER = st.Page(
    str(BASE_DIR / "pages" / "03_screener.py"),
    title="Screener",
    icon=":material/filter_alt:",
    url_path="screener",
)
PEERS = st.Page(
    str(BASE_DIR / "pages" / "04_peers.py"),
    title="Peer Comparison",
    icon=":material/groups:",
    url_path="peers",
)
TRENDS = st.Page(
    str(BASE_DIR / "pages" / "05_trends.py"),
    title="Trend Analysis",
    icon=":material/trending_up:",
    url_path="trends",
)
SECTORS = st.Page(
    str(BASE_DIR / "pages" / "06_sectors.py"),
    title="Sector Analysis",
    icon=":material/donut_large:",
    url_path="sectors",
)
CAPITAL = st.Page(
    str(BASE_DIR / "pages" / "07_capital.py"),
    title="Capital Allocation",
    icon=":material/account_balance:",
    url_path="capital-allocation",
)
REPORTS = st.Page(
    str(BASE_DIR / "pages" / "08_reports.py"),
    title="Annual Reports",
    icon=":material/description:",
    url_path="reports",
)

pg = st.navigation(
    {
        "Overview": [HOME, PROFILE],
        "Analysis": [SCREENER, PEERS, TRENDS, SECTORS, CAPITAL],
        "Reports": [REPORTS],
    },
    position="sidebar",
    expanded=True,
)

# Keep the connection state visible in both the sidebar and the main content
# while the hosted backend is waking from inactivity.
backend_status = st.sidebar.empty()
backend_notice = st.empty()
BACKEND_HEALTH_TTL_SECONDS = 60.0

def _show_backend_attempt(attempt: int, total_attempts: int) -> None:
    """Update the sidebar and main-page notice during backend connection attempts."""
    if attempt == 1:
        backend_status.caption("Backend · connecting...")
        backend_notice.info("Connecting to the hosted backend...")        
    else:
        backend_status.caption("Backend · waking up...")
        backend_notice.info(
            "The hosted backend is waking from inactivity... Please wait a moment while it starts."
        )           

last_health_success = st.session_state.get("_backend_health_last_success")
health_is_fresh = (
    last_health_success is not None
    and time.monotonic() - last_health_success < BACKEND_HEALTH_TTL_SECONDS
)

if health_is_fresh:
    # Page navigation reruns the app shell. 
    # Reuse a recent successful health check so every navigation does not briefly show the startup state.
    backend_status.caption("Backend · connected")
    backend_notice.empty()
else:
    try:
        backend_health = health(on_attempt=_show_backend_attempt)
        st.session_state["_backend_health_last_success"] = time.monotonic()
        backend_status.caption("Backend · connected")
        backend_notice.empty()
    except APIClientError as exc:
        st.session_state.pop("_backend_health_last_success", None)
        backend_status.caption("Backend · unavailable")
        backend_notice.info(str(exc))

        # Keep the final message compact and neutral. 
        # The API client provides a short local-development instruction or a concise deployed recovery note.
        st.sidebar.info(str(exc))

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 0.65rem 0.8rem; margin: 0.5rem 0;">
        <div style="font-weight: 700; color: #F8FAFC; font-size: 0.88rem; letter-spacing: -0.01em;">Mukesh Revanth</div>
        <div style="color: #38BDF8; font-size: 0.76rem; font-weight: 600; margin-top: 1px;">Data Analyst Intern</div>
        <div style="color: #94A3B8; font-size: 0.72rem; margin-top: 1px;">Bluestock Fintech</div>
        <div style="margin-top: 0.45rem; padding-top: 0.45rem; border-top: 1px solid rgba(148, 163, 184, 0.15); display: flex; justify-content: space-between;">
            <a href="https://github.com/Revanth-4233/N100-financial-intelligence-platform" target="_blank" style="color: #60A5FA; text-decoration: none; font-size: 0.72rem; font-weight: 500;">GitHub ↗</a>
            <span style="color: #64748B; font-size: 0.70rem;">v1.2.0</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

pg.run()