import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from master_workflow import master_workflow
import time

st.set_page_config(
    page_title="AutoAnalyze",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Main Container Styling */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        /* Increased padding-bottom to ensure content clears the chat input comfortably */
        padding-bottom: 12rem; 
    }
    
    /* Polished Header Text */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #b0b0b0;
        margin-bottom: 3rem;
    }

    /* Tab Layout Overhaul */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px; 
        justify-content: center; 
        margin-bottom: 2rem;
        border-bottom: 1px solid #303030; 
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 12px 24px;
        background-color: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        color: #8c8c8c;
        font-weight: 500;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #e0e0e0;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff;
        border-bottom-color: #ff4b4b; 
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    /* Adjust chat input position */
    .stChatInput {
        bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

def stream_text(text):
    for chunk in text.split(" "):
        for char in chunk + " ":
            yield char
            time.sleep(0.005)

st.title("🧠 AutoAnalyze")
st.markdown('<p class="header-subtitle">Your intelligent assistant for data exploration. Ask a question to unlock insights, interactive charts, and raw data reports.</p>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

user_prompt = st.chat_input("Ask something about your data, e.g., 'Show me sales over time'...")

if user_prompt:
    #display user message
    with st.chat_message("user"):
        st.write(user_prompt)

    #processing State
    with st.chat_message("assistant"):
        with st.status("Generating analysis...", expanded=False) as status:
            try:
                
                result = master_workflow.invoke({'user_prompt': user_prompt})
                
                #extracting results
                dfs = result.get('dfs', [])
                codes = result.get('plots', [])
                summary = result.get('summary', "No summary provided.")
                
                #store in session state for persistence
                st.session_state.last_result = {
                    "dfs": dfs,
                    "codes": codes,
                    "summary": summary
                }
                
                status.update(label="Analysis Complete!", state="complete")
                
            except Exception as e:
                status.update(label="Error Occurred", state="error")
                st.error(f"An error occurred during execution: {e}")
                st.stop()

if st.session_state.last_result:
    res = st.session_state.last_result
    
    tab1, tab2, tab3 = st.tabs(["📄 Key Insights", "📈 Visualizations", "💾 Source Data"])

    #tab 1: summary 
    with tab1:
        with st.container(border=True):
            st.subheader("Executive Summary")
            if user_prompt: 
                st.write_stream(stream_text(res['summary']))
            else:
                st.markdown(res['summary'])

    #tab 2: visualizations
    with tab2:
        if not res['codes']:
            st.info("No visualizations were generated for this query.", icon="ℹ️")
        
        for i, code in enumerate(res['codes']):
            try:
                with st.container(border=True):
                    st.subheader(f"Visualization {i+1}")
                    local_env = {}
                    global_env = {'dfs': res['dfs'], 'pd': pd, 'go': go}
                    
                    exec(code, global_env, local_env)
                    
                    if 'fig' in local_env:
                        st.plotly_chart(local_env['fig'], use_container_width=True, theme="streamlit")
                    else:
                        st.warning(f"Code block {i+1} ran but didn't create a 'fig' variable.")
                    
                    with st.expander(f"🔍 View Python Code for Plot {i+1}"):
                        st.code(code, language='python')
            except Exception as e:
                st.error(f"Could not render plot {i+1}. See details below.", icon="🚨")
                with st.expander("Error Details & Code"):
                    st.write(f"**Error:** {e}")
                    st.code(code, language='python')

    #tab3: dataframes
    with tab3:
        if not res['dfs']:
             st.info("No dataframes available for preview.", icon="ℹ️")
        
        for i, df in enumerate(res['dfs']):
            with st.container(border=True):
                st.subheader(f"Data Table {i+1}")
                st.caption(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
                st.dataframe(df, use_container_width=True, height=300)