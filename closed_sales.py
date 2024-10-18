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

st.markdown('<h1 class="main-title">CLOSED SALES VIEW</h1>', unsafe_allow_html=True)

filepath="WRITTEN PREMIUM 2024.xlsx"
sheet_name = "NEW BUSINES"
sheet_name1 ="ENDORSMENTS"
# Read all sheets into a dictionary of DataFrames
df0 = pd.read_excel(filepath, sheet_name=sheet_name)
df1=pd.read_excel(filepath, sheet_name=sheet_name1)




# Ensure the 'Start Date' column is in datetime format
df1['Start Date'] = pd.to_datetime(df1['Start Date'], errors='coerce')
# Filter rows where the Start Date is in 2024


df = pd.concat([df0, df1])


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
channel = st.sidebar.multiselect("Select Channel", options=df['Channel'].unique())
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
owner = st.sidebar.multiselect("Select Sales Team", options=df['Owner'].unique())
channel_name = st.sidebar.multiselect("Select Intermediary Name", options=df['Intermediary name'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())



# Apply filters to the DataFrame
if month:
    df = df[df['Start Month'].isin(month)]
if cover:
    df = df[df['Cover Type'].isin(cover)]
if channel:
    df = df[df['Channel'].isin(channel)]
if segment:
    df = df[df['Client Segment'].isin(segment)]
if product:
    df = df[df['Product'].isin(product)]
if owner:
    df = df[df['Owner'].isin(owner)]
if channel_name:
    df = df[df['Intermediary name'].isin(channel_name)]
if client_name:
    df = df[df['Client Name'].isin(client_name)]


# Determine the filter description
filter_description = ""
if month:
    filter_description += f"{', '.join(map(str, month))} "
if cover:
    filter_description += f"{', '.join(map(str, cover))} "
if channel:
    filter_description += f"{', '.join(channel)} "
if product:
    filter_description += f"{', '.join(product)} "
if segment:
    filter_description += f"{', '.join(segment)} "
if owner:
    filter_description += f"{', '.join(owner)} "
if channel_name:
    filter_description += f"{', '.join(channel_name)} "
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
df_endorsements_only = df[(df['Type'] == 'Endorsement') & (df['Product_name'] == 'Health')]
# Filter the concatenated DataFrame to include only endorsements
df_new = df[df['Cover Type'] == 'New Insured']
df_renew = df[df['Cover Type'] == 'Renew/Insured']
df_proactiv = df[df['Product_name'] == 'ProActiv']
df_health = df[df['Product_name'] == 'Health']

df_proactiv_new = df_proactiv[df_proactiv['Cover Type'] == 'New Insured']
df_proactiv_renew = df_proactiv[df_proactiv['Cover Type'] == 'Renew/Insured']

df_health_new = df_health[df_health['Cover Type'] == 'New Insured']
df_health_renew = df_health[df_health['Cover Type'] == 'Renew/Insured']
# Calculate the total premium for endorsements only
# Assuming the column name for the premium is 'Total Premium'
if not df.empty:
     # Calculate metrics
    scale=1_000_000  # For millions

    total_pre = df["Total Premium"].sum()
    total_in_pre = df["Total Premium"].sum()
    # Scale the sums
    total_pre_scaled = total_pre / scale
    total_in_pre_scaled = total_in_pre / scale

    total_endorsement_premium = (df_endorsements_only['Total Premium'].sum())/scale
    total_new = (df_new['Total Premium'].sum())/scale
    total_renew = (df_renew['Total Premium'].sum())/scale
    total_pro = (df_proactiv['Total Premium'].sum())/scale
    total_health = (df_health['Total Premium'].sum())/scale

    # Calculate total premiums for specific combinations
    total_proactiv_new = (df_proactiv_new['Total Premium'].sum()) / scale
    total_proactiv_renew = (df_proactiv_renew['Total Premium'].sum()) / scale
    total_health_new = (df_health_new['Total Premium'].sum()) / scale
    total_health_renew = (df_health_renew['Total Premium'].sum()) / scale

    # Create 4-column layout for metric cards

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

    st.markdown('<h3 class="custom-subheader">For Total Premiums</h3>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # Display metrics
    display_metric(col1, f"Total Premium ({filter_description.strip()})", value=f"RWF {total_pre_scaled:.0f} M")
    display_metric(col2, "Total Endorsement", f"RWF {total_endorsement_premium:.0f} M")
    display_metric(col3, "Total New Sales", value=f"RWF {total_new:.0f} M")
    display_metric(col4, "Total Renewals", value=f"RWF {total_renew:.0f} M")
    
    st.markdown('<h3 class="custom-subheader">For Health Insurance</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    display_metric(col1, "Total Health Sales", value=f"RWF {total_health:.0f} M")
    display_metric(col2, "Total New Health Premium", value=f"RWF {total_health_new:.0f} M")
    display_metric(col3, "Total Health Renewals", value=f"RWF {total_health_renew:.0f} M")

    st.markdown('<h3 class="custom-subheader">For ProActiv</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    display_metric(col1, "Total ProActiv Sales", value=f"RWF {total_pro:.0f} M")
    display_metric(col2, "Total New ProActiv Premium", value=f"RWF {total_proactiv_new:.0f} M")
    display_metric(col3, "Total ProActiv Renewals", value=f"RWF {total_proactiv_renew:.0f} M")

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

    cols1, cols2 = st.columns(2)

    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]


    
    # Function to format y-axis labels in millions
    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.0fM' % (x * 1e-6)

    # Group by day and Client Segment, then sum the Total Premium
    area_chart_total_insured = df.groupby([df["Start Date"].dt.strftime("%Y-%m-%d"), 'Product_name'])['Total Premium'].sum().reset_index(name='Total Premium')

    # Sort by the START DATE
    area_chart_total_insured = area_chart_total_insured.sort_values("Start Date")


    with cols1:
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


    # Group data by "Start Month Year" and "Client Segment" and calculate the average Total Premium
    yearly_avg_premium = df.groupby(['Start Year', 'Product_name'])['Total Premium'].mean().unstack().fillna(0)

    # Define custom colors

    with cols2:
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
            yaxis_title="Average Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height= 450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Average Premium Yearly by Product per Employer Group</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_avg_premium, use_container_width=True)


    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("Total Premium by Product over Time"):
            st.dataframe(area_chart_total_insured.style.format(precision=2))
        
    with cl2:  
            with st.expander("Yearly average premium"):
                    st.dataframe(yearly_avg_premium.style.format(precision=2))


    # Group data by "Cover Type" and "Product_name" and sum the Total Premium
    cover_product_premium = df.groupby(['Cover Type', 'Product_name'])['Total Premium'].sum().unstack().fillna(0)

    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls2:
        fig_cover_product_premium = go.Figure()


        for idx, product_name in enumerate(cover_product_premium.columns):
            fig_cover_product_premium.add_trace(go.Bar(
                x=cover_product_premium.index,
                y=cover_product_premium[product_name],
                name=product_name,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))

        # Set layout for the Total Premium chart
        fig_cover_product_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Cover Type",
            yaxis_title="Total Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Premium chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Premium Distribution by Cover Type and Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_cover_product_premium, use_container_width=True)



 # Calculate the Total Premium by Client Segment
    int_owner = df.groupby("Product_name")["Total Premium"].sum().reset_index()
    int_owner.columns = ["Product", "Total Premium"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Premium by Product</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Product", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 =st.columns(2)

    with cl2:  
            with st.expander("Premium by cover type and product"):
                    st.dataframe(cover_product_premium.style.format(precision=2))
    with cl1:  
            with st.expander("Total Product Premium"):
                    st.dataframe(int_owner.style.format(precision=2))


    # Group data by "Intermediary name" and sum the Total Premium
    premium_by_intermediary = df_health.groupby('Cover Type')['Total Premium'].sum().reset_index()

    # Calculate the number of sales by "Intermediary name"
    sales_by_cover = df_health.groupby('Cover Type').size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged_df = premium_by_intermediary.merge(sales_by_cover, on='Cover Type')

   # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Total Premium
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged_df['Cover Type'],
            y=merged_df['Total Premium'],
            text=merged_df['Total Premium'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Total Premium'
        ))


        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Cover Type",
            yaxis=dict(
                title="Total Premium",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),

            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Health Premium by Cover Type</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)


    # Group data by "Intermediary name" and sum the Total Premium
    premium_by_intermediary = df_proactiv.groupby('Cover Type')['Total Premium'].sum().reset_index()

    # Calculate the number of sales by "Intermediary name"
    sales_by_intermediary = df_proactiv.groupby('Cover Type').size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged_data = premium_by_intermediary.merge(sales_by_intermediary, on='Cover Type')


    with cls2:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Total Premium
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged_data['Cover Type'],
            y=merged_data['Total Premium'],
            text=merged_data['Total Premium'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Total Premium'
        ))


        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Cover Type",
            yaxis=dict(
                title="Total Premium",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),

            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total ProActiv Premium by Cover Type</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)

    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("Total Health sales by cover type"):
            st.dataframe(merged_df.style.format(precision=2))
        
    with cl2:  
            with st.expander("Total ProActiv sales by cover type"):
                    st.dataframe(merged_data.style.format(precision=2))

    # Group data by "Intermediary name" and sum the Total Premium
    premium_by_intermediary_name = df.groupby('Intermediary name')['Total Premium'].sum().reset_index()

    # Calculate the number of sales by "Intermediary name"
    sales_by_intermediary = df.groupby('Intermediary name').size().reset_index(name='Number of Sales')

    # Merge the premium and sales data
    merged = premium_by_intermediary_name.merge(sales_by_intermediary, on='Intermediary name')

   # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls2:
        fig_premium_by_intermediary = go.Figure()

        # Add bar trace for Total Premium
        fig_premium_by_intermediary.add_trace(go.Bar(
            x=merged['Intermediary name'],
            y=merged['Total Premium'],
            text=merged['Total Premium'],
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y',
            marker_color='#009DAE',
            name='Total Premium'
        ))


        # Set layout for the chart
        fig_premium_by_intermediary.update_layout(
            xaxis_title="Intermediary Name",
            yaxis=dict(
                title="Total Premium",
                titlefont=dict(color="#009DAE"),
                tickfont=dict(color="#009DAE")
            ),

            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Premium by Intermediary</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_premium_by_intermediary, use_container_width=True)

 # Calculate the Total Premium by Client Segment
    int_owner = df.groupby("Channel")["Total Premium"].sum().reset_index()
    int_owner.columns = ["Channel", "Total Premium"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Premium by Channel</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Channel", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("Total sales by channel"):
            st.dataframe(merged.style.format(precision=2))
        
    with cl2:  
            with st.expander("Total Channel Premium"):
                    st.dataframe(int_owner.style.format(precision=2))


    cl1, cl2 =st.columns(2)

 # Calculate the Total Premium by Client Segment
    int_owner = df.groupby("Client Segment")["Total Premium"].sum().reset_index()
    int_owner.columns = ["Segment", "Total Premium"]    

    with cl1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Premium by Client Segment</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Segment", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Total Health sales by client segment"):
            st.dataframe(merged.style.format(precision=2))
        
