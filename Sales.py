import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from itertools import chain


# SIDEBAR FILTER
logo_url = 'EC_logo (2).png'  
st.sidebar.image(logo_url, use_column_width=True)
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

st.markdown('<h1 class="main-title">SALES DASHBOARD</h1>', unsafe_allow_html=True)

df = pd.read_excel('sales Data.xlsx')
# Ensure 'created_time' is a datetime object
df['created_time'] = pd.to_datetime(df['created_time'])

# Drop all rows that have a duplicated value in the 'Employer group' column
df = df.drop_duplicates(subset='Employer group', keep="first")

# Get minimum and maximum dates for the date input
startDate = df["created_time"].min()
endDate = df["created_time"].max()

# Create 2-column layout for date inputs
col1, col2 = st.columns(2)

# Function to display date input in styled boxes
def display_date_input(col, title, default_date, min_date, max_date, key):
    col.markdown(f"""
        <div style="border-radius: 10px; text-align: left; margin: 5px;">
            <div style="font-size: 1.2em; margin-bottom: 5px; font-weight: bold;">{title}</div>
        </div>
        """, unsafe_allow_html=True)
    return col.date_input("", default_date, min_value=min_date, max_value=max_date, key=key)

# Display date inputs
with col1:
    date1 = display_date_input(col1, "Start Date", startDate, startDate, endDate, key="start_date")

with col2:
    date2 = display_date_input(col2, "End Date", endDate, startDate, endDate, key="end_date")

# Convert dates from Streamlit date_input to datetime
date1 = pd.to_datetime(date1).tz_localize('UTC')
date2 = pd.to_datetime(date2).tz_localize('UTC')

# Filter the DataFrame based on the selected date range
df_filtered = df[(df["created_time"] >= date1) & (df["created_time"] <= date2)].copy()

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

# Extract additional columns for filtering
df_filtered['year'] = df_filtered['created_time'].dt.year
df_filtered['MonthName'] = df_filtered['created_time'].dt.strftime('%B')
df_filtered['Client Segment'] = df_filtered['Client Segment'].astype(str)
df_filtered['Engagement'] = df_filtered['Engagement'].astype(str)
df_filtered['Employer group'] = df_filtered['Employer group'].astype(str)



# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df_filtered['year'].unique()))
month = st.sidebar.multiselect("Select Month", options=sorted(df_filtered['MonthName'].unique()))
client_type = st.sidebar.multiselect("Select Client Type", options=sorted(df_filtered['Client Segment'].unique()))
eng_type = st.sidebar.multiselect("Select Engagement Type", options=sorted(df_filtered['Engagement'].unique()))
em_group = st.sidebar.multiselect("Select Employer group", options=sorted(df_filtered['Employer group'].unique()))

## Filter by year
if year:
    df = df[df['year'].isin(year)]

# Filter by client type
if client_type:
    df = df[df['Client Segment'].isin(client_type)]

# Filter by month
if month:
    df = df[df['MonthName'].isin(month)]

# Filter by engagement type
if eng_type:
    df = df[df['Engagement'].isin(eng_type)]
if em_group:
    df = df[df['Employer group'].isin(em_group)]

filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if client_type:
    filter_description += f"{', '.join(map(str, client_type))} "
if month:
    filter_description += f"{', '.join(month)} "
if eng_type:
    filter_description += f"{', '.join(eng_type)} "
if not filter_description:
    filter_description = "All Data"

if not df.empty:

    scaling_factor = 1_000_000 

    # Calculate metrics
    em_group = df["Employer group"].count()
    em_size = df["Employee Size"].sum()
    amount = df["RWF Value"].sum()

    tot_amount= amount/scaling_factor
    # Create 3-column layout for metric cards
    col1, col2, col3 = st.columns(3)

    
    # Define CSS for the styled boxes
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
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 2em;
        }
        </style>
        """, unsafe_allow_html=True)

 # Function to display metrics in styled boxes
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    # Display metrics
    display_metric(col1, "Total employer group", f"{em_group:.0f}")
    display_metric(col2, "Number of Employees", f"{em_size:.0f}")
    display_metric(col3, "Total Amount", f"RWF {tot_amount:.0f}M")


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

    cols1, cols2 = st.columns(2)

    df_sorted = df.sort_values(by='Employee Size', ascending=False)

    # Get the top 10 rows by employee size
    top_employer_groups = df_sorted.head(15)

    with cols1:
        fig_employer_groups = go.Figure()

        fig_employer_groups.add_trace(go.Bar(
            x=top_employer_groups['Employer group'],
            y=top_employer_groups['Employee Size'],
            marker=dict(color='#009DAE'),
            text=top_employer_groups['Employee Size'],
            textposition='outside', 
            textfont=dict(color='black'),  
            hoverinfo='y+text'
        ))

        fig_employer_groups.update_layout(
            xaxis_title="Employer Group",
            yaxis_title="Employee Size",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Top 15 Employer Groups by Employee Size</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_employer_groups, use_container_width=True)

        # Count occurrences of each client segment
    client_segment_counts = df['Client Segment'].value_counts().reset_index()
    client_segment_counts.columns = ['Client Segment', 'Count']

    with cols2:
        st.markdown('<h2 class="custom-subheader">Client Segments Distribution</h2>', unsafe_allow_html=True)
        
        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]
        
        # Create a pie chart
        fig = px.pie(client_segment_counts, names="Client Segment", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='outside', textinfo='percent+label')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))
        
        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True, height=200)

    cl1, cl2 = st.columns(2)
    with cl1:
        with st.expander("Top 10 Employer Groups Data"):
            st.write(df_sorted[['Employer group', 'Employee Size']].style.background_gradient(cmap="YlOrBr"))

    with cl2:
        with st.expander("Client Segment Data"):
            st.write(client_segment_counts.style.background_gradient(cmap="YlOrBr"))
    

    cls1, cls2 = st.columns(2)
    with cls1:
        # Count the occurrences of each engagement type
        engagement_counts = df['Engagement'].value_counts().reset_index()
        engagement_counts.columns = ['Engagement', 'Count']

        # Display the header
        st.markdown('<h2 class="custom-subheader">Engagement Type Distribution</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(engagement_counts, names="Engagement", values="Count", template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='outside', textinfo='percent+label')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        with cls2:
            # Sort the DataFrame by 'RWF Value' in descending order and select the top 15 employer groups
            top_15_employer_groups = df.nlargest(15, 'RWF Value')

            # Streamlit app
            st.markdown('<h2 class="custom-subheader">Top 15 Employer Groups by RWF Value</h2>', unsafe_allow_html=True)
            custom_colors = ["#009DAE"]  # Replace with your desired colors

            # Create the bar chart with custom colors
            fig = px.bar(top_15_employer_groups, x="Employer group", y="RWF Value", template="seaborn", color_discrete_sequence=custom_colors)
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400, xaxis_title="Employer Group", yaxis_title="RWF Value")  # Adjust the height as needed

            st.plotly_chart(fig, use_container_width=True)

    ccl1, ccl2 = st.columns(2)
    with ccl2:
        with st.expander("Employer Groups' Monetary Value Data"):
            st.write(df[['Employer group', 'RWF Value']].style.background_gradient(cmap="YlOrBr"))

    with ccl1:
        with st.expander("Engagement Type Data"):
            st.write(engagement_counts.style.background_gradient(cmap="YlOrBr"))

        # Count values for Priority and Status
    priority_counts = df['Priority'].value_counts().reset_index()
    priority_counts.columns = ['Priority', 'Count']

    status_counts = df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

    # Create Streamlit columns
    clus1, clus2 = st.columns(2)

    with clus1:
        st.markdown('<h2 class="custom-subheader">Priority Distribution</h2>', unsafe_allow_html=True)
        
        # Create a pie chart for Priority
        fig_priority = px.pie(priority_counts, names="Priority", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig_priority.update_traces(textposition='outside', textinfo='percent+label')
        fig_priority.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))
        
        # Display the chart in Streamlit
        st.plotly_chart(fig_priority, use_container_width=True, height=200)

    with clus2:
        st.markdown('<h2 class="custom-subheader">Status Distribution</h2>', unsafe_allow_html=True)
        
        # Create a pie chart for Status
        fig_status = px.pie(status_counts, names="Status", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig_status.update_traces(textposition='outside', textinfo='percent+label')
        fig_status.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))
        
        # Display the chart in Streamlit
        st.plotly_chart(fig_status, use_container_width=True, height=200)

    ccl1, ccl2 = st.columns(2)
    with ccl2:
        with st.expander("Priority Data"):
            st.write(df[['Employer group', 'Priority']].style.background_gradient(cmap="YlOrBr"))

    with ccl1:
        with st.expander("Status Data"):
            st.write(status_counts.style.background_gradient(cmap="YlOrBr"))

    # Count values for Product
    product_counts = df['Product'].value_counts().reset_index()
    product_counts.columns = ['Product', 'Count']

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

    # Create Streamlit columns
    colus1, colus2 = st.columns(2)

    with colus1:
        st.markdown('<h2 class="custom-subheader">Product Type</h2>', unsafe_allow_html=True)
        
        # Create a pie chart for Product
        fig_product = px.pie(product_counts, names="Product", values="Count", template="plotly_dark", color_discrete_sequence=custom_colors)
        fig_product.update_traces(textposition='outside', textinfo='percent+label')
        fig_product.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))
        
        # Display the chart in Streamlit
        st.plotly_chart(fig_product, use_container_width=True, height=200)
        

        with st.expander("Product Type Data"):
            st.write(product_counts.style.background_gradient(cmap="YlOrBr"))
