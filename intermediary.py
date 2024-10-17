import streamlit as st
import matplotlib.colors as mcolors
import plotly.express as px
import pandas as pd
import altair as alt
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

st.markdown('<h1 class="main-title">CHANNEL VIEW DASHBOARD</h1>', unsafe_allow_html=True)

filepath="WRITTEN PREMIUM 2024.xlsx"
sheet_name = "NEW BUSINES"
# Read all sheets into a dictionary of DataFrames
df = pd.read_excel(filepath, sheet_name=sheet_name)


# Sidebar styling and logo
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content h3 {
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
df["START DATE"] = pd.to_datetime(df["Start Date"], errors='coerce')


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


# Sort months based on the predefined order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}
sorted_months = sorted(df['Start Month'].dropna().unique(), key=lambda x: month_order[x])
df['Start Date Year'] = pd.to_numeric(df['Start Year'], errors='coerce').dropna().astype(int)

# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Date Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
product = st.sidebar.multiselect("Select Product", options=df['Product_name'].unique())
channel = st.sidebar.multiselect("Select Channel", options=df['Channel'].unique())
channel_name = st.sidebar.multiselect("Select Intermediary name", options=df['Intermediary name'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())

# Filtered DataFrame
filtered_df = df.copy()

# Create a 'Month-Year' column
filtered_df['Month-Year'] = filtered_df['Start Month'] + ' ' + filtered_df['Start Year'].astype(str)


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
    filtered_df = filtered_df[filtered_df['Start Year'].isin(year)]
if month:
    filtered_df = filtered_df[filtered_df['Start Month'].isin(month)]
if channel:
    filtered_df = filtered_df[filtered_df['Channel'].isin(channel)]
if channel_name:
    filtered_df = filtered_df[filtered_df['Intermediary name'].isin(channel_name)]
if product:
    filtered_df = filtered_df[filtered_df['Product_name'].isin(product)]
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
if channel_name:
    filter_description += f"{', '.join(map(str, channel_name))} "
if product:
    filter_description += f"{', '.join(product)} "
if client_name:
    filter_description += f"{', '.join(client_name)} "
if not filter_description:
    filter_description = "All df"



if not filtered_df.empty:

    scaling_factor = 1_000_000  # For millions
    scale = 1_000

    # Calculate the median premium per employer group
    grouped = filtered_df.groupby('Client Name')['Average Premium'].median().reset_index()
    grouped.columns = ['Client Name', 'Median Premium']

    # Calculate key metrics
    median_premium = (grouped['Median Premium'].median())/scale
    Q1 = (grouped['Median Premium'].quantile(0.25))/scale
    Q3 = (grouped['Median Premium'].quantile(0.75))/scale
    IQR = Q3 - Q1


     # Calculate metrics
    scaling_factor = 1_000_000  # For millions
    scale = 1_000_000_000
    df_proactiv = df[df['Product_name'] == 'ProActiv']
    df_health = df[df['Product_name'] == 'Health']

    # Calculate the total premium for endorsements only
    # Assuming the column name for the premium is 'Total Premium'


    total_pro = (df_proactiv['Total Premium'].sum())/scaling_factor
    total_health = (df_health['Total Premium'].sum())/scale


    total_pre = filtered_df["Basic Premium"].sum()
    total_in_pre = filtered_df["Total Premium"].sum()
    total_lives = filtered_df["Total lives"].sum()
    total_pm  = filtered_df["No. of staffs"].sum()
    average_premium_per_life = total_in_pre/total_pm


    # Scale the sums
    total_pre_scaled = total_pre / scaling_factor
    total_in_pre_scaled = total_in_pre / scaling_factor
    average_pre_scaled = average_premium_per_life/scaling_factor

    # Create 4-column layout for metric cards
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
    display_metric(col1, "Total Premium", f"RWF {total_in_pre_scaled:.0f} M")
    display_metric(col2, "Total Lives", total_lives)
    display_metric(col3, "Total Principal Members", total_pm)  
    display_metric(col2, "Total Health Premium", f"RWF {total_health:.0f} B")
    display_metric(col3, "Total ProActiv Premium", f"RWF {total_pro:.0f} M")
    display_metric(col1, "Average Premium Per Principal Member", f"RWF {average_pre_scaled:.1f}M")






    # Sidebar styling and logo
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .sidebar .sidebar-content h3 {
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



    colc1, colc2 = st.columns(2)

    # Group by day and intermediary, then sum the Total Premium
    area_chart_total_insured = filtered_df.groupby([filtered_df["START DATE"].dt.strftime("%Y-%m-%d"), 'Channel'])['Total Premium'].sum().reset_index(name='Total Premium')

    # Sort by the START DATE
    area_chart_total_insured = area_chart_total_insured.sort_values("START DATE")

    custom_colors_insured = ["brown", "#e66c37", "#009DAE"]

    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.0fM' % (x * 1e-6)

    with colc1:
        # Create the area chart for Total Premium
        fig1, ax1 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='START DATE', columns='Channel', values='Total Premium').fillna(0)
        
        # Plot the stacked area chart
        pivot_df_insured.plot(kind='area', stacked=True, ax=ax1, color=custom_colors_insured[:len(pivot_df_insured.columns)])

        # Remove the border around the chart
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)

        # Set x-axis title
        ax1.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

        # Set y-axis title
        ax1.set_ylabel("Total Premium", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

        # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Premium by Channel over Time</h3>', unsafe_allow_html=True)

        # Format the y-axis
        formatter = FuncFormatter(millions)
        ax1.yaxis.set_major_formatter(formatter)

        # Display the chart in Streamlit
        st.pyplot(fig1)



    # Group by day and intermediary, then sum the Total Lives
    area_chart_total_lives = filtered_df.groupby([filtered_df["START DATE"].dt.strftime("%Y-%m-%d"), 'Channel'])['Total lives'].sum().reset_index(name='Total lives')

    # Sort by the START DATE
    area_chart_total_lives = area_chart_total_lives.sort_values("START DATE")


    with colc2:
        # Create the area chart for Total Lives
        fig2, ax2 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_lives = area_chart_total_lives.pivot(index='START DATE', columns='Channel', values='Total lives').fillna(0)
        
        # Plot the stacked area chart
        pivot_df_lives.plot(kind='area', stacked=True, ax=ax2, color=custom_colors_insured[:len(pivot_df_lives.columns)])


        # Remove the border around the chart
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        
        # Set x-axis title
        ax2.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

        # Set y-axis title
        ax2.set_ylabel("Total Lives Covered", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")


        # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Lives Covered by Channel over Time</h3>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig2)

    cols1,cols2 = st.columns(2)

    # Group data by "Start Date Year" and "Intermediary" and calculate the average Total Premium
    yearly_avg_premium = filtered_df.groupby(['Start Date Year', 'Channel'])['Average Premium'].mean().unstack().fillna(0)

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
            yaxis_title="Average Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Premium Yearly by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    # Calculate the IQR for each intermediary in each year
    iqr_data = filtered_df.groupby(['Start Date Year', 'Channel'])['Total Premium'].describe(percentiles=[.25, .5, .75]).unstack()

    # Flatten the MultiIndex columns
    iqr_data.columns = ['_'.join(col).strip() for col in iqr_data.columns.values]

    # Define custom colors
    custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]


    with cols2:
        # Create the box plot
        fig_iqr = go.Figure()

        for idx, intermediary in enumerate(filtered_df['Channel'].unique()):
            intermediary_data = filtered_df[filtered_df['Channel'] == intermediary]
            
            # Modified x values to include both year and intermediary
            fig_iqr.add_trace(go.Box(
                x=intermediary_data['Start Year'].astype(str) + ' - ' + intermediary,
                y=intermediary_data['Total Premium'],
                name=intermediary,
                boxmean='sd',  # Shows mean and standard deviation
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_iqr.update_layout(
            xaxis_title="Start Year",
            yaxis_title="Total Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450,
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",
                y=1.05,  # Adjust y position to move legend down
                xanchor="center",
                x=0.5
            )
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Interquartile Range of Premium by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_iqr, use_container_width=True)

    
   
    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Yearly Average Premium by Channel"):
            st.dataframe(yearly_avg_premium.style.format(precision=2))
    
    # Function to find the closest client to a given value
    def find_closest_client(df, value):
        return df.iloc[(df['Total Premium'] - value).abs().argsort()[:1]]['Client Name'].values[0]

    with ccl2:
        with st.expander("Client Names with Q1, Median, and Q3 Premiums by Channel"):
            for (year, intermediary), group in filtered_df.groupby(['Start Date Year', 'Channel']):
                q1 = group['Total Premium'].quantile(0.25)
                median = group['Total Premium'].median()
                q3 = group['Total Premium'].quantile(0.75)

                q1_client = find_closest_client(group, q1)
                median_client = find_closest_client(group, median)
                q3_client = find_closest_client(group, q3)

                st.markdown(f"**Year: {year}, Channel: {intermediary}**")
                
                # Create a DataFrame to display the data in tabular form
                table_data = {
                    "Metric": ["Q1 Premium", "Median Premium", "Q3 Premium"],
                    "Client Name": [q1_client, median_client, q3_client],
                    "Premium": [q1, median, q3]
                }
                table_df = pd.DataFrame(table_data)
                st.table(table_df)
                st.markdown("---")


    cul1, cul2 = st.columns(2)
 # Calculate the Total Premium by intermediary
    int_premiums = filtered_df.groupby("Channel")["Average Premium"].sum().reset_index()
    int_premiums.columns = ["Channel", "Total Premium"]    

    with cul2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Average Premium by Channel</h3>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(int_premiums, names="Channel", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

 # Calculate the Total Premium by intermediary
    prod_premiums = filtered_df.groupby("Product_name")["Average Premium"].sum().reset_index()
    prod_premiums.columns = ["Product", "Total Premium"]    

    with cul1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Average Premium by Product</h3>', unsafe_allow_html=True)

        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]

        # Create a donut chart
        fig = px.pie(prod_premiums, names="Product", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    cul1, cul2 = st.columns(2)

    with cul2:
        with st.expander("Average Premium by Channel"):
            st.dataframe(int_premiums.style.format(precision=2))

    with cul1:
        with st.expander("Average Premium by Product"):
            st.dataframe(prod_premiums.style.format(precision=2))


    # Group by Client Name and Intermediary, then sum the Total Premium
    df_grouped = filtered_df.groupby(['Intermediary name', 'Channel'])['Total Premium'].sum().reset_index()

    # Get the top 10 clients by Total Premium
    top_10_clients = df_grouped.groupby('Intermediary name')['Total Premium'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Intermediary name'].isin(top_10_clients['Intermediary name'])]
    # Sort the client_df by Total Premium in descending order
    client_df = client_df.sort_values(by='Total Premium', ascending=False)
   
    with cul1:
            # Create the bar chart
        fig = go.Figure()

            # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

            # Add bars for each intermediary
        for idx, intermediary in enumerate(client_df['Channel'].unique()):
                intermediary_data = client_df[client_df['Channel'] == intermediary]
                fig.add_trace(go.Bar(
                    x=intermediary_data['Intermediary name'],
                    y=intermediary_data['Total Premium'],
                    name=intermediary,
                    text=[f'{value/1e6:.0f}M' for value in intermediary_data['Total Premium']],
                    textposition='auto',
                    marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                ))

        fig.update_layout(
                barmode='stack',
                yaxis_title="Total Premium",
                xaxis_title="Intermediary name",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )

            # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Intermediaries by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)



    # Group by Client Name and Intermediary, then sum the Total Premium
    df_grouped = filtered_df.groupby(['Client Name', 'Channel'])['Total Premium'].sum().reset_index()

    # Get the top 10 clients by Total Premium
    top_10_clients = df_grouped.groupby('Client Name')['Total Premium'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    int = df_grouped[df_grouped['Client Name'].isin(top_10_clients['Client Name'])]
    # Sort the client_df by Total Premium in descending order
    int_df = int.sort_values(by='Total Premium', ascending=False)
   
    with cul2:
            # Create the bar chart
        fig = go.Figure()

            # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

            # Add bars for each intermediary
        for idx, intermediary in enumerate(int_df['Channel'].unique()):
                intermediary_data = int_df[int_df['Channel'] == intermediary]
                fig.add_trace(go.Bar(
                    x=intermediary_data['Client Name'],
                    y=intermediary_data['Total Premium'],
                    name=intermediary,
                    text=[f'{value/1e6:.0f}M' for value in intermediary_data['Total Premium']],
                    textposition='auto',
                    marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
                ))

        fig.update_layout(
                barmode='stack',
                yaxis_title="Total Premium",
                xaxis_title="Client Name",
                font=dict(color='Black'),
                xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                margin=dict(l=0, r=0, t=30, b=50)
            )

            # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Top 15 Client Premium by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)


    with cul1:
        with st.expander("Intermedirary premium by Channel"):
            st.dataframe(client_df.style.format(precision=2))
    with cul2:
        with st.expander("Client Premium by Channel"):
            st.dataframe(int_df.style.format(precision=2))




    cls1, cls2 = st.columns(2)

    # Group data by "Start Date Month" and "Intermediary" and sum the Total Premium
    monthly_premium = filtered_df.groupby(['Start Month', 'Channel'])['Total Premium'].sum().unstack().fillna(0)


    with cls1:
        # Define custom colors
        custom_colors = ["#006E7F", "#e66c37", "#B4B4B8"]

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

        # Add a line chart to show the trend of Total Premium over time
        fig_monthly_premium.add_trace(go.Scatter(
            x=monthly_premium.index,
            y=monthly_premium.sum(axis=1),
            mode='lines+markers',
            name='Rate of change',
            line=dict(color='red', width=2),
            marker=dict(size=6, symbol='circle', color='red')
        ))

        # Set layout for the Total Premium chart
        fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Month",
            yaxis_title="Total Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Premium chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Premium by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)


  # Group by Start Date Month and Intermediary and sum the Total lives
    monthly_lives = filtered_df.groupby(['Start Month', 'Channel'])['Total lives'].sum().unstack().fillna(0)

    with cls2:
        fig_monthly_lives = go.Figure()

        for idx, intermediary in enumerate(monthly_lives.columns):
            fig_monthly_lives.add_trace(go.Bar(
                x=monthly_lives.index,
                y=monthly_lives[intermediary],
                name=intermediary,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Add a line chart to show the trend of total lives covered over time
        fig_monthly_lives.add_trace(go.Scatter(
            x=monthly_lives.index,
            y=monthly_lives.sum(axis=1),
            mode='lines+markers',
            name='Rate of change',
            line=dict(color='red', width=2),
            marker=dict(size=6, symbol='circle', color='red')
        ))

        # Set layout for the Total Lives chart
        fig_monthly_lives.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Month",
            yaxis_title="Total Lives Covered",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Lives chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Lives Covered by Channel</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives, use_container_width=True)

    clm1, clm2 = st.columns(2)

    with clm1:
        # Create an expandable section for the table
        with st.expander("View Monthly Total Premium by Channel"):
            st.dataframe(monthly_premium.style.format(precision=2))

    with clm2:
        with st.expander("View Monthly Total Live covered by Channel"):
            st.write(df[['Client Name', 'Channel', 'Total Premium']].style.background_gradient(cmap="YlOrBr"))
 



    # summary table
    st.markdown('<h3 class="custom-subheader">Month-Wise Premium By Client Segment Table</h3>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=filtered_df,
            values="Total Premium",
            index=["Channel"],
            columns="Start Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
    

        
else:
    st.error("No data available for this selection")