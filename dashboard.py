import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Bike Sharing", layout="wide")
st.title("Dashboard Analisis Bike Sharing Dataset")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Main_Data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['weekend'] = df['weekday'].apply(lambda x: 1 if x in [0, 6] else 0)
    df['season_name'] = df['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
    df['hr_label'] = df['hr'].apply(lambda x: f"{x:02d}:00")
    df.rename(columns={'cnt': 'total_count'}, inplace=True)
    return df

data = load_data()

st.subheader("📄 Dataset Bike Sharing")

show_all = st.checkbox("Tampilkan Seluruh Dataset")
if show_all:
    st.dataframe(data, use_container_width=True)
else:
    st.dataframe(data.head(20), use_container_width=True)

pivot_casual_registered = data.groupby('weekend')[['casual', 'registered']].sum()
pivot_casual_registered.index = pivot_casual_registered.index.map({0: 'Weekday', 1: 'Weekend'})
pivot_casual_registered['total'] = pivot_casual_registered['casual'] + pivot_casual_registered['registered']

st.subheader("📊 Penggunaan Sepeda oleh Casual vs Registered (Weekday vs Weekend)")
st.dataframe(pivot_casual_registered, use_container_width=True)

fig1, ax1 = plt.subplots(figsize=(8, 5))
pivot_casual_registered[['casual', 'registered']].plot(
    kind='bar',
    stacked=False,
    color=['#64b5f6', '#f06292'],
    ax=ax1,
    width=0.6
)
ax1.set_title('Penggunaan Sepeda Weekday vs Weekend')
ax1.set_xticklabels(pivot_casual_registered.index, rotation=0)
ax1.set_xlabel('')
ax1.grid(axis='y', linestyle='--', alpha=0.5)
ax1.legend(title='Tipe Pengguna')

y_max = pivot_casual_registered[['casual', 'registered']].values.max()
interval = 250000
y_ticks = list(range(0, int(y_max + interval), interval))
ax1.set_yticks(ticks=y_ticks)
ax1.set_yticklabels([f"{y:,}" for y in y_ticks])

st.pyplot(fig1)

# Pivot Table: Rata-rata penggunaan sepeda per jam per musim
pivot_jam_musim = data.pivot_table(
    index='hr_label',
    columns='season_name',
    values='total_count',
    aggfunc='mean'
).round(1)

pivot_jam_musim_reset = pivot_jam_musim.copy()
pivot_jam_musim_reset['hr'] = [int(h.split(':')[0]) for h in pivot_jam_musim.index]
pivot_jam_musim_reset.set_index('hr', inplace=True)

st.subheader("🕒 Rata-rata Penggunaan Sepeda per Jam per Musim")
st.dataframe(pivot_jam_musim, use_container_width=True)

fig2, ax2 = plt.subplots(figsize=(12, 6))
for season in pivot_jam_musim_reset.columns:
    ax2.plot(
        pivot_jam_musim_reset.index,
        pivot_jam_musim_reset[season],
        marker='o',
        label=season
    )

jam_labels = [f'{h:02d}.00' for h in pivot_jam_musim_reset.index]
ax2.set_xticks(pivot_jam_musim_reset.index)
ax2.set_xticklabels(jam_labels, rotation=45)
ax2.set_title('Rata-rata Penggunaan Sepeda per Jam per Musim')
ax2.set_ylabel('Rata-rata Jumlah Pengguna')
ax2.set_xlabel('Jam')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend(title='Musim')

st.pyplot(fig2)

# Heatmap Total Penggunaan Sepeda berdasarkan Waktu & Musim
data_clustered = data.copy()
data_clustered['total'] = data_clustered['casual'] + data_clustered['registered']

def time_of_day(hr):
    if 6 <= hr < 10:
        return 'Morning Peak'
    elif 10 <= hr < 16:
        return 'Daytime'
    elif 16 <= hr < 20:
        return 'Evening Peak'
    else:
        return 'Night'

data_clustered['time_cluster'] = data_clustered['hr'].apply(time_of_day)
season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
data_clustered['season_name'] = data_clustered['season'].map(season_map)

pivot_heatmap = data_clustered.groupby(['time_cluster', 'season_name'])['total'].sum().unstack().fillna(0)

st.subheader("🔥 Heatmap Total Penggunaan Sepeda berdasarkan Waktu & Musim")
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.heatmap(
    pivot_heatmap,
    annot=True,
    fmt='.0f',
    cmap='YlGnBu',
    linewidths=0.3,
    linecolor='gray',
    cbar_kws={'label': 'Total Penggunaan Sepeda'},
    ax=ax3
)
ax3.set_title('Total Penggunaan Sepeda berdasarkan Waktu & Musim')
ax3.set_ylabel('Waktu')
ax3.set_xlabel('Musim')

st.pyplot(fig3)

st.markdown("---")
st.caption("Made Wisnu Widana — Proyek Analisis Data Dicoding • 2025")