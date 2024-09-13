import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
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

st.markdown('<h1 class="main-title">YTD PREMIUM DASHBOARD</h1>', unsafe_allow_html=True)

filepath="closed_sales Data.xlsx"
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
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())

# Filtered DataFrame
filtered_df = df

# Apply filters to the DataFrame
if year:
    filtered_df = filtered_df[filtered_df['Start Date Year'].isin(year)]
if month:
    filtered_df = filtered_df[filtered_df['Start Date Month'].isin(month)]
if segment:
    filtered_df = filtered_df[filtered_df['Client Segment'].isin(segment)]
if client_name:
    filtered_df = filtered_df[filtered_df['Client Name'].isin(client_name)]


# Determine the filter description
filter_description = ""
if year:
    filter_description += f"{', '.join(map(str, year))} "
if segment:
    filter_description += f"{', '.join(map(str, segment))} "
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

    # Scale the sums
    total_pre_scaled = total_pre / scaling_factor
    total_in_pre_scaled = total_in_pre / scaling_factor

    # Create 4-column layout for metric cards
    col1, col2 = st.columns(2)

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
    display_metric(col1, "Total Basic Premuim", f"RWF {total_pre_scaled:.0f}M")
    display_metric(col2, "Total Insured Premium", f"RWF {total_in_pre_scaled:.0f} M")
   
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

    df_sorted = filtered_df.sort_values(by='Basic Premium', ascending=False)

    # Get the top 10 rows by employee size
    top_employer_groups = df_sorted.head(10)

    with cols1:
        fig_employer_groups = go.Figure()

        fig_employer_groups.add_trace(go.Bar(
            x=top_employer_groups['Client Name'],
            y=top_employer_groups['Basic Premium'],
            marker=dict(color='#009DAE'),
            text=top_employer_groups["Basic Premium"].apply(lambda x: f"RWF {x / 1e6:.0f} M"),
            textposition='outside', 
            textfont=dict(color='black'),  
            hoverinfo='y+text'
        ))

        fig_employer_groups.update_layout(
            xaxis_title="Client Name",
            yaxis_title="Basic Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Top 10 Clients By Basic Premuim </h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_employer_groups, use_container_width=True)

    # Calculate the total insured premium by intermediary
    int_premiums = filtered_df.groupby("Intermediary")["Total insured Premium"].sum().reset_index()
    int_premiums.columns = ["Intermediary", "Total insured Premium"]

    

    with cols2:
        # Display the header
        st.markdown('<h2 class="custom-subheader">YTD Total Insured Premium by Channel</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Intermediary", values="Total insured Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True, height=200)

    ccl1, ccl2 =st.columns(2)

    with ccl1:
        with st.expander("Clients Basic Premuim Data"):
            st.write(df[['Client Name', 'Basic Premium']].style.background_gradient(cmap="YlOrBr"))
    with ccl2:
        with st.expander("Insured Premium by Channel Data"):
            st.write(df[['Total insured Premium', 'Intermediary']].style.background_gradient(cmap="YlOrBr"))

    cl1, cl2 =st.columns(2)

        # Calculate the total insured premium by client segment
    int_premiums = filtered_df.groupby("Client Segment")["Total insured Premium"].sum().reset_index()
    int_premiums.columns = ["Client Segment", "Total insured Premium"]

    with cl1:    
        # Display the header
        st.markdown('<h2 class="custom-subheader">YTD Total Insured Premium by Client Segment</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Client Segment", values="Total insured Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

# Define the correct order for the months
    month_order = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]

# Convert "Start Date Month" to a categorical type with the specified order
    filtered_df['Start Date Month'] = pd.Categorical(filtered_df['Start Date Month'], categories=month_order, ordered=True)

    # Group data by month and sum the Basic Premium
    monthly_premium = filtered_df.groupby('Start Date Month')['Basic Premium'].sum().reset_index()

    # Custom function to format the values
    def format_premium(value):
        return f"RWF {value / 1e6:.0f} M"

    # Apply the custom function to format the text
    monthly_premium['Formatted Premium'] = monthly_premium['Basic Premium'].apply(format_premium)
    with cl2:
        # Create the bar chart
        fig_monthly_premium = go.Figure()

        fig_monthly_premium.add_trace(go.Bar(
            x=monthly_premium['Start Date Month'],
            y=monthly_premium['Basic Premium'],
            marker=dict(color='#009DAE'),
            text=monthly_premium['Formatted Premium'],
            textposition='outside',
            textfont=dict(color='black'),
            hoverinfo='y+x'
        ))

        fig_monthly_premium.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Basic Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Basic Premium Monthly</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    ccls1, ccls2 =st.columns(2)

    with ccls2:
        with st.expander("Clients Insured Premuim Data"):
            st.write(df[['Client Name', 'Total insured Premium']].style.background_gradient(cmap="YlOrBr"))
    with ccls1:
        with st.expander("Insured Premium by Client Sement Data"):
            st.write(df[['Total insured Premium', 'Client Segment']].style.background_gradient(cmap="YlOrBr"))


    cls1, cls2 = st.columns(2)

    # Group data by "Start Date Month" and "Intermediary" and sum the Total Insured Premium
    monthly_premium = data.groupby(['Start Date Month', 'Intermediary'])['Total insured Premium'].sum().unstack().fillna(0)

    # Custom function to format the values
    def format_premium(value):
        return f"RWF {value / 1e6:.0f} M"

    # Apply the custom function to format the text
    monthly_premium['Formatted Premium'] = monthly_premium.sum(axis=1).apply(format_premium)

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]
    with cls1:
        # Create the stacked bar chart
        fig_monthly_premium = go.Figure()

        for idx, intermediary in enumerate(monthly_premium.columns[:-1]):  # Exclude the 'Formatted Premium' column
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_premium.index,
                y=monthly_premium[intermediary],
                name=intermediary,
                text=monthly_premium[intermediary].apply(lambda x: f"RWF {x / 1e6:.0f} M"),
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_monthly_premium.update_layout(
            barmode='stack',
            xaxis_title="Month",
            yaxis_title="Total Insured Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Insured Premium Monthly by Intermediary</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)
        
     # Group data by "Start Date Month" and "Client Segment" and sum the Total Insured Premium
    monthly_premium = data.groupby(['Start Date Month', 'Client Segment'])['Total insured Premium'].sum().unstack().fillna(0)

    # Custom function to format the values
    def format_premium(value):
        return f"RWF {value / 1e6:.0f} M"

    # Apply the custom function to format the text
    monthly_premium['Formatted Premium'] = monthly_premium.sum(axis=1).apply(format_premium)

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8", "#f8a785"]
    with cls2:
        # Create the stacked bar chart
        fig_monthly_premium = go.Figure()

        for idx, client_segment in enumerate(monthly_premium.columns[:-1]):  # Exclude the 'Formatted Premium' column
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_premium.index,
                y=monthly_premium[client_segment],
                name=client_segment,
                text=monthly_premium[client_segment].apply(lambda x: f"RWF {x / 1e6:.0f} M"),
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_monthly_premium.update_layout(
            barmode='stack',
            xaxis_title="Month",
            yaxis_title="Total Insured Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Insured Premium Monthly</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    clu1, clu2 =  st.columns(2)
 # Group by 'START DATE'
    date_total_premium = data.groupby('Start Date Month')['Total insured Premium'].sum().reset_index(name='Total Insured Premium')
    date_total_lives = data.groupby('Start Date Month')['Total lives'].sum().reset_index(name='Total lives')

    # Merge the premium and lives data
    merged_data = pd.merge(date_total_premium, date_total_lives, on='Start Date Month')

    with clu1:
        # Create the dual-axis chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Bar(x=merged_data['Start Date Month'], y=merged_data['Total Insured Premium'], name="Total Insured Premium", marker_color='#009DAE'),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=merged_data['Start Date Month'], y=merged_data['Total lives'], name="Total lives", line=dict(color='#ff7f0e')),
            secondary_y=True,
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Month")

        # Set y-axes titles
        fig.update_yaxes(title_text="Annual Premium in RWF", secondary_y=False)
        fig.update_yaxes(title_text="Lives Covered", secondary_y=True)

        st.markdown('<h2 class="custom-subheader">Total Premium By Total Lives</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    # Group by 'Client'
    client_total_premium = data.groupby('Start Date Month')['Average Premium per Principal Member'].sum().reset_index(name='Average Premium per Principal Member')
    client_total_lives = data.groupby('Start Date Month')['No. of Principal Member'].sum().reset_index(name='No. of Principal Member')

    # Merge the premium and lives data
    merged_data = pd.merge(client_total_premium, client_total_lives, on='Start Date Month')

    with clu2:
        # Create the dual-axis chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Bar(x=merged_data['Start Date Month'], y=merged_data['Average Premium per Principal Member'], name="Average Premium per Principal Member", marker_color='#009DAE'),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=merged_data['Start Date Month'], y=merged_data['No. of Principal Member'], name="No. of Principal Member", line=dict(color='#ff7f0e')),
            secondary_y=True,
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Month")

        # Set y-axes titles
        fig.update_yaxes(title_text="Average Premium per Principal Member", secondary_y=False)
        fig.update_yaxes(title_text="No. of Principal Member", secondary_y=True)
    
        st.markdown('<h2 class="custom-subheader">Average Premium By Principal Member</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
                

    # Group by day and sum the values
    area_chart_basic_premium = filtered_df.groupby(filtered_df["START DATE"].dt.strftime("%Y-%m-%d"))['Basic Premium'].sum().reset_index(name='Total Basic Premium')
    area_chart_total_insured = filtered_df.groupby(filtered_df["START DATE"].dt.strftime("%Y-%m-%d"))['Total insured Premium'].sum().reset_index(name='Total Insured Premium')

    # Merge the basic premium and total insured premium data
    area_chart = pd.merge(area_chart_basic_premium, area_chart_total_insured, on='START DATE')

    # Sort by the START DATE
    area_chart = area_chart.sort_values("START DATE")

    # Create the dual-axis area chart
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig2.add_trace(
        go.Scatter(x=area_chart['START DATE'], y=area_chart['Total Basic Premium'], name="Basic Premium", fill='tozeroy', line=dict(color='#e66c37')),
        secondary_y=False,
    )

    fig2.add_trace(
        go.Scatter(x=area_chart['START DATE'], y=area_chart['Total Insured Premium'], name="Total Insured Premium", fill='tozeroy', line=dict(color='#009DAE')),
        secondary_y=True,
    )

    # Set x-axis title
    fig2.update_xaxes(title_text="Date", tickangle=45)  # Rotate x-axis labels to 45 degrees for better readability

    # Set y-axes titles
    fig2.update_yaxes(title_text="<b>Basic Premium</b>", secondary_y=False)
    fig2.update_yaxes(title_text="<b>Total Insured Premium</b>", secondary_y=True)

    st.markdown('<h2 class="custom-subheader">Basic Premium and Total Insured Premium Over Time</h2>', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<h3 class="custom-subheader">Month-Wise Insured Premium By Client Segment Table</h2>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=filtered_df,
            values="Total insured Premium",
            index=["Client Segment"],
            columns="Start Date Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
        
else:
    st.error("No data available for this selection")