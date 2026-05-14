import streamlit as st
import mysql.connector

# --- ALL BACKEND FUNCTIONS ---
# --- ALL BACKEND FUNCTIONS (OPTIMIZED) ---

@st.cache_resource(ttl=600)
def connect_db():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=int(st.secrets["mysql"]["port"]),
            autocommit=True
        )
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def get_active_conn():
    conn = connect_db()
    # Agar connection band ho gaya ho, toh cache clear karke naya banaye
    if conn is None or not conn.is_connected():
        st.cache_resource.clear()
        return connect_db()
    return conn

@st.cache_data
def get_all_streams():
    try:
        conn = get_active_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM streams")
        data = cursor.fetchall()
        cursor.close()
        return data
    except Exception as e:
        st.error(f"Streams fetching error: {e}")
        return []

@st.cache_data
def get_jobs_by_stream(s_id):
    try:
        conn = get_active_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_roles WHERE stream_id = %s", (s_id,))
        data = cursor.fetchall()
        cursor.close()
        return data
    except Exception as e:
        st.error(f"Jobs fetching error: {e}")
        return []

@st.cache_data
def get_resources_by_roles(job_id):
    try:
        conn = get_active_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT job_id, name, title, link, difficulty, access_type, description, res_id FROM resources WHERE job_id = %s", (job_id,))
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        st.error(f"Resources fetching error: {e}")
        return []

@st.cache_data
def get_job_roadmap(job_id):
    try:
        conn = get_active_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT step_order, step_name, duration, description FROM job_roadmaps WHERE job_id = %s ORDER BY step_order ASC", (job_id,))
        roadmap = cursor.fetchall()
        cursor.close()
        return roadmap
    except Exception as e:
        return []

def log_user_activity(selection_name):
    try:
        conn = get_active_conn()
        cursor = conn.cursor()
        query = "INSERT INTO analytics (search_query) VALUES (%s)"
        cursor.execute(query, (selection_name,))
        # Caching nahi hai isliye yahan commit zaroori hai (autocommit=True handle kar lega fir bhi)
        cursor.close()
    except Exception as e:
        print(f"Logging error: {e}")

# --- PAGE CONFIG & UI DESIGN ---
st.set_page_config(page_title="skillscript", page_icon="🚀")

# --- SIDEBAR ---
with st.sidebar:

    st.markdown("## 🧭 Navigator's Hub")
    st.markdown("<p style='color: #00dbde; font-weight: bold; font-style: italic; font-size: 16px;'> \"Where passion meets profession: Map your future with us.\" </p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🌐 About skillscript")
    st.info("""
        An **interactive ecosystem** designed to simplify professional choices. We provide clear roadmaps for every student's success.
    """)
    
    # Key Highlights
    st.markdown("""
    **Core Features:**
    * 📂 **110+** High-demand job roles.
    * 🎓 **Verified** Learning resources.
    * 🗺️ **Step-by-Step** Career roadmaps.
    """)

    st.divider()

    # Section: Guide
    with st.expander("📖 Quick Start Guide"):
        st.write("""
        1. **Search** for a role or **Select** a stream.
        2. **Explore** the list of specialized jobs.
        3. **Click** to expand for resources & links.
        """)

    # Section: Contact & Footer
    st.divider()
    st.markdown("### ✉️ Contact Us")
    st.link_button("🌐 Connect on LinkedIn", "https://www.linkedin.com/in/naitik-tripathi-97b5b13a7/")
    
    st.write("") # Spacer
    st.caption("© 2026 skillscript | v2.0")

# Custom CSS - GITHUB THEME & ANIMATIONS
st.markdown("""
    <style>
    /* GitHub-Inspired Deep Dark Background */
    .stApp {
        background-color: #0d1117;
    }
    
    /* Animation for the "Slide Up" effect */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Roadmap Card Styling (Terminal Window Look) */
    .roadmap-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
        animation: fadeInUp 0.6s ease-out;
        transition: border-color 0.3s ease, transform 0.2s ease;
    }

    .roadmap-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }

    h1 {
        background: linear-gradient(to right, #58a6ff, #bc8cf2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 800;
    }
    
    .terminal-dots {
        color: #8b949e;
        font-size: 14px;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🚀 skillscript</h1>", unsafe_allow_html=True)

# --- SMART SEARCH CONFIG ---
aliases = {
    "ca": "Chartered Accountant",
    "cs": "Company Secretary",
    "cma": "Cost & Management Accountant",
    "hr": "Human Resource (HR) Specialist",
    "it": "Information Technology"
}

# --- UI HELPER FOR ROADMAP + RESOURCES ---
def display_career_details(job_id, job_name):
    # Part A: Roadmap Section (GitHub UI Style)
    roadmap = get_job_roadmap(job_id)
    if roadmap:
        st.markdown(f"#### 🧭 {job_name} Career Journey")
        for step in roadmap:
            st.markdown(f"""
                <div class="roadmap-card">
                    <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; margin-bottom: 12px; padding-bottom: 5px;'>
                        <span style='color: #58a6ff; font-family: monospace; font-weight: bold;'>STEP_{step[0]:02d}</span>
                        <div class="terminal-dots">● ● ●</div>
                    </div>
                    <h5 style='color: #f0f6fc; margin: 0; font-size: 18px;'>{step[1]}</h5>
                    <div style='margin: 8px 0;'>
                        <span style='background-color: rgba(188, 140, 242, 0.15); color: #bc8cf2; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;'>⏳ {step[2]}</span>
                    </div>
                    <p style='color: #8b949e; font-size: 14px; line-height: 1.6; margin: 0;'>{step[3]}</p>
                </div>
            """, unsafe_allow_html=True)
        st.divider()

    # Part B: Resources Section
    st.markdown(f"#### 📚 Learning Resources")
    resources = get_resources_by_roles(job_id)
    if resources:
        for res in resources:
            st.markdown(f"### {res[2]}")
            st.markdown(f"**Level:** `{res[4]}` | **Type:** `{res[5]}`")
            st.info(res[6])
            if res[3]: st.link_button(f"👉 Go to {res[2]}", res[3])
    else:
        st.info("Resources added soon!")

# --- APP LOGIC: SEARCH & STREAM HANDLING ---

# Search Input
# --- APP LOGIC: SEARCH & STREAM HANDLING (FIXED) ---

# Search Input
search_query = st.text_input("🔍 Direct Career Search:", placeholder="e.g. CA, Data Analyst, Web Developer...")

is_searching = False

if search_query.strip():
    is_searching = True
    input_term = search_query.strip().lower()
    
    # Convert short forms (CA -> Chartered Accountant)
    search_term = aliases.get(input_term, input_term)
    
    try:
        # Naya active connection logic
        conn = get_active_conn()
        cursor = conn.cursor()
        
        query = """
            SELECT job_id, job_name FROM job_roles 
            WHERE job_name LIKE %s 
            ORDER BY (job_name = %s) DESC, job_id ASC
            LIMIT 1
        """
        param = (f"%{search_term}%", search_term)
        
        cursor.execute(query, param)
        result = cursor.fetchone()
        cursor.close() # Sirf cursor close karo, connection nahi

        if result:
            st.write(f"Showing best match for: **{search_query.upper()}**")
            job_id, job_name = result[0], result[1]
            
            with st.expander(f"🎯 {job_name}", expanded=True):
                display_career_details(job_id, job_name)
            
            st.divider()
            st.info("💡 **Tip:** Explore more options by clearing the search and checking 'Streams' below!")
        else:
            st.warning(f"Information regarding '{search_query}' is currently unavailable in our database.")
            is_searching = False 

    except Exception as e:
        st.error(f"Search error: {e}")

# --- SHOW STREAMS ONLY IF NOT SEARCHING ---
if not is_searching:
    st.write("---")
    streams = get_all_streams()
    if streams:
        stream_options = {s[1]: s[0] for s in streams}
        selected_stream = st.selectbox("Or choose by stream for a detailed roadmap:", ["Select"] + list(stream_options.keys()))

        if selected_stream != "Select":
            log_user_activity(selected_stream)
            s_id = stream_options[selected_stream]
            jobs = get_jobs_by_stream(s_id)
            
            st.subheader(f"🎯 Top Careers in {selected_stream}")
            if not jobs:
                st.info("Is stream ke liye jobs update ho rahi hain!")
            
            for job in jobs:
                with st.expander(f"💼 {job[2]}"):
                    display_career_details(job[0], job[2])
    else:
        st.warning("Database se connect nahi ho paya.")
