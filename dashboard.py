import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from db_config import engine

st.set_page_config(
    page_title="MyBank Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)
st.markdown("""
<style>
.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
}
.metric-title {
    font-size: 14px;
    color: #9CA3AF;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    interactions = pd.read_sql("SELECT * FROM interactions", engine)
    transactions = pd.read_sql("SELECT * FROM transactions", engine)
    return interactions, transactions

interactions, transactions = load_data()

interactions['event_type'] = interactions['event_type'].str.lower()
st.title("🏦 MyBank Personalization Analytics")
st.caption("Dashboard monitoring CTR & user engagement")

# KPI SECTION
click = interactions[interactions['event_type'] == 'click'].shape[0]
view = interactions[interactions['event_type'] == 'view'].shape[0]
ctr = (click / view * 100) if view > 0 else 0

col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div class="metric-card">
<div class="metric-title">Total Click</div>
<div class="metric-value">{click}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="metric-card">
<div class="metric-title">Total View</div>
<div class="metric-value">{view}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="metric-card">
<div class="metric-title">CTR (%)</div>
<div class="metric-value">{ctr:.2f}%</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# CTR PER USER
st.subheader("👤 CTR per User")

ctr_user = interactions.groupby('no_rek').agg(
    click_count=('event_type', lambda x: (x == 'click').sum()),
    view_count=('event_type', lambda x: (x == 'view').sum())
).reset_index()

ctr_user['ctr'] = ctr_user.apply(
    lambda x: (x['click_count'] / x['view_count'] * 100)
    if x['view_count'] > 0 else 0,
    axis=1
)

fig_user = px.bar(
    ctr_user.sort_values(by='ctr', ascending=False).head(10),
    x='no_rek',
    y='ctr',
    title="Top 10 User CTR",
    labels={'ctr': 'CTR (%)', 'no_rek': 'User'}
)

st.plotly_chart(fig_user, use_container_width=True)

# CTR PER KATEGORI
st.subheader("📂 CTR per Kategori")

merged = interactions.merge(transactions, on='no_rek', how='inner')

ctr_kategori = merged.groupby('kategori').agg(
    click_count=('event_type', lambda x: (x == 'click').sum()),
    total_event=('event_type', 'count')
).reset_index()

ctr_kategori['ctr'] = (
    ctr_kategori['click_count'] / ctr_kategori['total_event'] * 100
)

fig_kat = px.pie(
    ctr_kategori,
    names='kategori',
    values='ctr',
    title="Distribusi CTR per Kategori"
)

st.plotly_chart(fig_kat, use_container_width=True)

# INSIGHT SECTION
st.subheader("🧠 Insight Otomatis")

top_kategori = ctr_kategori.sort_values(by='ctr', ascending=False).iloc[0]

st.info(f"""
Kategori dengan CTR tertinggi adalah **{top_kategori['kategori']}** 
dengan CTR sebesar **{top_kategori['ctr']:.2f}%**.
""")

# USER DRILL DOWN
st.subheader("🔍 User Drill Down")

selected_user = st.selectbox(
    "Pilih User",
    interactions['no_rek'].unique()
)

user_data = interactions[interactions['no_rek'] == selected_user]

st.write("Riwayat Interaksi User:")
st.dataframe(user_data, use_container_width=True)