import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import chain

# Centered and styled main title using inline styles
st.markdown('''
    <style>
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
    </style>
''', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">KPI METRICS VIEW DASHBOARD</h1>', unsafe_allow_html=True)

filepath="closed_sales Data - Copy.xlsx"
sheet_name = "Closed Sales Data"
# Read the data with additional parameters
data = pd.read_excel(filepath, sheet_name=sheet_name)

# Identify the index of the last relevant row containing "REM LIMITED"
last_relevant_index = data[data['Client Name'] == 'REM LIMITED'].index[0]
df = data.iloc[:last_relevant_index + 1]

# Sidebar styling and logo
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content h2 {
        color: #007BFF; /* Change this color to your preferred title color */
        font-size: 1.5em;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-title {
        color: #e66c37;
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-header {
        color: #e66c37; /* Change this color to your preferred header color */
        font-size: 2.5em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar .sidebar-content .filter-multiselect {
        margin-bottom: 15px;
    }
    .sidebar .sidebar-content .logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar .sidebar-content .logo img {
        max-width: 80%;
        height: auto;
        border-radius: 50%;
    }
            
    </style>
    """, unsafe_allow_html=True)


# Ensure the 'Start Date' column is in datetime format if needed
df["START DATE"] = pd.to_datetime(df["START DATE"], errors='coerce')


# Get minimum and maximum dates for the date input
startDate = df["START DATE"].min()
endDate = df["START DATE"].max()

# Define CSS for the styled date input boxes
st.markdown("""
    <style>
    .date-input-box {
        border-radius: 10px;
        text-align: left;
        margin: 5px;
        font-size: 1.2em;
        font-weight: bold;
    }
    .date-input-title {
        font-size: 1.2em;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Create 2-column layout for date inputs
col1, col2 = st.columns(2)

# Function to display date input in styled boxes
def display_date_input(col, title, default_date, min_date, max_date):
    col.markdown(f"""
        <div class="date-input-box">
            <div class="date-input-title">{title}</div>
        </div>
        """, unsafe_allow_html=True)
    return col.date_input("", default_date, min_value=min_date, max_value=max_date)

# Display date inputs
with col1:
    date1 = pd.to_datetime(display_date_input(col1, "Start Date", startDate, startDate, endDate))

with col2:
    date2 = pd.to_datetime(display_date_input(col2, "End Date", endDate, startDate, endDate))

# Filter DataFrame based on the selected dates
df = df[(df["START DATE"] >= date1) & (df["START DATE"] <= date2)].copy()



# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Date Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted(df['Start Date Month'].dropna().unique()))
channel = st.sidebar.multiselect("Select Channel", options=df['Intermediary'].unique())
segment = st.sidebar.multiselect("Select Clent Segment", options=df['Client Segment'].unique())
cover = st.sidebar.multiselect("Select Cover Type", options=df['Cover Type'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())


# Filtered DataFrame
filtered_df = df

# Apply filters to the DataFrame
if year:
    filtered_df = filtered_df[filtered_df['Start Date Year'].isin(year)]
if month:
    filtered_df = filtered_df[filtered_df['Start Date Month'].isin(month)]
if channel:
    filtered_df = filtered_df[filtered_df['Intermediary'].isin(channel)]
if client_name:
    filtered_df = filtered_df[filtered_df['Client Name'].isin(client_name)]


# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if channel:
    filter_description += f"{', '.join(map(str, channel))} "
if month:
    filter_description += f"{', '.join(month)} "
if client_name:
    filter_description += f"{', '.join(client_name)} "
if not filter_description:
    filter_description = "All df"



if not filtered_df.empty:
     # Calculate metrics
    scaling_factor = 1_000_000  # For millions
    scaled = 1_000_000_000  # for billions

    total_clients = filtered_df["Client Name"].nunique()
    total_pre = filtered_df["Basic Premium"].sum()
    total_in_pre = filtered_df["Total insured Premium"].sum()
    total_lives = filtered_df["Total lives"].sum()
    total_mem = filtered_df["No. of Principal Member"].sum()
    total_dependents = filtered_df["Dependents"].sum()
    average_dep = filtered_df["Average Number of Dependents per Employee"].sum()
    average_pre = filtered_df["Average Premium per Principal Member"].sum()
    average_premium_per_life = filtered_df["Total insured Premium"].mean()
    gwp_average = total_clients * total_lives * average_premium_per_life

    dependency_ratio = total_dependents / total_mem



    # Scale the sums
    total_pre_scaled = total_pre / scaling_factor
    total_in_pre_scaled = total_in_pre / scaling_factor
    average_pre_scaled = average_pre/scaling_factor
    gwp_average_scaled = gwp_average/scaled

    # Create 4-column layout for metric cards# Define CSS for the styled boxes and tooltips
    st.markdown("""
        <style>
        .custom-subheader {
            color: #e66c37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .metric-box {
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin: 10px;
            font-size: 1.2em;
            font-weight: bold;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            border: 1px solid #ddd;
            position: relative;
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 1em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1.5em;
        }
        .tooltip {
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position the tooltip above the text */
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .tooltip::after {
            content: "";
            position: absolute;
            top: 100%; /* Arrow at the bottom */
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: #555 transparent transparent transparent;
        }
        .metric-box:hover .tooltip {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """, unsafe_allow_html=True)

    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value, tooltip_text):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                <div class="tooltip">{tooltip_text}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<h2 class="custom-subheader">For Closed Sales</h2>', unsafe_allow_html=True)    


    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    display_metric(col1, "Total Clients", total_clients, "The total number of clients.")
    display_metric(col2, "Total Basic Premium", f"RWF {total_pre_scaled:.0f} M", "The total basic premium in millions of RWF.")
    display_metric(col3, "Total Insured Premium", f"RWF {total_in_pre_scaled:.0f} M", "The total insured premium in millions of RWF.")
    display_metric(col4, "Total Lives", total_lives, "The total number of lives covered (Number of pricipal members + Dependents).")
    display_metric(col1, "Total Principal Members", total_mem, "The total number of principal members.")
    display_metric(col2, "Total Dependents", total_dependents, "The total number of dependents.")
    display_metric(col3, "Average Dependents Per Principal Member", f"{average_dep:.0f}", "The average number of dependents per principal member.")
    display_metric(col4, "Average Premium Per Principal Member", f"RWF {average_pre_scaled:.0f}M", "The average insured premium per principal member in millions of RWF.")
    display_metric(col1, "Average GWP", f"RWF {gwp_average_scaled:.0f} B", "The average Gross Written Premium in billions of RWF (total number of clients x total lives covered x average Premium per life")
    display_metric(col2, "Dependency Ratio", f"{dependency_ratio:.1f}", "The ratio of dependents to principal members. this shows that for every 8 dependents, there are 10 principal members ")


    st.markdown('<h2 class="custom-subheader">For Prospective Sales</h2>', unsafe_allow_html=True)    

    df_closed = pd.read_excel("sales Data.xlsx")
    filtered_df = df_closed

    total_clients = filtered_df["Employer group"].nunique()
    total_lives = filtered_df["Employee Size"].sum()
    total_in_val = filtered_df["RWF Value"].sum()
    average_pre_per_life = filtered_df["RWF Value"].mean()
    gwp_average = total_clients * total_lives * average_pre_per_life
    total_items = len(filtered_df)
    closed_items = len(filtered_df[filtered_df['Status'] == 'Closed 💪'])
    percentage_closed = (closed_items / total_items) * 100

    total_val_scaled = total_pre / scaling_factor
    average_pre_scaled = average_pre_per_life/scaling_factor
    gwp_average_scaled = gwp_average/scaled


    # Display metrics
    cols1, cols2, cols3 = st.columns(3)
    display_metric(cols1, "Total Clients", total_clients, "The total number of potential clients.")
    display_metric(cols2, "Total Premium", f"RWF {total_val_scaled:.0f} M", "The total expected premium in millions of RWF.")
    display_metric(cols3, "Estimated Lives Covered", total_lives, "The total number of lives covered depending on the employee size.")
    display_metric(cols1, "Average Estimated Premium", f"RWF {average_pre_scaled:.0f}M", "The average estimated premium per life in millions of RWF.")
    display_metric(cols2, "Average GWP", f"RWF {gwp_average_scaled:.0f} B", "The average Gross Written Premium in billions of RWF (total number of clients x total lives covered x average Premium per life")
    display_metric(cols3, "Percentage Closed", f"{percentage_closed : .1f} %", "The percentage of propective sales that have been closed.")



