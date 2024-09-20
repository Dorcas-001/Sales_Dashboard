
import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Eden Care Sales Dashboard",
    page_icon=Image.open("logo.png"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# SIDEBAR FILTER
logo_url = 'EC_logo.png'  
st.sidebar.image(logo_url, use_column_width=True)

page = st.sidebar.selectbox("Choose a dashboard", ["Home", "Overview Metric View", "Channel View"])

st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #013220;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #013220;
        color: white;
    }
    .main-title {
        color: #e66c37; /* Title color */
        text-align: center; /* Center align the title */
        font-size: 3rem; /* Title font size */
        font-weight: bold; /* Title font weight */
        margin-bottom: .5rem; /* Space below the title */
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1); /* Subtle text shadow */
    }
    div.block-container {
        padding-top: 2rem; /* Padding for main content */
    }
    .subheader {
        color: #e66c37;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        padding: 10px;
        border-radius: 5px;
        display: inline-block;
    }
    .section-title {
        font-size: 1.75rem;
        color: #004d99;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
    }
    .text {
        font-size: 1.1rem;
        color: #333;
        padding: 10px;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .nav-item {
        font-size: 1.2rem;
        color: #004d99;
        margin-bottom: 0.5rem;
    }
    .separator {
        margin: 2rem 0;
        border-bottom: 2px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if page == "Home":
    st.markdown('<h1 class="main-title">EDEN CARE SALES DASHBOARD</h1>', unsafe_allow_html=True)
    st.image("image.png", caption='Eden Care Medical', use_column_width=True)
    st.markdown('<h2 class="subheader">Welcome to the Eden Care Sales Dashboard</h2>', unsafe_allow_html=True)
    
    # Introduction
    st.markdown('<div class="text">Welcome to the Sales Dashboard! This comprehensive tool provides a clear and insightful overview of our sales performance across three key areas: <strong>Closed Sales, Lives, and Prospective Sales </strong>. The <strong>Closed Sales dashboard</strong> details successful deals and revenue generated, helping identify trends and high-performing teams. The <strong>Lives Dashboard</strong> tracks the number of individuals covered under our plans, offering insights into our market reach and effectiveness. The <strong>Prospective Sales</strong> section monitors potential sales opportunities, aiding in lead prioritization and resource allocation. Together, these dashboards enable stakeholders to make informed decisions, optimize strategies, and drive business success.</div>', unsafe_allow_html=True)
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    # User Instructions
    st.markdown('<h2 class="subheader">User Instructions</h2>', unsafe_allow_html=True)
    st.markdown('<div class="text">1. <strong>Navigation:</strong> Use the menu on the left to navigate between visits, claims and Preauthorisation dashboards.</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">2. <strong>Filters:</strong> Apply filters on the left side of each page to customize the data view.</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">3. <strong>Manage visuals:</strong> Hover over the visuals and use the options on the top right corner of each visual to download zoom or view on fullscreen</div>', unsafe_allow_html=True)
    st.markdown('<div class="text">3. <strong>Manage Table:</strong> click on the dropdown icon (<img src="https://img.icons8.com/ios-glyphs/30/000000/expand-arrow.png"/>) on table below each visual to get a full view of the table data and use the options on the top right corner of each table to download or search and view on fullscreen.</div>', unsafe_allow_html=True)    
    st.markdown('<div class="text">4. <strong>Refresh Data:</strong> The data will be manually refreshed on the last week of every quarter. </div>', unsafe_allow_html=True)
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

    

elif page == "Overview Metric View":
    exec(open("overview.py").read())
elif page == "Channel View":
    exec(open("intermediary.py").read())