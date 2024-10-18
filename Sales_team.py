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

st.markdown('<h1 class="main-title">Eden Care Sales Team  View</h1>', unsafe_allow_html=True)

filepath="WRITTEN PREMIUM 2024.xlsx"
sheet_name = "NEW BUSINES"

# Read all sheets into a dictionary of DataFrames
df = pd.read_excel(filepath, sheet_name=sheet_name)



# Ensure the 'Start Date' column is in datetime format if needed
df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')


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


eden_care_df = df[df['Intermediary company'] == 'Eden Care']



month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}
# Sort months based on their order
sorted_months = sorted(df['Start Month'].dropna().unique(), key=lambda x: month_order[x])
# Sidebar for filters
st.sidebar.header("Filters")
month = st.sidebar.multiselect("Select Month", options=sorted_months)
cover = st.sidebar.multiselect("Select Cover Type", options=df['Cover Type'].unique())
product = st.sidebar.multiselect("Select Product", options=df['Product_name'].unique())
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
owner = st.sidebar.multiselect("Select Sales Person", options=eden_care_df['Intermediary name'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())



# Apply filters to the DataFrame
if month:
    df = df[df['Start Month'].isin(month)]
if cover:
    df = df[df['Cover Type'].isin(cover)]
if product:
    df = df[df['Product_name'].isin(product)]
if segment:
    df = df[df['Client Segment'].isin(segment)]
if owner:
    df = df[df['Owner'].isin(owner)]
if client_name:
    df = df[df['Client Name'].isin(client_name)]


# Determine the filter description
filter_description = ""
if month:
    filter_description += f"{', '.join(map(str, month))} "
if cover:
    filter_description += f"{', '.join(map(str, cover))} "
if product:
    filter_description += f"{', '.join(product)} "
if owner:
    filter_description += f"{', '.join(owner)} "
if client_name:
    filter_description += f"{', '.join(client_name)} "
if not filter_description:
    filter_description = "All data"


df['Start Year'] = df['Start Year'].astype(int)

# Create a 'Month-Year' column
df['Month-Year'] = df['Start Month'] + ' ' + df['Start Year'].astype(str)


# Function to sort month-year combinations
def sort_key(month_year):
    month, year = month_year.split()
    return (int(year), month_order[month])

# Extract unique month-year combinations and sort them
month_years = sorted(df['Month-Year'].unique(), key=sort_key)

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
df = df[
    df['Month-Year'].apply(lambda x: (int(x.split()[1]), month_order[x.split()[0]])).between(start_index, end_index)
]

# Filter the concatenated DataFrame to include only endorsements
df_new = df[df['Cover Type'] == 'New Insured']
df_renew = df[df['Cover Type'] == 'Renew/Insured']
df_proactiv = df[df['Product_name'] == 'ProActiv']
df_health = df[df['Product_name'] == 'Health']

# Calculate the total premium for endorsements only
# Assuming the column name for the premium is 'Total Premium'

if not df.empty:
     # Calculate metrics
    scale=1_000_000  # For millions

    total_pre = df["Total Premium"].sum()
    total_in_pre = df["Total Premium"].sum()
    total_lives=df["Total lives"].sum()
    # Scale the sums
    total_pre_scaled = total_pre / scale
    total_in_pre_scaled = total_in_pre / scale


    total_new = (df_new['Total Premium'].sum())/scale
    total_renew = (df_renew['Total Premium'].sum())/scale
    total_pro = (df_proactiv['Total Premium'].sum())/scale
    total_health = (df_health['Total Premium'].sum())/scale


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
            font-size: 1.5em;
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
    display_metric(col1, f"Total Premium ({filter_description.strip()})", value=f"RWF {total_pre_scaled:.0f} M")
    display_metric(col2, "Total Health Sales", f"RWF {total_health:.0f} M")
    display_metric(col3, f"Total ProActiv Sales ({filter_description.strip()})", value=f"RWF {total_pro:.0f} M")
    display_metric(col1, f"Total New Sales({filter_description.strip()})", value=f"RWF {total_new:.0f} M")
    display_metric(col2, F"Total Renewals ({filter_description.strip()})", value=f"RWF {total_renew:.0f} M")
    display_metric(col3, "Total Lives Covered", f"{total_lives:.0f} ")




   
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
    # Filter data for "Eden Care" intermediaries
    eden_care_df = df[df['Intermediary company'] == 'Eden Care']
 

    # Group by day and Client Segment, then sum the Total Lives
    area_chart_total_lives = eden_care_df.groupby([eden_care_df["Start Date"].dt.strftime("%Y-%m-%d"), 'Intermediary name'])['Total Premium'].sum().reset_index(name='Total Premium')

    # Sort by the START DATE
    area_chart_total_lives = area_chart_total_lives.sort_values("Start Date")

    with colc1:
        # Create the area chart for Total Lives Covered
        fig2, ax2 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_lives = area_chart_total_lives.pivot(index='Start Date', columns='Intermediary name', values='Total Premium').fillna(0)
        
        # Plot the stacked area chart
        pivot_df_lives.plot(kind='area', stacked=True, ax=ax2, color=custom_colors[:len(pivot_df_lives.columns)])

        # Remove the border around the chart
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)

        # Set x-axis title
        ax2.set_xlabel("Date", fontsize=9, color="gray")
        plt.xticks(rotation=45, fontsize=9, color="gray")

        # Set y-axis title
        ax2.set_ylabel("Total Premium", fontsize=9, color="gray")
        plt.yticks(fontsize=9, color="gray")

        # Set chart title
        st.markdown('<h3 class="custom-subheader">Total Sales by Sales Team Over Time</h3>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig2)


    # Group data by "Intermediary name" and sum the Total Premium
    premium_by_intermediary = eden_care_df.groupby('Intermediary name')['Total Premium'].sum().reset_index()

    # Calculate the number of sales by "Intermediary name"
    sales_by_intermediary = eden_care_df.groupby('Intermediary name').size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged_data = premium_by_intermediary.merge(sales_by_intermediary, on='Intermediary name')



    with colc2:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Total Premium
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged_data['Intermediary name'],
            y=merged_data['Total Premium'],
            text=merged_data['Total Premium'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Total Premium'
        ))

        # Add scatter trace for Number of Sales on secondary y-axis
        fig_premium_by_intermediary.add_trace(go.Scatter(
            x=merged_data['Intermediary name'],
            y=merged_data['Number of Sales'],
            mode='lines+markers',
            name='Number of Sales',
            yaxis='y2',
            marker=dict(color='red', size=10),
            line=dict(color='red', width=2)
        ))

        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Intermediary Name",
            yaxis=dict(
                title="Total Premium",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),
            yaxis2=dict(
                title="Number of Sales",
                titlefont=dict(color="red"),
                tickfont=dict(color="red"),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Premium and Number of Sales by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)



    cl1, cl2 =st.columns(2)

    with cl2:
        with st.expander("Premium for Sales Team"):
            st.dataframe(sales_by_intermediary.style.format(precision=2))
        
    with cl1:  
            with st.expander("Total Premium by Sales Team over Time"):
                    st.dataframe(area_chart_total_lives.style.format(precision=2))



    # Group data by "Start Date Month" and "Client Segment" and sum the Total Premium
    monthly_premium = eden_care_df.groupby(['Start Month', 'Intermediary name'])['Total Premium'].sum().unstack().fillna(0)



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
    st.markdown('<h3 class="custom-subheader">Monthly Sales Distribution by Sales Team</h3>', unsafe_allow_html=True)
    st.plotly_chart(fig_monthly_premium, use_container_width=True)


  
        # Expander for IQR table
    with st.expander("Target and premuim by Product"):
            st.dataframe(monthly_premium.style.format(precision=2))



    colc1, colc2 = st.columns(2)
    

    # Group data by "Intermediary name" and "Cover Type" and sum the Total Premium
    cover_type_by_intermediary = eden_care_df.groupby(['Intermediary name', 'Cover Type'])['Total Premium'].sum().unstack().fillna(0)


    with colc1:
        fig_cover_type_by_intermediary = go.Figure()

        for idx, cover_type in enumerate(cover_type_by_intermediary.columns):
            fig_cover_type_by_intermediary.add_trace(go.Bar(
                x=cover_type_by_intermediary.index,
                y=cover_type_by_intermediary[cover_type],
                name=cover_type,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Set layout for the Total Premium chart
        fig_cover_type_by_intermediary.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Intermediary Name",
            yaxis_title="Total Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Premium chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Premium Distribution by Cover Type by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_cover_type_by_intermediary, use_container_width=True)



    # Group by Client Name and Client Segment, then sum the Total Premium
    df_grouped = eden_care_df.groupby(['Client Name', 'Intermediary name'])['Total Premium'].sum().nlargest(15).reset_index()

    # Get the top 10 clients by Total Premium
    top_10_clients = df_grouped.groupby('Client Name')['Total Premium'].sum().reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Client Name'].isin(top_10_clients['Client Name'])]
    # Sort the client_df by Total Premium in descending order
    client_df = client_df.sort_values(by='Total Premium', ascending=False)


    with colc2:
        # Create the bar chart
        fig = go.Figure()


                # Add bars for each Client Segment
        for idx, Client_Segment in enumerate(client_df['Intermediary name'].unique()):
                    Client_Segment_data = client_df[client_df['Intermediary name'] == Client_Segment]
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
        st.markdown('<h3 class="custom-subheader">Client Premium by Sales Team</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    colc1, colc2 = st.columns(2)
    with colc2:  
        with st.expander("Client Premium by Sales Team"):
                st.dataframe(client_df.style.format(precision=2))

    with colc1:
        # Expander for IQR table
        with st.expander("Premium for Sales Team"):
            st.dataframe(cover_type_by_intermediary.style.format(precision=2))
