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

st.markdown('<h1 class="main-title">SALES AND TARGET VIEW</h1>', unsafe_allow_html=True)

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
df0['Start Date'] = pd.to_datetime(df0['Start Date'], errors='coerce')

# Filter rows where the Start Date is in 2024
df1 = df1[df1['Start Date'].dt.year == 2024]
df0 = df0[df0['Start Date'].dt.year == 2024]

     # Calculate metrics
scaling_factor = 1_000_000

target_2024 = (df4["Target"].sum())/scaling_factor

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
df4['Start Year'] = 2024




df = pd.concat([df0, df1, df4])


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
product = st.sidebar.multiselect("Select Product", options=df['Product'].unique())
owner = st.sidebar.multiselect("Select Sales Team", options=df['Owner'].unique())
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
df_endorsements_only = df[df['Type'] == 'Endorsement']
df_new = df[df['Product'] == 'Health']
df_renew = df[df['Product'] == 'Renewals']
df_proactiv = df[df['Product'] == 'ProActiv']


# Calculate the total premium for endorsements only
# Assuming the column name for the premium is 'Total Premium'

if not df.empty:
     # Calculate metrics
    scale=1_000_000  # For millions

    total_pre = df["Total Premium"].sum()
    total_in_pre = df["Total Premium"].sum()
    total_target = (df["Target"].sum())/scale
    # Scale the sums
    total_pre_scaled = total_pre / scale
    total_in_pre_scaled = total_in_pre / scale
    variance = total_in_pre_scaled-total_target
    percent_var = (variance/total_target) *100

    total_endorsement_premium = (df_endorsements_only['Total Premium'].sum())/scale
    total_new = (df_new['Total Premium'].sum())/scale
    total_renew = (df_renew['Total Premium'].sum())/scale
    total_pro = (df_proactiv['Total Premium'].sum())/scale

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
    display_metric(col1, f"Total Premuim ({filter_description.strip()})", value=f"RWF {total_pre_scaled:.0f} M")
    display_metric(col2, "Total Endorsement", f"RWF {total_endorsement_premium:.0f} M")
    display_metric(col3, "2024 Target", f"RWF {target_2024:.0f} M")
    display_metric(col1, f"Target Premium ({filter_description.strip()})", value=f"RWF {total_target:.0f} M")
    display_metric(col2, "Variance", f"RWF {variance:.0f} M")
    display_metric(col3, f"Percentage Variance ({filter_description.strip()})", value=f"RWF {percent_var:.0f} %")
    display_metric(col1, "Total New Sales", value=f"RWF {total_new:.0f} M")
    display_metric(col2, "Total Renewals", value=f"RWF {total_renew:.0f} M")
    display_metric(col3, "Total ProActiv Sales", value=f"RWF {total_pro:.0f} M")


   
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
        st.markdown('<h3 class="custom-subheader">Total Target and Premium by Sales Team</h3>', unsafe_allow_html=True)
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
            xaxis_title="Product",
            yaxis_title="Total Values",
            font=dict(color='Black'),
            xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
            margin=dict(l=0, r=0, t=30, b=50),
            height=450
        )

        # Display the chart in Streamlit
        st.markdown('<h3 class="custom-subheader">Total Target and Premium by Product</h3>', unsafe_allow_html=True)
        st.plotly_chart(fig_yearly_totals, use_container_width=True)

 

    ccl1, ccl2 = st.columns(2)
    with ccl1:
        with st.expander("Target and premuim by Owner"):
            st.dataframe(yearly_totals.style.format(precision=2))
        
    with ccl2:
        # Expander for IQR table
        with st.expander("Target and premuim by Product"):
            st.dataframe(product_totals.style.format(precision=2))

    cls1, cls2 = st.columns(2)

 # Calculate the Total Premium by Client Segment
    int_owner = df.groupby("Owner")["Total Premium"].sum().reset_index()
    int_owner.columns = ["Owner", "Total Premium"]    

    with cls1:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Total Premium by Sales Team</h3>', unsafe_allow_html=True)


        # Create a donut chart
        fig_owner = px.pie(int_owner, names="Owner", values="Total Premium", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig_owner.update_traces(textposition='inside', textinfo='value+percent')
        fig_owner.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig_owner, use_container_width=True)

# Count the occurrences of each Status
    prod_counts = df["Owner"].value_counts().reset_index()
    prod_counts.columns = ["Owner", "Count"]

    with cls2:
        # Display the header
        st.markdown('<h3 class="custom-subheader">Number of Sales By Sales Team</h3>', unsafe_allow_html=True)

        # Create a donut chart
        fig = px.pie(prod_counts, names="Owner", values="Count", hole=0.5, template="plotly_dark", color_discrete_sequence=custom_colors)
        fig.update_traces(textposition='inside', textinfo='value+percent')
        fig.update_layout(height=450, margin=dict(l=0, r=10, t=30, b=50))

        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    cl1, cl2 =st.columns(2)

    with cl1:
        with st.expander("TotalPremium by Sales Team"):
            st.dataframe(prod_counts.style.format(precision=2))
        
    with cl2:
        with st.expander("Number of Sales by Sales Team"):
            st.dataframe(int_owner.style.format(precision=2))

