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

st.markdown('<h1 class="main-title">CHANNEL VIEW DASHBOARD</h1>', unsafe_allow_html=True)

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



# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Date Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted(df['Start Date Month'].dropna().unique()))
channel = st.sidebar.multiselect("Select Channel", options=df['Intermediary'].unique())
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

    total_pre = filtered_df["Basic Premium"].sum()
    total_in_pre = filtered_df["Total insured Premium"].sum()
    total_lives = filtered_df["Total lives"].sum()
    average_premium_per_life = filtered_df["Total insured Premium"].mean()


    # Scale the sums
    total_pre_scaled = total_pre / scaling_factor
    total_in_pre_scaled = total_in_pre / scaling_factor
    average_pre_scaled = average_premium_per_life/scaling_factor

    # Create 4-column layout for metric cards
    col1, col2, col3, col4 = st.columns(4)

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
            font-size: 1em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1.2em;
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
    display_metric(col1, "Total Basic Premuim", f"RWF {total_pre_scaled:.0f}M")
    display_metric(col2, "Total Insured Premium", f"RWF {total_in_pre_scaled:.0f} M")
    display_metric(col3, "Total Lives", total_lives)
    display_metric(col4, "Average Premium Per Principal Member", f"RWF {average_pre_scaled:.0f}M")



   
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

    cols1,cols2 = st.columns(2)

    # Group data by "Start Date Year" and "Intermediary" and calculate the average Total Insured Premium
    yearly_avg_premium = filtered_df.groupby(['Start Date Year', 'Intermediary'])['Total insured Premium'].mean().unstack().fillna(0)

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

    with cols1:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, intermediary in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[intermediary],
                name=intermediary,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Date Year",
            yaxis_title="Average Insured Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Average Insured Premium Yearly by Channel</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    # Calculate the total insured premium by intermediary
    int_premiums = filtered_df.groupby("Intermediary")["Total insured Premium"].sum().reset_index()
    int_premiums.columns = ["Intermediary", "Total insured Premium"]    

    with cols2:
        # Display the header
        st.markdown('<h2 class="custom-subheader">Total Insured Premium by Channel</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Intermediary", values="Total insured Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
   
    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Yearly Average Insured Premium by Intermediary"):
            st.dataframe(yearly_avg_premium.style.format(precision=2))
        

    with ccl2:
        with st.expander("Total Insured Premium by Intermediary"):
            st.dataframe(int_premiums.style.format(precision=2))


    cls1, cls2 = st.columns(2)
    # Group data by "Start Date Month" and "Intermediary" and sum the Total Insured Premium
    monthly_premium = filtered_df.groupby(['Start Date Month', 'Intermediary'])['Total insured Premium'].sum().unstack().fillna(0)

    # Group data by "Start Date Month" and sum the Total Lives
    monthly_lives = filtered_df.groupby(['Start Date Month'])['Total lives'].sum()

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

    with cls1:
        # Create the grouped bar chart
        fig_monthly_premium = go.Figure()

        for idx, intermediary in enumerate(monthly_premium.columns):
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_premium.index,
                y=monthly_premium[intermediary],
                name=intermediary,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Add a line chart to show the trend of total lives over time
        fig_monthly_premium.add_trace(go.Scatter(
            x=monthly_lives.index,
            y=monthly_lives,
            mode='lines+markers',
            name='Total Lives Trend',
            line=dict(color='red', width=2),
            marker=dict(size=6, symbol='circle', color='red'),
            yaxis='y2'
        ))

        fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Date",
            yaxis_title="Total Insured Premium",
            yaxis2=dict(
                title='Total Lives',
                overlaying='y',
                side='right',
                showgrid=False,
                tickfont=dict(color='gray'),
                titlefont=dict(color='gray')
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Insured Premium Monthly by Channel</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)
        

    # Group by Client Name and Intermediary, then sum the Total Insured Premium
    df_grouped = filtered_df.groupby(['Client Name', 'Intermediary'])['Total insured Premium'].sum().reset_index()

    # Get the top 10 clients by Total Insured Premium
    top_10_clients = df_grouped.groupby('Client Name')['Total insured Premium'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Client Name'].isin(top_10_clients['Client Name'])]

    with cls2:
        # Create the bar chart
        fig = go.Figure()

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

        # Add bars for each intermediary
        for idx, intermediary in enumerate(client_df['Intermediary'].unique()):
            intermediary_data = client_df[client_df['Intermediary'] == intermediary]
            fig.add_trace(go.Bar(
                x=intermediary_data['Client Name'],
                y=intermediary_data['Total insured Premium'],
                name=intermediary,
                text=[f'{value/1e6:.0f}M' for value in intermediary_data['Total insured Premium']],
                textposition='auto',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig.update_layout(
            barmode='stack',
            yaxis_title="Total Insured Premium",
            xaxis_title="Client Name",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Top 10 Client Premium by Channel</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    clm1, clm2 = st.columns(2)

    with clm1:
        # Create an expandable section for the table
        with st.expander("View Detailed Monthly Total Insured Premium by Intermediary"):
            st.dataframe(monthly_premium.style.format(precision=2))

    with clm2:
        with st.expander("Client Premium by Intermediary"):
            st.write(df[['Client Name', 'Intermediary', 'Total insured Premium']].style.background_gradient(cmap="YlOrBr"))
    # Group by day and intermediary, then sum the Total Insured Premium
    line_chart_total_insured = filtered_df.groupby([df["START DATE"].dt.strftime("%Y-%m-%d"), 'Intermediary'])['Total insured Premium'].sum().reset_index(name='Total Insured Premium')

    # Sort by the START DATE
    line_chart_total_insured = line_chart_total_insured.sort_values("START DATE")

    custom_colors = ["#006E7F", "#e66c37", "red"]

    # Create the line chart
    fig2 = go.Figure()

    # Add traces for each intermediary with custom colors
    for i, intermediary in enumerate(line_chart_total_insured['Intermediary'].unique()):
        intermediary_data = line_chart_total_insured[line_chart_total_insured['Intermediary'] == intermediary]
        fig2.add_trace(
            go.Scatter(
                x=intermediary_data['START DATE'], 
                y=intermediary_data['Total Insured Premium'], 
                mode='lines+markers', 
                name=intermediary,
                line=dict(color=custom_colors[i % len(custom_colors)])  # Use custom colors
            )
        )

    # Set x-axis title
    fig2.update_xaxes(title_text="Date", tickangle=45)  

    # Set y-axis title
    fig2.update_yaxes(title_text="Total Insured Premium")

    # Set chart title and layout
    fig2.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Insured Premium",
        font=dict(color='Black'),
        margin=dict(l=0, r=0, t=30, b=50)
    )

    # Display the chart in Streamlit
    st.markdown('<h2 class="custom-subheader">Intermediary Trend vs Total Insured Premium Over Time</h2>', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)


    # summary table
    st.markdown('<h3 class="custom-subheader">Month-Wise Insured Premium By Client Segment Table</h2>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=filtered_df,
            values="Total insured Premium",
            index=["Intermediary"],
            columns="Start Date Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
    

        
else:
    st.error("No data available for this selection")