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

st.markdown('<h1 class="main-title">KPI METRICS VIEW DASHBOARD</h1>', unsafe_allow_html=True)

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


df = pd.concat([df0, df1, df4])
df
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



# Dictionary to map month names to their order
month_order = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}

# Sort months based on their order
sorted_months = sorted(df['Start Month'].dropna().unique(), key=lambda x: month_order[x])


# Sidebar for filters
st.sidebar.header("Filters")
year = st.sidebar.multiselect("Select Year", options=sorted(df['Start Year'].dropna().unique()))
month = st.sidebar.multiselect("Select Month", options=sorted_months)
product = st.sidebar.multiselect("Select Product", options=df['Product_name'].unique())
cover = st.sidebar.multiselect("Select Cover Type", options=df['Cover Type'].unique())
segment = st.sidebar.multiselect("Select Client Segment", options=df['Client Segment'].unique())
channel = st.sidebar.multiselect("Select Channel", options=df['Channel'].unique())
team = st.sidebar.multiselect("Select Sales Team", options=df['Owner'].unique())
channel_name = st.sidebar.multiselect("Select Intermediary name", options=df['Intermediary name'].unique())
client_name = st.sidebar.multiselect("Select Client Name", options=df['Client Name'].unique())

# Apply filters to the DataFrame
if 'Start Year' in df.columns and year:
    df = df[df['Start Year'].isin(year)]
if 'Start Month' in df.columns and month:
    df = df[df['Start Month'].isin(month)]
if 'Product_name' in df.columns and product:
    df = df[df['Product_name'].isin(product)]
if 'Channel' in df.columns and channel:
    df = df[df['Channel'].isin(channel)]
if 'Owner' in df.columns and team:
    df = df[df['Owner'].isin(team)]
if 'Channel' in df.columns and channel_name:
    df = df[df['Channel'].isin(channel_name)]
if 'Client Segment' in df.columns and segment:
    df = df[df['Client Segment'].isin(segment)]
if 'Cover Type' in df.columns and cover:
    df = df[df['Cover Type'].isin(cover)]
if 'Client Name' in df.columns and client_name:
    df = df[df['Client Name'].isin(client_name)]

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
    filter_description = "All data"




# Calculate metrics
scaling_factor = 1_000_000

target_2024 = df["Target"].sum() / scaling_factor
df_proactiv_target_2024 = df[df['Product'] == 'ProActiv']
df_health_target_2024 = df[df['Product'] == 'Health']
df_renewals_2024 = df[df['Product'] == 'Renewals']

# Calculate Basic Premium RWFs for specific combinations
total_renewals_ytd = df_renewals_2024['Target'].sum() / scaling_factor
total_pro_target_ytd = df_proactiv_target_2024['Target'].sum() / scaling_factor
total_health_target_ytd = df_health_target_2024['Target'].sum() / scaling_factor

# Adjust the 'Target' column
df['Target'] = df['Target'] * (10 / 12)

# Add a 'Month' column for filtering
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October']
num_months = len(months)

# Create a new DataFrame to hold the replicated data
df_replicated = pd.DataFrame()

# Replicate the dataset for each month
for month in months:
    df_month = df.copy()
    df_month['Month'] = month
    df_replicated = pd.concat([df_replicated, df_month], ignore_index=True)

# Adjust the 'Target' column by dividing by the number of months
df_replicated['Target'] = df_replicated['Target'] / num_months


# Handle non-finite values in 'Start Year' column
df['Start Year'] = df['Start Year'].fillna(0).astype(int)  # Replace NaN with 0 or any specific value

# Handle non-finite values in 'Start Month' column
df['Start Month'] = df['Start Month'].fillna('Unknown')

# Create a 'Month-Year' column
df['Month-Year'] = df['Start Month'] + ' ' + df['Start Year'].astype(str)

# Function to sort month-year combinations
def sort_key(month_year):
    month, year = month_year.split()
    return (int(year), month_order.get(month, 0))  # Use .get() to handle 'Unknown' month

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

start_index = (int(start_year), month_order.get(start_month, 0))
end_index = (int(end_year), month_order.get(end_month, 0))

# Filter DataFrame based on month-year order indices
df = df[
    df['Month-Year'].apply(lambda x: (int(x.split()[1]), month_order.get(x.split()[0], 0))).between(start_index, end_index)
]


    # Filter the concatenated DataFrame to include only endorsements
df_endorsements_only = df[(df['Type'] == 'Endorsement')]
df_new = df[df['Cover Type'] == 'New Insured']
df_renew = df[df['Cover Type'] == 'Renew/Insured']
df_proactiv = df[df['Product_name'] == 'ProActiv']
df_health = df[df['Product_name'] == 'Health']

df_renew_2024 = df[df['Cover Type'] == 'Renew/Insured']
df_proactiv_2024 = df[df['Product_name'] == 'ProActiv']
df_health_2024 = df[df['Product_name'] == 'Health']

# Further filter by Cover Type within each product
df_proactiv_new = df_proactiv[df_proactiv['Cover Type'] == 'New Insured']
df_proactiv_renew = df_proactiv[df_proactiv['Cover Type'] == 'Renew/Insured']

df_health_new = df_health[df_health['Cover Type'] == 'New Insured']
df_health_renew = df_health[df_health['Cover Type'] == 'Renew/Insured']

df_proactiv_target = df[df['Product'] == 'ProActiv']
df_health_target = df[df['Product'] == 'Health']
df_renewals = df[df['Product'] == 'Renewals']



if not df.empty:

# Calculate the total premium for endorsements only

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

    # Calculate total premiums for specific combinations
    total_renewals = (df_renewals['Target'].sum())/scale
    total_pro_target = (df_proactiv_target['Target'].sum())/scale
    total_health_target = (df_health_target['Target'].sum())/scale
    total_health_target

    # Calculate total premiums for specific combinations
    total_renew_2024 = (df_renew_2024['Total Premium'].sum())/scale
    total_pro_2024 = (df_proactiv_2024['Total Premium'].sum())/scale
    total_health_2024 = (df_health_2024['Total Premium'].sum())/scale


    health_variance = (total_health_2024-total_health_target)
    health_percent_var = (health_variance/total_health_target) *100
    
    pro_variance = total_pro_2024-total_pro_target
    pro_percent_var = (pro_variance/total_pro_target) *100

    renew_variance = total_renew_2024-total_renewals
    renew_percent_var = (renew_variance/total_renewals) *100

    df["No. of staffs"] = pd.to_numeric(df["No. of staffs"], errors='coerce').fillna(0).astype(int)
    df["Dependents"] = pd.to_numeric(df["Dependents"], errors='coerce').fillna(0).astype(int)

    total_clients = df["Client Name"].nunique()
    total_pre = df["Basic Premium"].sum()
    total_in_pre = df["Total Premium"].sum()
    total_lives = df["Total lives"].sum()
    total_mem = df["No. of staffs"].sum()
    total_dependents = df["Dependents"].sum()
    average_dep = total_mem/total_dependents
    average_pre = df["Total Premium"].mean()
    average_premium_per_life = total_in_pre/total_mem
    gwp_average = total_lives * average_premium_per_life / total_clients




    # Scale the sums
    total_pre_scaled = total_pre / scaling_factor
    total_in_pre_scaled = total_in_pre / scaling_factor
    average_pre_scaled = average_pre/scaling_factor
    gwp_average_scaled = gwp_average/scaling_factor



    scaled = 1_000

    # Calculate key metrics
    lowest_premium = df['Total Premium'].min() /scaled
    highest_premium = df['Total Premium'].max() / scaling_factor

    # Create 4-column layout for metric cards# Define CSS for the styled boxes and tooltips
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
            position: relative;
        }
        .metric-title {
            color: #e66c37; /* Change this color to your preferred title color */
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #009DAE;
            font-size: 1em;
        }

        </style>
        """, unsafe_allow_html=True)



    # Function to display metrics in styled boxes with tooltips
    def display_metric(col, title, value):
        col.markdown(f"""
            <div class="metric-box">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)


    st.markdown('<h3 class="custom-subheader">For Health Insurance or ProActiv Sales</h3>', unsafe_allow_html=True)    


    # Display metrics
    col1, col2, col3= st.columns(3)
    display_metric(col1, f"Total Clients ({filter_description.strip()})", total_clients)
    display_metric(col2, f"Total Sales ({filter_description.strip()})", f"RWF {total_in_pre_scaled:.0f} M")
    display_metric(col3, "Total Principal Members", total_mem)
    display_metric(col1, "Average Sale Per Principal Member", f"RWF {average_pre_scaled:.0f}M")
    display_metric(col2, "Total Endorsement Sales", f"RWF {total_endorsement_premium:.0f} M")
    display_metric(col3, "Average Sale per Employer group", f"RWF {gwp_average_scaled:.0f} M")
    display_metric(col1, "Lowest Sale per Employer group", f"RWF {lowest_premium:.0f} K")
    display_metric(col2, "Highest Sale per Employer group", f"RWF {highest_premium:.0f} M",)
    display_metric(col3, "Total Target 2024", f"RWF {target_2024:.0f} M")


    grouped = df.groupby('Client Name')['Total lives'].median().reset_index()
    grouped.columns = ['Client Name', 'Median lives']
    # Calculate key metrics
    st.markdown('<h2 class="custom-subheader">For Lives Covered</h2>', unsafe_allow_html=True)    

    cols1,cols2, cols3, cols4 = st.columns(4)

    display_metric(cols1, "Total Lives", f"{total_lives:.0f}")
    display_metric(cols2, "Total Principal Members", total_mem)
    display_metric(cols3, "Total Dependents", total_dependents)
    display_metric(cols4, "Average Dependents Per Principal Member", f"{average_dep:.0f}")


    st.markdown('<h2 class="custom-subheader">For Health Insurance</h2>', unsafe_allow_html=True) 
    col1, col2, col3 = st.columns(3)
    display_metric(col1, "Total Health Sales", value=f"RWF {total_health:.0f} M")
    display_metric(col2, "Total New Health Sales", value=f"RWF {total_health_new:.0f} M")
    display_metric(col3, "Total Health Renewal Sales", value=f"RWF {total_health_renew:.0f} M")

    st.markdown('<h2 class="custom-subheader">For ProActiv Sales</h2>', unsafe_allow_html=True) 
    col1, col2, col3= st.columns(3)

    display_metric(col1, "Total ProActiv Sales", value=f"RWF {total_pro:.0f} M")
    display_metric(col2, "Total New ProActiv Sales", value=f"RWF {total_proactiv_new:.0f} M")
    display_metric(col3, "Total ProActiv Renewal Sales", value=f"RWF {total_proactiv_renew:.0f} M")

    st.markdown('<h2 class="custom-subheader">For Health Insurance Target</h2>', unsafe_allow_html=True) 
    col1, col2, col3= st.columns(3)

    display_metric(col1, "2024 Target Health Sales", f"RWF {total_health_target_ytd:.0f} M")
    display_metric(col2, "YTD Health Target Sales", f"RWF {total_health_target:.0f} M")
    display_metric(col3, "YTD Actual Health Sales", f"RWF {total_health_2024:.0f} M")
    display_metric(col1, "Variance", f"RWF {health_variance:.1f} M")
    display_metric(col2, "Percentage Variance", value=f"{health_percent_var:.2f} %")

    st.markdown('<h2 class="custom-subheader">For ProActiv Target</h2>', unsafe_allow_html=True) 
    col1, col2, col3= st.columns(3)

    display_metric(col1, "2024 Target ProActiv Sales", f"RWF {total_pro_target_ytd:.0f} M")
    display_metric(col2, "YTD ProActiv Target Sales", f"RWF {total_pro_target:.0f} M")
    display_metric(col3, "YTD Actual ProActiv Sales", f"RWF {total_pro_2024:.0f} M")
    display_metric(col1, "Variance", f"RWF {pro_variance:.0f} M")
    display_metric(col2, "Percentage Variance", value=f"{pro_percent_var:.0f} %")

    st.markdown('<h2 class="custom-subheader">For Renewals Target</h2>', unsafe_allow_html=True) 
    col1, col2, col3= st.columns(3)

    display_metric(col1, "2024 Target Renewal Sales", f"RWF {total_renewals_ytd:.0f} M")
    display_metric(col2, "YTD Renewal Target Sales", f"RWF {total_renewals:.0f} M")
    display_metric(col3, "YTD Actual Renewed Sales", f"RWF {total_renew_2024:.0f} M")
    display_metric(col1, "Variance", f"RWF {renew_variance:.0f} M")
    display_metric(col2, "Percentage Variance", value=f"{renew_percent_var:.0f} %")



