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

st.markdown('<h1 class="main-title">PREMIUM VIEW</h1>', unsafe_allow_html=True)

filepath="WRITTEN PREMIUM 2024.xlsx"
sheet_name = "NEW BUSINES"
sheet_name1 ="ENDORSMENTS"
sheet_name2= "ProActiv"
sheet_name3="Monthly Sales"
sheet_name4="Target"
# Read all sheets into a dictionary of DataFrames
df0 = pd.read_excel(filepath, sheet_name=sheet_name)
df1=pd.read_excel(filepath, sheet_name=sheet_name1)
df2=pd.read_excel(filepath, sheet_name=sheet_name2)
df3=pd.read_excel(filepath, sheet_name=sheet_name3)
df4=pd.read_excel(filepath, sheet_name=sheet_name4)




# Ensure the 'Start Date' column is in datetime format
df1['Start Date'] = pd.to_datetime(df1['Start Date'], errors='coerce')
# Filter rows where the Start Date is in 2024
df1 = df1[df1['Start Date'].dt.year == 2024]

df4['Target'] = df4['Target'] * (9 / 12)

df4['Target'] = df4['Target'] / 9

# Add a 'Month' column for filtering
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']

# Create a DataFrame for each month from January to September
expanded_rows = []
for _, row in df4.iterrows():
    for month in months:
        expanded_rows.append([row['Product'], row['Owner'], month, row['Target']])

# Create the expanded DataFrame
df_expanded = pd.DataFrame(expanded_rows, columns=['Product', 'Owner', 'Start Month', 'Target'])



df4 = pd.concat([df4]*9, ignore_index=True)
df4['Start Month'] = months * (len(df4) // len(months))

df = pd.concat([df0, df1, df4])
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
df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')


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
product = st.sidebar.multiselect("Select Product", options=df['Product'].unique())
owner = st.sidebar.multiselect("Select Owner", options=df['Owner'].unique())
channel_name = st.sidebar.multiselect("Select Intermediary Name", options=df['Intermediary name'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())



# Apply filters to the DataFrame
if month:
    df = df[df['Start Month'].isin(month)]
if cover:
    df = df[df['Cover Type'].isin(cover)]
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
if product:
    filter_description += f"{', '.join(product)} "
if owner:
    filter_description += f"{', '.join(owner)} "
if channel_name:
    filter_description += f"{', '.join(channel_name)} "
if client_name:
    filter_description += f"{', '.join(client_name)} "
if not filter_description:
    filter_description = "All data"

if not df.empty:
     # Calculate metrics
    scaling_factor = 1_000_000_000
    scale=1_000_000  # For millions

    total_pre = df0["Total Premium"].sum()
    total_in_pre = df["Total Premium"].sum()
    total_target = (df["Target"].sum())/scaling_factor
    # Scale the sums
    total_pre_scaled = total_pre / scaling_factor
    total_in_pre_scaled = total_in_pre / scaling_factor
    variance = total_in_pre_scaled-total_target
    percent_var = (variance/total_target) *100
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
    display_metric(col1, f"Total Premuim ({filter_description.strip()})", value=f"RWF {total_pre_scaled:.1f} B")
    display_metric(col2, "Total Premium with Endorsement", f"RWF {total_in_pre_scaled:.1f} B")
    display_metric(col3, f"Target Premium ({filter_description.strip()})", value=f"RWF{total_target:.1f} B")
    display_metric(col1, "Variance", f"RWF {variance:.1f} B")
    display_metric(col2, f"Percentage Variance ({filter_description.strip()})", value=f"RWF {percent_var:.0f} %")



   
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

    custom_colors = ["#006E7F", "#e66c37", "#461b09", "#f8a785", "#CC3636"]


    # Group data by "Owner" and calculate the total Target and Total Premium
    yearly_totals = df.groupby('Owner')[['Target', 'Total Premium']].sum().fillna(0)

    with cols1:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Target
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals.index,
            y=yearly_totals['Target'],
            name='Target',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0],  # Use the first custom color for Target
            offsetgroup=0
        ))

        # Add bars for Total Premium
        fig_yearly_totals.add_trace(go.Bar(
            x=yearly_totals.index,
            y=yearly_totals['Total Premium'],
            name='Total Premium',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1],  # Use the second custom color for Total Premium
            offsetgroup=1
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Owner",
            yaxis_title="Total Values",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Target and Premium by Owner</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)


    # Group data by "Owner" and calculate the total Target and Total Premium
    product_totals = df.groupby('Product')[['Target', 'Total Premium']].sum().fillna(0)

    with cols2:
        # Create the grouped bar chart
        fig_yearly_totals = go.Figure()

        # Add bars for Target
        fig_yearly_totals.add_trace(go.Bar(
            x=product_totals.index,
            y=product_totals['Target'],
            name='Target',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[0],  # Use the first custom color for Target
            offsetgroup=0
        ))

        # Add bars for Total Premium
        fig_yearly_totals.add_trace(go.Bar(
            x=product_totals.index,
            y=product_totals['Total Premium'],
            name='Total Premium',
            textposition='inside',
            textfont=dict(color='white'),
            hoverinfo='x+y+name',
            marker_color=custom_colors[1],  # Use the second custom color for Total Premium
            offsetgroup=1
        ))

        fig_yearly_totals.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Owner",
            yaxis_title="Total Values",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Target and Premium by Owner</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)

 

    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Target and premuim by Owner"):
            st.dataframe(yearly_totals.style.format(precision=2))
        
    with ccl2:
        # Expander for IQR table
        with st.expander("Target and premuim by Product"):
            st.dataframe(product_totals.style.format(precision=2))

   # Create the layout columns
    cls1, cls2 = st.columns(2)
# Count the occurrences of each Status
    prod_counts = df["Owner"].value_counts().reset_index()
    prod_counts.columns = ["Owner", "Count"]

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Number of Sales By Owners</h3>', unsafe_allow_html=True)

        # Create a donut chart
        fig = px.pie(prod_counts, names="Owner", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


# Count the occurrences of each Status
    prod_counts = df["Channel"].value_counts().reset_index()
    prod_counts.columns = ["Channel", "Count"]

    with cls2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Number of Sales By Channel</h3>', unsafe_allow_html=True)

        # Create a donut chart
        fig = px.pie(prod_counts, names="Channel", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)





    # Group data by "Start Date Month" and "Client Segment" and sum the Total Premium
    monthly_product = df.groupby(['Start Month', 'Product'])['Total Premium'].sum().unstack().fillna(0)

    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:
        fig_monthly_premium = go.Figure()

        for idx, Client_Segment in enumerate(monthly_product.columns):
            fig_monthly_premium.add_trace(go.Bar(
                x=monthly_product.index,
                y=monthly_product[Client_Segment],
                name=Client_Segment,
                textposition='inside',
                textfont=dict(color='white'),
                hoverinfo='x+y+name',
                marker_color=custom_colors[idx % len(custom_colors)]  # Cycle through custom colors
            ))


        # Set layout for the Total Premium chart
        fig_monthly_premium.update_layout(
            barmode='group',  # Grouped bar chart
            xaxis_title="Start Date",
            yaxis_title="Total Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Premium chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Sales Distribution by Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)


    # Group data by "Start Date Month" and "Client Segment" and sum the Total Premium
    monthly_premium = df.groupby(['Start Month', 'Owner'])['Total Premium'].sum().unstack().fillna(0)


    with cls2:
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
            xaxis_title="Start Date",
            yaxis_title="Total Premium",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
        )

        # Display the Total Premium chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Monthly Sales Distribution by Owner</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_monthly_premium, use_container_width=True)

    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("Target and premuim by Owner"):
            st.dataframe(monthly_product.style.format(precision=2))
        
    with cl2:
        # Expander for IQR table
        with st.expander("Target and premuim by Product"):
            st.dataframe(monthly_premium.style.format(precision=2))

 # Calculate the Total Premium by Client Segment
    int_premiums = df.groupby("Product")["Total Premium"].sum().reset_index()
    int_premiums.columns = ["Product", "Total Premium"]    

    # Create the layout columns
    cls1, cls2 = st.columns(2)

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Premium by Product</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_premiums, names="Product", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)


 # Calculate the Total Premium by Client Segment
    int_owner = df.groupby("Owner")["Total Premium"].sum().reset_index()
    int_owner.columns = ["Owner", "Total Premium"]    

    with cls2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Premium by Owner</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig = px.pie(int_owner, names="Owner", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("Target and premuim by Owner"):
            st.dataframe(int_premiums.style.format(precision=2))
        
    with cl2:
        with st.expander("Target and premuim by Product"):
            st.dataframe(int_owner.style.format(precision=2))


    colc1, colc2 = st.columns(2)
    
    # Function to format y-axis labels in millions
    def millions(x, pos):
        'The two args are the value and tick position'
        return '%1.0fM' % (x * 1e-6)

    # Group by day and Client Segment, then sum the Total Premium
    area_chart_total_insured = df.groupby([df["Start Date"].dt.strftime("%Y-%m-%d"), 'Product'])['Total Premium'].sum().reset_index(name='Total Premium')

    # Sort by the START DATE
    area_chart_total_insured = area_chart_total_insured.sort_values("Start Date")


    with colc1:
        # Create the area chart for Total Premium
        fig1, ax1 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_insured = area_chart_total_insured.pivot(index='Start Date', columns='Product', values='Total Premium').fillna(0)
        
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
        st.markdown('<h2 class="custom-subheader">Total Premium by Product Over Time</h2>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig1)

    # Group by day and Client Segment, then sum the Total Lives
    area_chart_total_lives = df.groupby([df["Start Date"].dt.strftime("%Y-%m-%d"), 'Owner'])['Total Premium'].sum().reset_index(name='Total Premium')

    # Sort by the START DATE
    area_chart_total_lives = area_chart_total_lives.sort_values("Start Date")

    with colc2:
        # Create the area chart for Total Lives Covered
        fig2, ax2 = plt.subplots()

        # Pivot the DataFrame for easier plotting
        pivot_df_lives = area_chart_total_lives.pivot(index='Start Date', columns='Owner', values='Total Premium').fillna(0)
        
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
        st.markdown('<h2 class="custom-subheader">Total Sales by Owners Over Time</h2>', unsafe_allow_html=True)

        # Display the chart in Streamlit
        st.pyplot(fig2)

    # Group by Client Name and Client Segment, then sum the Total Premium
    df_grouped = df.groupby(['Client Name', 'Owner'])['Total Premium'].sum().reset_index()

    # Get the top 10 clients by Total Premium
    top_10_clients = df_grouped.groupby('Client Name')['Total Premium'].sum().reset_index()

    # Filter the original DataFrame to include only the top 10 clients
    client_df = df_grouped[df_grouped['Client Name'].isin(top_10_clients['Client Name'])]
    # Sort the client_df by Total Premium in descending order
    client_df = client_df.sort_values(by='Total Premium', ascending=False)

        # Create the bar chart
    fig = go.Figure()


            # Add bars for each Client Segment
    for idx, Client_Segment in enumerate(client_df['Owner'].unique()):
                Client_Segment_data = client_df[client_df['Owner'] == Client_Segment]
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
    st.markdown('<h2 class="custom-subheader">Client Premium by Owners</h2>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

  
    with st.expander("Target and premuim by Owner"):
            st.dataframe(client_df.style.format(precision=2))