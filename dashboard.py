import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    layout="centered",
)

st.title("Beijing Air Quality")

st.divider()

def load_data():
    df = pd.read_csv('https://haneya.space/data/stacked_data.csv')
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    return df

df = load_data()


st.sidebar.header("Input Informasi")
min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_selection = st.sidebar.date_input(
    label='Pilih Tanggal atau Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]  
)

if len(date_selection) == 2:
    start_date, end_date = date_selection
elif len(date_selection) == 1:
    start_date = date_selection[0]
    end_date = date_selection[0]
else:
    st.error("Pilih setidaknya satu tanggal")
    st.stop()

main_df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]

pollutants = ["PM2.5", "PM10", "SO2", "NO2", "CO"]
selected_pollutant = st.sidebar.selectbox("Pilih Polutan untuk Dianalisis:", pollutants)

stations = df['station'].unique()
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun untuk grafik polutan udara Beijing (Kosongkan untuk Rata-rata Semua):",
    options=stations,
    default=[] 
)

st.header("Konsentrasi Polutan Udara Beijing")

hourly_avg = main_df.groupby('hour')[selected_pollutant].mean()


if start_date == end_date:
    st.write(f"Konsentrasi per Jam **{selected_pollutant}** pada tanggal **{start_date}**.")
else:
    st.write(f"Konsentrasi per Jam **{selected_pollutant}** dari **{start_date}** hingga **{end_date}**.")

avg_fig, avg_ax = plt.subplots(figsize=(12, 6))

if not selected_stations:
    avg_all = main_df.groupby('hour')[selected_pollutant].mean()
    avg_ax.plot(avg_all.index, 
                avg_all.values, 
                marker="o", 
                color="crimson", 
                linewidth=3, 
                label="Rata-rata Seluruh Stasiun")
    st.write(f"Menampilkan tren rata-rata **seluruh stasiun** di Beijing.")
else:
    for station in selected_stations:
        station_data = main_df[main_df['station'] == station].groupby('hour')[selected_pollutant].mean()
        avg_ax.plot(station_data.index, 
                    station_data.values, 
                    marker="o", 
                    label=station, 
                    linewidth=2)
    st.write(f"Menampilkan tren untuk stasiun: **{', '.join(selected_stations)}**.")

avg_ax.set_title(f"Tren Kadar {selected_pollutant} per Jam", fontsize=14)
avg_ax.set_xlabel('Jam (0-23)', fontsize=12)
avg_ax.set_ylabel(f'Konsentrasi {selected_pollutant} (ug/m^3)', fontsize=12)
avg_ax.set_xticks(range(0, 24))
avg_ax.legend(loc='upper right', bbox_to_anchor=(1, 1), title='Stasiun')
avg_ax.grid(True, alpha=0.3)
st.pyplot(avg_fig, bbox_inches='tight')

st.divider()

st.header("Perbedaan Kualitas Udara Antar Stasiun")
if start_date == end_date:
    st.write(f"Peringkat stasiun berdasarkan data yang telah diurutkan dari terbersih hingga terkotor **{selected_pollutant}** pada tanggal **{start_date}**.")
else:
    st.write(f"Peringkat stasiun berdasarkan data yang telah diurutkan dari terbersih hingga terkotor dari **{start_date}** hingga **{end_date}**.")

station_avg = main_df.groupby('station')[pollutants].mean()

station_normalized = (station_avg - station_avg.min()) / (station_avg.max() - station_avg.min())
station_normalized['score'] = station_normalized.mean(axis=1)

score_df = station_normalized[['score']].sort_values(by='score', ascending=False)

score_fig, score_ax = plt.subplots(figsize=(12, 7))
sns.barplot(x=score_df['score'], y=score_df.index, ax=score_ax, palette="YlOrRd_r")
score_ax.set_title('Peringkat Tingkat Polusi Relatif per Stasiun', fontsize=14)
score_ax.set_xlabel('Skala Polusi Relatif (0 = Terbersih, 1 = Terkotor)', fontsize=12)
score_ax.set_ylabel('Stasiun', fontsize=12)
score_ax.grid(axis='x', alpha=0.6)

st.pyplot(score_fig)
