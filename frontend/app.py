"""
Streamlit frontend for Secure Enterprise RAG Copilot.

Run from project root:
    streamlit run frontend/app.py
"""
import os
import requests
import streamlit as st
from datetime import datetime

# ─── Config ────────────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Role styling
ROLE_CONFIG = {
    "public": {
        "color": "#22c55e",
        "bg": "rgba(34,197,94,0.15)",
        "border": "#22c55e",
        "icon": "🌐",
        "label": "PUBLIC",
        "desc": "Access to public documents only",
    },
    "employee": {
        "color": "#3b82f6",
        "bg": "rgba(59,130,246,0.15)",
        "border": "#3b82f6",
        "icon": "👤",
        "label": "EMPLOYEE",
        "desc": "Access to public + employee documents",
    },
    "manager": {
        "color": "#f59e0b",
        "bg": "rgba(245,158,11,0.15)",
        "border": "#f59e0b",
        "icon": "🏢",
        "label": "MANAGER",
        "desc": "Access to public + employee + manager documents",
    },
    "hr": {
        "color": "#a855f7",
        "bg": "rgba(168,85,247,0.15)",
        "border": "#a855f7",
        "icon": "🔐",
        "label": "HR",
        "desc": "Full access — all document levels",
    },
}

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechCorp RAG Copilot",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    min-height: 100vh;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(20px);
}

/* Inputs */
.stTextInput > div > div > input,
.stTextInput > div > div > input:focus {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(255,255,255,0.3) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Text areas */
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
    resize: vertical !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #94a3b8 !important;
    font-size: 13px !important;
}

/* Chat message cards */
.user-bubble {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.25));
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 16px 16px 4px 16px;
    padding: 16px 20px;
    margin: 8px 0 8px 40px;
    color: #e2e8f0;
    font-size: 14px;
    line-height: 1.6;
    animation: fadeInRight 0.3s ease;
}

.assistant-bubble {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 16px 16px 16px;
    padding: 16px 20px;
    margin: 8px 40px 8px 0;
    color: #e2e8f0;
    font-size: 14px;
    line-height: 1.7;
    animation: fadeInLeft 0.3s ease;
}

.assistant-bubble.access-denied {
    border-color: rgba(239,68,68,0.4);
    background: rgba(239,68,68,0.08);
}

.bubble-header {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 8px;
    opacity: 0.6;
}

/* Role badge */
.role-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 50px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    border: 1px solid;
    margin-bottom: 8px;
}

/* Source chip */
.source-chip {
    display: inline-block;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 11px;
    color: #94a3b8;
    margin: 2px;
    font-family: 'Courier New', monospace;
}

/* Access level tags */
.level-tag-public   { color: #22c55e; background: rgba(34,197,94,0.1);   border: 1px solid rgba(34,197,94,0.3);   border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600; }
.level-tag-employee { color: #3b82f6; background: rgba(59,130,246,0.1);  border: 1px solid rgba(59,130,246,0.3);  border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600; }
.level-tag-manager  { color: #f59e0b; background: rgba(245,158,11,0.1);  border: 1px solid rgba(245,158,11,0.3);  border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600; }
.level-tag-hr       { color: #a855f7; background: rgba(168,85,247,0.1);  border: 1px solid rgba(168,85,247,0.3);  border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600; }

/* Stats panel */
.stat-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
    margin: 4px;
}

.stat-number {
    font-size: 22px;
    font-weight: 700;
    color: #818cf8;
}

.stat-label {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}

/* Logo / Header */
.app-header {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.1));
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
}

/* Divider */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 20px 0;
}

/* Spinner color override */
.stSpinner > div {
    border-top-color: #6366f1 !important;
}

/* Alert styling */
.stAlert {
    border-radius: 10px !important;
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
}

/* Welcome screen */
.welcome-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    margin: 20px 0;
}

.demo-user-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    margin: 6px 0;
    border: 1px solid rgba(255,255,255,0.06);
    cursor: pointer;
    transition: all 0.2s;
}

@keyframes fadeInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.typing-indicator {
    animation: pulse 1.5s infinite;
    color: #6366f1;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


# ─── Session state initialization ─────────────────────────────────────────────
def init_session():
    defaults = {
        "token": None,
        "username": None,
        "role": None,
        "messages": [],
        "total_queries": 0,
        "blocked_queries": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ─── API helpers ───────────────────────────────────────────────────────────────
def api_login(username: str, password: str) -> dict | None:
    try:
        r = requests.post(
            f"{BACKEND_URL}/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
        return {"error": r.json().get("detail", "Login failed")}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the API running on port 8000?"}
    except Exception as e:
        return {"error": str(e)}


def api_ask(question: str, token: str) -> dict | None:
    try:
        r = requests.post(
            f"{BACKEND_URL}/ask",
            json={"question": question},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()
        return {"error": r.json().get("detail", "Query failed")}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is the API running on port 8000?"}
    except Exception as e:
        return {"error": str(e)}


def logout():
    for key in ["token", "username", "role", "messages", "total_queries", "blocked_queries"]:
        st.session_state[key] = None if key in ["token","username","role"] else ([] if key == "messages" else 0)
    st.rerun()


# ─── UI Components ─────────────────────────────────────────────────────────────
def render_role_badge(role: str):
    cfg = ROLE_CONFIG.get(role, ROLE_CONFIG["public"])
    st.markdown(
        f"""<div class="role-badge" style="color:{cfg['color']};
            background:{cfg['bg']}; border-color:{cfg['border']};">
            {cfg['icon']} {cfg['label']}
        </div>
        <div style="font-size:11px; color:#64748b; margin-bottom:16px;">{cfg['desc']}</div>""",
        unsafe_allow_html=True,
    )


def render_source_chunk(src: dict, idx: int):
    level = src.get("access_level", "public")
    tag_class = f"level-tag-{level}"
    with st.expander(f"📄 Source {idx+1} — {src.get('source_file','unknown')}", expanded=False):
        st.markdown(
            f"""<span class="{tag_class}">{level.upper()}</span>
            <span class="source-chip">📁 {src.get('source_file','')}</span>
            <span class="source-chip">🆔 {src.get('chunk_id','')[:40]}</span>""",
            unsafe_allow_html=True,
        )
        st.markdown(f"> {src.get('text', '')}", unsafe_allow_html=False)


def render_message(msg: dict):
    role = msg["role"]
    content = msg["content"]
    timestamp = msg.get("timestamp", "")

    if role == "user":
        st.markdown(
            f"""<div class="user-bubble">
                <div class="bubble-header">You · {timestamp}</div>
                {content}
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        denied = msg.get("access_denied", False)
        extra_class = "access-denied" if denied else ""
        icon = "🚫" if denied else "🤖"
        chunks = msg.get("chunks_retrieved", 0)

        st.markdown(
            f"""<div class="assistant-bubble {extra_class}">
                <div class="bubble-header">{icon} RAG Copilot · {timestamp} · {chunks} chunks retrieved</div>
                {content}
            </div>""",
            unsafe_allow_html=True,
        )

        # Show sources if not denied
        if not denied and msg.get("sources"):
            with st.container():
                st.markdown(
                    f"<div style='font-size:12px;color:#64748b;margin:4px 40px 2px 0;'>🔍 {len(msg['sources'])} retrieved source(s):</div>",
                    unsafe_allow_html=True,
                )
                for i, src in enumerate(msg["sources"]):
                    render_source_chunk(src, i)


# ─── Login Page ────────────────────────────────────────────────────────────────
def render_login():
    st.markdown("""
    <div class="app-header">
        <h1 style="margin:0; font-size:26px; font-weight:700; color:#f1f5f9;">
            🔐 TechCorp RAG Copilot
        </h1>
        <p style="margin:4px 0 0 0; color:#64748b; font-size:14px;">
            Secure Enterprise Knowledge Assistant — Role-Based Access Control
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### Sign In")
        username = st.text_input("Username", placeholder="e.g. alice", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Password", key="login_pass")

        if st.button("Sign In →", key="login_btn"):
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Authenticating…"):
                    result = api_login(username.strip(), password.strip())

                if result and "error" not in result:
                    st.session_state.token = result["access_token"]
                    st.session_state.username = result["username"]
                    st.session_state.role = result["role"]
                    st.success(f"Welcome, {result['username']}! Role: {result['role'].upper()}")
                    st.rerun()
                else:
                    err = result.get("error", "Login failed") if result else "Connection error"
                    st.error(f"❌ {err}")

    with col2:
        st.markdown("### Demo Accounts")
        st.markdown("<div style='color:#64748b; font-size:12px; margin-bottom:12px;'>Click any account to autofill credentials:</div>", unsafe_allow_html=True)

        demo_accounts = [
            ("alice", "alice123", "public", "🌐", "#22c55e"),
            ("bob", "bob123", "employee", "👤", "#3b82f6"),
            ("carol", "carol123", "manager", "🏢", "#f59e0b"),
            ("dave", "dave123", "hr", "🔐", "#a855f7"),
        ]

        for uname, pwd, role, icon, color in demo_accounts:
            st.markdown(
                f"""<div class="demo-user-row">
                    <span style="font-size:18px;">{icon}</span>
                    <div>
                        <div style="font-weight:600; color:#e2e8f0; font-size:13px;">{uname} / {pwd}</div>
                        <div style="font-size:11px; color:{color}; text-transform:uppercase; letter-spacing:0.5px;">{role}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Architecture overview
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="welcome-card">
        <h3 style="color:#818cf8; margin:0 0 16px 0; font-size:16px;">🏗️ How It Works</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; text-align:left; max-width:600px; margin:0 auto;">
            <div>
                <div style="color:#22c55e; font-weight:600; font-size:13px;">🌐 PUBLIC</div>
                <div style="color:#64748b; font-size:12px;">Company handbook, FAQ</div>
            </div>
            <div>
                <div style="color:#3b82f6; font-weight:600; font-size:13px;">👤 EMPLOYEE</div>
                <div style="color:#64748b; font-size:12px;">Benefits, leave policy</div>
            </div>
            <div>
                <div style="color:#f59e0b; font-weight:600; font-size:13px;">🏢 MANAGER</div>
                <div style="color:#64748b; font-size:12px;">Roadmap, budgets</div>
            </div>
            <div>
                <div style="color:#a855f7; font-weight:600; font-size:13px;">🔐 HR</div>
                <div style="color:#64748b; font-size:12px;">Salary bands, headcount</div>
            </div>
        </div>
        <p style="color:#475569; font-size:12px; margin:16px 0 0 0;">
            RBAC filtering happens at the <strong style="color:#818cf8;">retrieval layer</strong> — 
            the LLM never sees documents outside your permission level.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─── Main Chat Page ────────────────────────────────────────────────────────────
def render_chat():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:16px 0 8px 0;">
            <div style="font-size:28px;">🔐</div>
            <div style="font-weight:700; color:#f1f5f9; font-size:16px;">RAG Copilot</div>
            <div style="color:#64748b; font-size:11px;">TechCorp Enterprise</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

        # User info
        st.markdown(f"**👋 {st.session_state.username}**")
        render_role_badge(st.session_state.role)

        # Stats
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px; color:#64748b; margin-bottom:8px;'>SESSION STATS</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                f"""<div class="stat-box">
                    <div class="stat-number">{st.session_state.total_queries}</div>
                    <div class="stat-label">Queries</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""<div class="stat-box">
                    <div class="stat-number" style="color:#ef4444;">{st.session_state.blocked_queries}</div>
                    <div class="stat-label">Blocked</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # Suggested questions
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px; color:#64748b; margin-bottom:8px;'>💡 TRY ASKING</div>", unsafe_allow_html=True)

        suggestions_by_role = {
            "public":   ["What is TechCorp's mission?", "Where are your offices?", "How do I report a concern?"],
            "employee": ["What health plans are offered?", "How many PTO days do I get?", "Explain the 401k match"],
            "manager":  ["What's on the Q3 roadmap?", "What is the engineering budget?", "What are the Q4 key metrics?"],
            "hr":       ["What are the IC-3 salary bands?", "How many hires are planned for H2?", "What is the attrition risk register?"],
        }

        for q in suggestions_by_role.get(st.session_state.role, []):
            if st.button(f"→ {q}", key=f"sug_{q[:20]}", use_container_width=True):
                st.session_state["_suggested_question"] = q
                st.rerun()

        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            logout()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.total_queries = 0
            st.session_state.blocked_queries = 0
            st.rerun()

    # Main area
    st.markdown("""
    <div class="app-header">
        <h1 style="margin:0; font-size:22px; font-weight:700; color:#f1f5f9;">
            🔐 Enterprise RAG Copilot
        </h1>
        <p style="margin:4px 0 0; color:#64748b; font-size:13px;">
            Ask questions about TechCorp — I'll answer only from documents you're authorized to see.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align:center; padding:60px 20px; color:#334155;">
                <div style="font-size:48px; margin-bottom:16px;">💬</div>
                <div style="font-size:16px; font-weight:500; color:#475569;">Start a conversation</div>
                <div style="font-size:13px; color:#334155; margin-top:8px;">
                    Ask me anything about TechCorp — try a suggested question from the sidebar!
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                render_message(msg)

    # Input bar
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

    # Handle suggested question pre-fill
    default_q = st.session_state.pop("_suggested_question", "")

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        question = st.text_area(
            label="",
            value=default_q,
            placeholder="Ask a question about TechCorp policies, benefits, roadmap, compensation…",
            height=80,
            key="chat_input",
            label_visibility="collapsed",
        )
    with col_btn:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        submit = st.button("Send ➤", key="send_btn")

    if submit and question.strip():
        ts = datetime.now().strftime("%H:%M")

        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": question.strip(),
            "timestamp": ts,
        })
        st.session_state.total_queries += 1

        # Call API
        with st.spinner("🤔 Retrieving and generating answer…"):
            result = api_ask(question.strip(), st.session_state.token)

        if result and "error" not in result:
            denied = result.get("access_denied", False)
            if denied:
                st.session_state.blocked_queries += 1

            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get("sources", []),
                "chunks_retrieved": result.get("chunks_retrieved", 0),
                "access_denied": denied,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
        else:
            err = result.get("error", "Unknown error") if result else "Connection error"
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Error: {err}",
                "sources": [],
                "chunks_retrieved": 0,
                "access_denied": False,
                "timestamp": datetime.now().strftime("%H:%M"),
            })

        st.rerun()


# ─── Router ────────────────────────────────────────────────────────────────────
if st.session_state.token:
    render_chat()
else:
    render_login()
