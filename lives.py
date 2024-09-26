import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import chain
from matplotlib.ticker import FuncFormatter


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

st.markdown('<h1 class="main-title">LIVES COVERED VIEW</h1>', unsafe_allow_html=True)

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


# Dictionary to map month names to their order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}

df['Start Date Year'] = pd.to_numeric(df['Start Date Year'], errors='coerce').dropna().astype(int)
# Sort months based on their order
sorted_months = sorted(df['Start Date Month'].dropna().unique(), key=lambda x: month_order[x])


# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Date Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())

# Filtered DataFrame
filtered_df = df


# Create a 'Month-Year' column
filtered_df['Month-Year'] = filtered_df['Start Date Month'] + ' ' + filtered_df['Start Date Year'].astype(str)


# Function to sort month-year combinations
def sort_key(month_year):
    month, year = month_year.split()
    return (int(year), month_order[month])

# Extract unique month-year combinations and sort them
month_years = sorted(filtered_df['Month-Year'].unique(), key=sort_key)

# Select slider for month-year range
selected_month_year_range = st.select_slider(
    "Select Month-Year Range",
    options=month_years,
    value=(month_years[0], month_years[-1])
)

# Filter DataFrame based on selected month-year range
start_month_year, end_month_year = selected_month_year_range
start_month, start_year = start_month_year.split()
end_month, end_year = end_month_year.split()

start_index = (int(start_year), month_order[start_month])
end_index = (int(end_year), month_order[end_month])

# Filter DataFrame based on month-year order indices
filtered_df = filtered_df[
    filtered_df['Month-Year'].apply(lambda x: (int(x.split()[1]), month_order[x.split()[0]])).between(start_index, end_index)
]


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

    # Create 4-column layout for metric cards
    col1, col2, col3, col4 = st.columns(4)

    # Define CSS for the styled boxes
    st.markdown("""
        <style>
        .custom-subheader {
            color: #e66c37;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            padding: 5px;
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
            font-size: 0.9em;
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

     # Calculate metrics
    scaling_factor = 1_000_000  # For millions
    scaled = 1_000_000_000  # for billions

    total_clients = filtered_df["Client Name"].nunique()
    total_in_pre = filtered_df["Total Premium"].sum()
    total_lives = filtered_df["Total lives"].sum()
    total_mem = filtered_df["No. of Principal Member"].sum()
    total_dependents = filtered_df["Dependents"].sum()
    average_dep = filtered_df["Average Number of Dependents per Employee"].sum()
    average_pre = filtered_df["Average Premium per Principal Member"].sum()
    average_premium_per_life = filtered_df["Total Premium"].mean()
    gwp_average = total_clients * total_lives * average_premium_per_life

    dependency_ratio = total_dependents / total_mem



    # Scale the sums
    total_in_pre_scaled = total_in_pre / scaling_factor
    average_pre_scaled = average_pre/scaling_factor
    gwp_average_scaled = gwp_average/scaled

    scale = 1_000
    # Calculate the median premium per employer group
    grouped = filtered_df.groupby('Client Name')['Average Premium per Principal Member'].median().reset_index()
    grouped.columns = ['Client Name', 'Median Premium']
    # Calculate key metrics
    median_premium = (grouped['Median Premium'].median())/scale
    Q1 = (grouped['Median Premium'].quantile(0.25))/scale
    Q3 = (grouped['Median Premium'].quantile(0.75))/scale
    IQR = Q3 - Q1

    display_metric(col1, "Total Lives", total_lives)
    display_metric(col2, "Total Principal Members", total_mem)
    display_metric(col3, "Total Dependents", total_dependents)
    display_metric(col4, "Average Premium Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    display_metric(col1, "Average Dependents Per Principal Member", f"{average_dep:.0f}")
    display_metric(col2, "Dependency Ratio", f"{dependency_ratio:.1f}")
    display_metric(col3, "Median Premium", f"RWF {median_premium:.0f} K")
    display_metric(col4, "Interquartile Range (IQR)", f"RWF {IQR:.0f} K")



    

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

    cul1, cul2 =st.columns(2)
# Group by day and intermediary, then sum the Total Premium
    area_chart_total_insured = filtered_df.groupby([filtered_df["START DATE"].dt.strftime("%Y-%m-%d"), 'Cover Type'])['Total lives'].sum().reset_index(name='Total lives')

    # Sort by the START DATE
    area_chart_total_insured = area_chart_total_insured.sort_values("START DATE")

    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]
    with cul1:
        # Set the figure size to a height of 450
        fig1, ax1 = plt.subplots(figsize=(10, 9))  # Adjust the width and height as needed

        # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='START DATE', columns='Cover Type', values='Total lives').fillna(0)
            
        # Plot the stacked area chart
        pivot_df_insured.plot(kind='area', stacked=True, ax=ax1, color=custom_colors[:len(pivot_df_insured.columns)])

        # Remove the border around the chart
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        # Set x-axis title
        ax1.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

        # Set y-axis title
        ax1.set_ylabel("Total Lives Covered", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

        # Set chart title
        st.markdown('<h2 class="custom-subheader">Total Lives Covered by Cover Type over Time</h2>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig1)


    # Group data by "Start Date Month" and calculate the total number of Principal Members and Dependents
    yearly_totals = filtered_df.groupby(['Start Date Month']).agg({
        'No. of Principal Member': 'sum',
        'Dependents': 'sum'
    }).reset_index()

    # Calculate total lives for sorting
    yearly_totals['Total Lives'] = yearly_totals['No. of Principal Member'] + yearly_totals['Dependents']

    # Sort the DataFrame by total lives in descending order
    yearly_totals = yearly_totals.sort_values('Total Lives', ascending=False)

    with cul2:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Principal Members
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Date Month'],
            y=yearly_totals['No. of Principal Member'],
            name='Principal Member',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0]  # Custom color for Principal Member
        ))

        # Add bars for Dependents
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Date Month'],
            y=yearly_totals['Dependents'],
            name='Dependents',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1]  # Custom color for Dependents
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=400
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Lives by Month and Member Type</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)

        with st.expander("Principal Members and Dependents Distribution Data"):
            st.write(df[['Client Name', 'No. of Principal Member','Dependents']].style.background_gradient(cmap="YlOrBr"))

    colus1,colus2 = st.columns(2)

    # Group data by "Start Date Year" and calculate the total number of Principal Members and Dependents
    yearly_totals = filtered_df.groupby(['Start Date Year']).agg({
        'No. of Principal Member': 'sum',
        'Dependents': 'sum'
    }).reset_index()

    with colus1:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Principal Members
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Date Year'],
            y=yearly_totals['No. of Principal Member'],
            name='Principal Member',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0]  # Custom color for Principal Member
        ))

        # Add bars for Dependents
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals['Start Date Year'],
            y=yearly_totals['Dependents'],
            name='Dependents',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1]  # Custom color for Dependents
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Month",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Total Lives by Year and Member Type</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)


   


    df_sorted = filtered_df.sort_values(by='Total lives', ascending=False)

    # Get the top 10 rows by employee size
    top_employer_groups = df_sorted.head(10)

    with colus2:
        fig_employer_groups = go.Figure()

        fig_employer_groups.add_trace(go.Bar(
            x=top_employer_groups['Client Name'],
            y=top_employer_groups['Total lives'],
            marker=dict(color='#009DAE'),
            text=top_employer_groups["Total lives"],
            textposition='outside', 
            textfont=dict(color='black'),  
            hoverinfo='y+text'
        ))

        fig_employer_groups.update_layout(
            xaxis_title="Client Name",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Top 10 Clients By Total Lives </h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_employer_groups, use_container_width=True)

        with st.expander("Clients Lives Covered Data"):
            st.write(df[['Client Name', 'Total lives']].style.background_gradient(cmap="YlOrBr"))

    
    cls1, cls2 = st.columns(2)
    
    # Group data by "Start Date Month" and "Client Segment" and sum the Total Lives
    monthly_lives_by_segment = data.groupby(['Start Date Month', 'Client Segment'])['Total lives'].sum().unstack().fillna(0)

    # Define custom colors (you can define more colors if you have more segments)
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8", "#f8a785"]

    with cls2:
        # Create the stacked bar chart
        fig_monthly_lives_by_segment = go.Figure()

        for i, segment in enumerate(monthly_lives_by_segment.columns):
            fig_monthly_lives_by_segment.add_trace(go.Bar(
                x=monthly_lives_by_segment.index,
                y=monthly_lives_by_segment[segment],
                name=segment,
                text=monthly_lives_by_segment[segment],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        fig_monthly_lives_by_segment.update_layout(
            barmode='stack',
            xaxis_title="Month",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Monthly Total Lives by Client Segment</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives_by_segment, use_container_width=True)

 # Group data by "Start Date Month" and "Intermediary" and sum the Total Lives
    monthly_lives_by_intermediary = data.groupby(['Start Date Month', 'Intermediary'])['Total lives'].sum().unstack().fillna(0)

    with cls1:
        # Define custom colors (you can define more colors if you have more intermediaries)
        custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

        # Create the stacked bar chart
        fig_monthly_lives_by_intermediary = go.Figure()

        for i, intermediary in enumerate(monthly_lives_by_intermediary.columns):
            fig_monthly_lives_by_intermediary.add_trace(go.Bar(
                x=monthly_lives_by_intermediary.index,
                y=monthly_lives_by_intermediary[intermediary],
                name=intermediary,
                text=monthly_lives_by_intermediary[intermediary],
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[i % len(custom_colors)]
            ))

        fig_monthly_lives_by_intermediary.update_layout(
            barmode='stack',
            xaxis_title="Month",
            yaxis_title="Total Lives",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50)
        )

        # Display the chart in Streamlit
        st.markdown('<h2 class="custom-subheader">Monthly Total Lives by Intermediary</h2>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives_by_intermediary, use_container_width=True)


    # Calculate the total insured premium by intermediary
    int_premiums = filtered_df.groupby("Intermediary")["Total lives"].sum().reset_index()
    int_premiums.columns = ["Intermediary", "Total lives"]


    cols1, cols2 = st.columns(2)

    with cols1:
        # Display the header
        st.markdown('<h2 class="custom-subheader">Total Lives by Channel</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Intermediary", values="Total lives", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True, height=200)

        with st.expander("Total Lives by Channel Data"):
            st.write(df[['Total lives', 'Intermediary']].style.background_gradient(cmap="YlOrBr"))

        # Calculate the total insured premium by client segment
    int_premiums = filtered_df.groupby("Client Segment")["Total lives"].sum().reset_index()
    int_premiums.columns = ["Client Segment", "Total lives"]

    with cols2:    
        # Display the header
        st.markdown('<h2 class="custom-subheader">Total Lives by Client Segment</h2>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Client Segment", values="Total lives", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=80))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Total lives by Client Sement Data"):
            st.write(df[['Total lives', 'Client Segment']].style.background_gradient(cmap="YlOrBr"))




    




    st.markdown('<h3 class="custom-subheader">Month-Wise Lives Distribution By Client Segment Table</h3>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=filtered_df,
            values="Total lives",
            index=["Client Segment"],
            columns="Start Date Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
        
else:
    st.error("No data available for this selection")