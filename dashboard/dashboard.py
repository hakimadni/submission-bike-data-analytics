import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Choose Style
sns.set(style='dark')
plt.style.use('dark_background')
@st.cache_data
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/hakimadni/submission-bike-data-analytics/refs/heads/main/dashboard/all_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Sidebar
with st.sidebar:
    htp="https://raw.githubusercontent.com/hakimadni/submission-bike-data-analytics/main/rent_17677632.png"
    st.image(htp, caption= 'logo', width=350)
    st.sidebar.header('Filter Data')
    selected_year = st.sidebar.selectbox('Select Year', [2011, 2012, 'Both'])
    st.sidebar.header("Visit my Profile:")
    st.sidebar.markdown("Hakim Amal Adni")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.markdown("[![Github](https://img.icons8.com/glyph-neue/64/FFFFFF/github.png)](https://github.com/hakimadni)")
with col2:
    st.markdown("[![LinkedIn](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg)](https://www.linkedin.com/in/hakimadni/)")

if selected_year == 'Both':
    filtered_df = df
else:
    filtered_df = df[df['date'].dt.year == selected_year]

# Title and Description
st.title('Learning Data Analisys with Python')
st.write(f"Displaying data for {selected_year}" if selected_year != 'Both' else "Displaying data for both years")

col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = filtered_df.total.sum()
    st.metric("Total Rentals", value=total_rentals)
 
with col2:
    total_registered = filtered_df.registered.sum()
    st.metric("Total Registered Customer", value=total_registered)

with col3:
    total_casual = filtered_df.casual.sum()
    st.metric("Total Casual Customer", value=total_casual)


st.markdown("""
    This dashboard covers the following insights:
    - Monthly user by user Type
    - Bike rental trends by hour of the day (Workdays and Non-Workdays)
    - Influence of weather conditions on rentals
    """)

def create_monthly_df(df):
    monthly_df = df.resample(rule='M', on='date').agg({
        "registered": "sum",
        "casual": "sum",
        "total": "sum"
    })
    monthly_df = monthly_df.reset_index()
    return monthly_df

monthly_df = create_monthly_df(filtered_df)

st.subheader('Monthly Rentals')
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_df["date"], monthly_df["total"],
    marker='o', linewidth=2, label="Total", color="skyblue"
)
ax.plot(
    monthly_df["date"], monthly_df["registered"],
    marker='o', linewidth=2, label="Registered", color="orange"
)
ax.plot(
    monthly_df["date"], monthly_df["casual"],
    marker='o', linewidth=2, label="Casual", color="green"
)
ax.set_xlabel("Month", fontsize=15)
ax.set_ylabel("Customers", fontsize=15)
ax.set_title("Monthly Rentals", fontsize=20)
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=12)
ax.grid(True)
ax.legend(fontsize=12)

st.pyplot(fig)

st.subheader('Hourly Rentals')

def plot_bike_rentals_by_working_day():
    # Group and aggregate data
    data_sum_perjam = df.groupby(by=['hour', 'workingday']).agg({
        'casual': 'mean',
        'registered': 'mean',
        'total': 'mean'
    }).sort_values(by='hour', ascending=True).reset_index()

    # Separate data by working day
    data_wday = data_sum_perjam[data_sum_perjam['workingday'] == 'Yes'].reset_index()
    data_nwday = data_sum_perjam[data_sum_perjam['workingday'] == 'No'].reset_index()

    # Create the first plot for Working Days
    plt.figure(figsize=(15, 5))
    ax1 = data_wday[['casual', 'registered', 'total']].plot(
        color=['#f54242', '#f58d42', '#f58d42'],
        marker='o',
        ax=plt.gca(),
    )
    ax1.set_xticks(range(24))
    plt.grid(True, alpha=0.7)
    plt.title("Rata-rata Rental Sepeda per Jam (Working Days)")
    plt.xlabel("Jam")
    plt.ylabel("Jumlah Rental Sepeda")
    plt.tight_layout()
    st.pyplot(plt)  # Display first plot

    # Create the second plot for Non-Working Days
    plt.figure(figsize=(15, 5))
    ax2 = data_nwday[['casual', 'registered', 'total']].plot(
        color=['#42f5f2', '#428af5', '#6642f5'],
        marker='d',
        ax=plt.gca(),
    )
    ax2.set_xticks(range(24))
    plt.grid(True, alpha=0.7)
    plt.title("Rata-rata Rental Sepeda per Jam (Non-Working Days)")
    plt.xlabel("Jam")
    plt.ylabel("Jumlah Rental Sepeda")
    plt.tight_layout()
    st.pyplot(plt)

plot_bike_rentals_by_working_day()

# Hourly Bike Rentals by Weather Conditions
st.header('Bike Rentals by Weather Conditions')

def plot_bike_rentals_by_weather():
    data_per_cuaca = df.groupby(by=['hour', 'weathersit']).agg({
        'total': 'mean'
    }).sort_values(by='hour', ascending=True).reset_index()

    data_clear = data_per_cuaca[data_per_cuaca['weathersit'] == 'Clear'].reset_index()
    data_misty = data_per_cuaca[data_per_cuaca['weathersit'] == 'Misty'].reset_index()
    data_light_rainsnow = data_per_cuaca[data_per_cuaca['weathersit'] == 'Light_rainsnow'].reset_index()
    data_heavy_rainsnow = data_per_cuaca[data_per_cuaca['weathersit'] == 'Heavy_rainsnow'].reset_index()

    datasets = [
        (data_clear, '#1f77b4', 'Clear', 'o'),
        (data_misty, '#ab77b4', 'Misty', 'D'),
        (data_light_rainsnow, '#2ca02c', 'Light Rain/Snow', '*'),
        (data_heavy_rainsnow, '#8c564b', 'Heavy Rain/Snow', '>')
    ]

    plt.figure(figsize=(15, 10))
    for data, color, label, marker in datasets:
        ax = data.plot(
            x='hour', y='total', color=color, marker=marker, ax=plt.gca(),
            label=f"Total in {label}", linestyle='-'
        )
    ax.set_xticks(range(24))
    plt.grid(True, alpha=0.7)
    plt.title("Average Bike Rentals per Hour by Weather Condition")
    plt.xlabel("Hour")
    plt.ylabel("Average Rentals")
    plt.tight_layout()
    st.pyplot(plt)
plot_bike_rentals_by_weather()

st.caption('Copyright ©Hakim Amal Adni 2024')