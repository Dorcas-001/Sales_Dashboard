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

st.markdown('<h1 class="main-title">CLIENT SEGMENT VIEW </h1>', unsafe_allow_html=True)

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
df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')



# Get minimum and maximum dates for the date input
startDate = df["Start Date"].min()
endDate = df["Start Date"].max()

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
df = df[(df["Start Date"] >= date1) & (df["Start Date"] <= date2)].copy()



df['Start Year'] = df['Start Year'].astype(int)

# Create a 'Month-Year' column
df['Month-Year'] = df['Start Month'] + ' ' + df['Start Year'].astype(str)



month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}
# Sort months based on their order
sorted_months = sorted(df['Start Month'].dropna().unique(), key=lambda x: month_order[x])


# Ensure the 'Start Month' column is in datetime format if needed
df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')

df['Start Year'] = pd.to_numeric(df['Start Year'], errors='coerce').dropna().astype(int)

# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
product = st.sidebar.multiselect("Select Product", options=df['Product_name'].unique())
channel = st.sidebar.multiselect("Select Intermediary name", options=df['Intermediary name'].unique())

client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())

# Filtered DataFrame
filtered_df = df

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
if segment:
    filtered_df = filtered_df[filtered_df['Client Segment'].isin(segment)]
if channel:
    filtered_df = filtered_df[filtered_df['Intermediary name'].isin(channel)]
if product:
    filtered_df = filtered_df[filtered_df['Product_name'].isin(product)]
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
if channel:
    filter_description += f"{', '.join(map(str, channel))} "
if product:
    filter_description += f"{', '.join(product)} "
if client_name:
    filter_description += f"{', '.join(client_name)} "
if not filter_description:
    filter_description = "All df"



if not filtered_df.empty:
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
    display_metric(col3, "Total Health Premium", f"RWF {total_health:.0f} B")
    display_metric(col2, "Total ProActiv Premium", f"RWF {total_pro:.0f} M")
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

    
    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]



    colc1, colc2 = st.columns(2)
    # Sample function to format y-axis labels
    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.1fM' % (x * 1e-6)

    # Assuming filtered_df is already defined and contains the necessary data
    # Ensure 'Start Month' is in datetime format
    filtered_df['Start Date'] = pd.to_datetime(filtered_df['Start Date'], errors='coerce')

    # Group by day and Client Segment, then sum the Total Premium
    area_chart_total_insured = (
        filtered_df.groupby([filtered_df["Start Date"].dt.strftime("%Y-%m-%d"), 'Client Segment'])['Total Premium']
        .sum()
        .reset_index(name='Total Premium')
    )

    # Sort by the Start Month
    area_chart_total_insured = area_chart_total_insured.sort_values("Start Date")

    # Ensure 'Total Premium' is numeric
    area_chart_total_insured['Total Premium'] = pd.to_numeric(area_chart_total_insured['Total Premium'], errors='coerce')

    # Check if the DataFrame is empty before plotting
    if not area_chart_total_insured.empty:
        with colc1:
            # Create the area chart for Total Premium
            fig1, ax1 = plt.subplots()

            # Pivot the DataFrame for easier plotting
            pivot_df_insured = area_chart_total_insured.pivot(index='Start Date', columns='Client Segment', values='Total Premium').fillna(0)

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
            ax1.set_ylabel("Total Premium", fontsize=9, color="gray")
            plt.yticks(fontsize=9, color="gray")

            # Format the y-axis
            formatter = FuncFormatter(millions)
            ax1.yaxis.set_major_formatter(formatter)

            # Set chart title
            st.markdown('<h3 class="custom-subheader">Total Premium by Client Segment Over Time</h3>', unsafe_allow_html=True)

            # Display the chart in Streamlit
            st.pyplot(fig1)
   # Function to format y-axis labels in millions
    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.0fM' % (x * 1e-6)

    # Group by day and Client Segment, then sum the Total Premium
    area_chart_total_insured = df.groupby([df["Start Date"].dt.strftime("%Y-%m-%d"), 'Product_name'])['Total Premium'].sum().reset_index(name='Total Premium')

    # Sort by the Start Month
    area_chart_total_insured = area_chart_total_insured.sort_values("Start Date")


    with colc2:
        # Create the area chart for Total Premium
        fig1, ax1 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='Start Date', columns='Product_name', values='Total Premium').fillna(0)
        
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
        ax1.set_ylabel("Total Premium", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

        # Format the y-axis
        formatter = FuncFormatter(millions)
        ax1.yaxis.set_major_formatter(formatter)

        # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Premium by Product Over Time</h3>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig1)


    cols1,cols2 = st.columns(2)

    # Group data by "Start Month Year" and "Client Segment" and calculate the average Total Premium
    yearly_avg_premium = filtered_df.groupby(['Start Year', 'Client Segment'])['Average Premium'].mean().unstack().fillna(0)

    # Define custom colors

    with cols1:
        # Create the grouped bar chart
        fig_yearly_avg_premium = go.Figure()

        for idx, Client_Segment in enumerate(yearly_avg_premium.columns):
            fig_yearly_avg_premium.add_trace(go.Bar(
                x=yearly_avg_premium.index,
                y=yearly_avg_premium[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        fig_yearly_avg_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Year",
            yaxis_title="Average Insured Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Insured Premium Yearly by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    # Calculate the IQR for each client segment in each year
    iqr_data = filtered_df.groupby(['Start Year', 'Client Segment'])['Total Premium'].describe(percentiles=[.25, .5, .75]).unstack()

    # Flatten the MultiIndex columns
    iqr_data.columns = ['_'.join(col).strip() for col in iqr_data.columns.values]


    with cols2:
        # Create the box plot
        fig_iqr = go.Figure()

        for idx, client_segment in enumerate(filtered_df['Client Segment'].unique()):
            client_segment_data = filtered_df[filtered_df['Client Segment'] == client_segment]
            
            fig_iqr.add_trace(go.Box(
                x=client_segment_data['Start Year'].astype(str) + ' - ' + client_segment,
                y=client_segment_data['Total Premium'],
                name=client_segment,
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
        st.markdown('<h3 class="custom-subheader">Interquartile Range of Total Premium by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_iqr, use_container_width=True)


    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Yearly Average Insured Premium by Client Segment"):
            st.dataframe(yearly_avg_premium.style.format(precision=2))
        
    # Function to find the closest client to a given value
    def find_closest_client(df, value):
        return df.iloc[(df['Total Premium'] - value).abs().argsort()[:1]]['Client Name'].values[0]

    with ccl2:
        with st.expander("Client Names with Q1, Median, and Q3 Premiums by Client Segment"):
            for (year, client_segment), group in filtered_df.groupby(['Start Year', 'Client Segment']):
                q1 = group['Total Premium'].quantile(0.25)
                median = group['Total Premium'].median()
                q3 = group['Total Premium'].quantile(0.75)

                q1_client = find_closest_client(group, q1)
                median_client = find_closest_client(group, median)
                q3_client = find_closest_client(group, q3)

                st.markdown(f"**Year: {year}, Client Segment: {client_segment}**")
                
                # Create a DataFrame to display the data in tabular form
                table_data = {
                    "Metric": ["Q1 Premium", "Median Premium", "Q3 Premium"],
                    "Client Name": [q1_client, median_client, q3_client],
                    "Premium": [q1, median, q3]
                }
                table_df = pd.DataFrame(table_data)
                st.table(table_df)
                st.markdown("---")


    cls1, cls2 = st.columns(2)

    # Group data by "Start Month Month" and "Client Segment" and sum the Total Premium
    monthly_premium = filtered_df.groupby(['Start Month', 'Client Segment'])['Total Premium'].sum().unstack().fillna(0)

    # Group data by "Start Month Month" and "Client Segment" and sum the Total Lives
    monthly_lives = filtered_df.groupby(['Start Month', 'Client Segment'])['Total lives'].sum().unstack().fillna(0)



    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:
        fig_monthly_premium = go.Figure()

        for idx, Client_Segment in enumerate(monthly_premium.columns):
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_premium.index,
                y=monthly_premium[Client_Segment],
                name=Client_Segment,
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
            xaxis_title="Month",
            yaxis_title="Total Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Premium chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Premium Monthly by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    with cls2:
        fig_monthly_lives = go.Figure()

        for idx, Client_Segment in enumerate(monthly_lives.columns):
            fig_monthly_lives.add_trace(go.Bar(
                x=monthly_lives.index,
                y=monthly_lives[Client_Segment],
                name=Client_Segment,
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
        st.markdown('<h3 class="custom-subheader">Total Lives Covered Monthly by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_lives, use_container_width=True)


    clm1, clm2 = st.columns(2)

    with clm1:
        # Create an expandable section for the table
        with st.expander("View Monthly Total Premium by Client Segment"):
            st.dataframe(monthly_premium.style.format(precision=2))

    with clm2:
        with st.expander("View Monthly Total Live covered by Client Segment"):
            st.write(df[['Client Name', 'Client Segment', 'Total Premium']].style.background_gradient(cmap="YlOrBr"))
 

    cul1, cul2 = st.columns(2)

 # Calculate the Total Premium by Client Segment
    int_premiums = filtered_df.groupby("Client Segment")["Total Premium"].sum().reset_index()
    int_premiums.columns = ["Client Segment", "Total Premium"]    

    with cul1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Premium by Client Segment</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_premiums, names="Client Segment", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


    # Group by Client Name and Client Segment, then sum the Total Premium
    df_grouped = filtered_df.groupby(['Client Name', 'Client Segment'])['Total Premium'].sum().reset_index()

    # Get the top 10 clients by Total Premium
    top_10_clients = df_grouped.groupby('Client Name')['Total Premium'].sum().nlargest(15).reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Client Name'].isin(top_10_clients['Client Name'])]
    # Sort the client_df by Total Premium in descending order
    client_df = client_df.sort_values(by='Total Premium', ascending=False)

    with cul2:
        # Create the bar chart
        fig = go.Figure()


            # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Client Segment'].unique()):
                Client_Segment_data = client_df[client_df['Client Segment'] == Client_Segment]
                fig.add_trace(go.Bar(
                    x=Client_Segment_data['Client Name'],
                    y=Client_Segment_data['Total Premium'],
                    name=Client_Segment,
                    text=[f'{value/1e6:.0f}M' for value in Client_Segment_data['Total Premium']],
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
        st.markdown('<h3 class="custom-subheader">Top 15 Client Premium by Client Segment</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    culs1, culs2 = st.columns(2)
    with culs1:
        with st.expander("Client Premium by Client Segment"):
                st.write(df[['Client Name', 'Client Segment', 'Total Premium']].style.background_gradient(cmap="YlOrBr"))

    with culs2:
        with st.expander("Total Premium by Client Segment"):
            st.dataframe(int_premiums.style.format(precision=2))
    # summary table
    st.markdown('<h3 class="custom-subheader">Month-Wise Insured Premium By Client Segment Table</h3>', unsafe_allow_html=True)

    with st.expander("Summary_Table"):

        colors = ["#527853", "#F9E8D9", "#F7B787", "#EE7214", "#B99470"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("EarthyPalette", colors)
        # Create the pivot table
        sub_specialisation_Year = pd.pivot_table(
            data=filtered_df,
            values="Total Premium",
            index=["Client Segment"],
            columns="Start Month"
        )
        st.write(sub_specialisation_Year.style.background_gradient(cmap="YlOrBr"))
    

        
else:
    st.error("No data available for this selection")