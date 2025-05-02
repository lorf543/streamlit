import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Cargar datos desde SQLite
@st.cache_data
def load_data():
    conn = sqlite3.connect("data.db")
    df = pd.read_sql_query("SELECT * FROM campaigns", conn)
    conn.close()
    df.columns = df.columns.str.strip()
    df["Month"] = pd.to_datetime(df["Month"])
    return df

df = load_data()

vendors = df['VENDOR'].dropna().unique()
campaign_groups = df['Group'].dropna().unique()

selected_vendor = st.sidebar.multiselect("Select Vendor", vendors, default=list(vendors))
selected_group = st.sidebar.multiselect("Select Campaign Group", campaign_groups, default=list(campaign_groups))

filtered_df = df[
    (df['VENDOR'].isin(selected_vendor)) &
    (df['Group'].isin(selected_group))
]

available_months = sorted(df['Month'].dt.strftime('%Y-%m').unique())

st.markdown("""Analyzing campaign effectiveness through contact rate, close rate, revenue efficiency, and more.""")

st.subheader("📈 Comprehensive Campaign Performance Analysis")

selected_months_comp = st.multiselect(
    "Select months for comprehensive analysis",
    options=available_months,
    default=available_months,
    key="months_comprehensive"
)

comp_df = filtered_df[
    filtered_df['Month'].dt.strftime('%Y-%m').isin(selected_months_comp)
].copy()

numeric_cols = ['Contact Rate', 'Close rate', 'Revenue per hour', 'Revenue', 'Contacts']
for col in numeric_cols:
    comp_df[col] = pd.to_numeric(comp_df[col], errors='coerce')

if not comp_df.empty:
    campaign_stats = comp_df.groupby('Name of the campaign').agg({
        'Contact Rate': 'mean',
        'Close rate': 'mean',
        'Revenue per hour': 'mean',
        'Revenue': 'sum',
        'Contacts': 'sum'
    }).reset_index()
    
    campaign_stats_filled = campaign_stats.fillna(0)
    
    st.dataframe(campaign_stats.sort_values('Revenue per hour', ascending=False), use_container_width=True)
    
    tab1, tab2, tab3 = st.tabs(["Contact Rate", "Close Rate", "Revenue per Hour"])
    
    with tab1:
        contact_data = campaign_stats.dropna(subset=['Contact Rate']).sort_values('Contact Rate', ascending=False).head(20)
        fig_contact = px.bar(contact_data,
                            y='Name of the campaign',
                            x='Contact Rate',
                            title="Average Contact Rate by Campaign",
                            color='Contact Rate',
                            orientation='h',
                            height=600)
        st.plotly_chart(fig_contact, use_container_width=True)
    
    with tab2:
        close_data = campaign_stats.dropna(subset=['Close rate']).sort_values('Close rate', ascending=False).head(20)
        fig_close = px.bar(close_data,
                          y='Name of the campaign',
                          x='Close rate',
                          title="Average Close Rate by Campaign",
                          color='Close rate',
                          orientation='h',
                          height=600)
        st.plotly_chart(fig_close, use_container_width=True)
    
    with tab3:
        rev_data = campaign_stats.dropna(subset=['Revenue per hour']).sort_values('Revenue per hour', ascending=False).head(20)
        fig_rev = px.bar(rev_data,
                        y='Name of the campaign',
                        x='Revenue per hour',
                        title="Average Revenue per Hour by Campaign",
                        color='Revenue per hour',
                        orientation='h',
                        height=600)
        st.plotly_chart(fig_rev, use_container_width=True)

def create_section(title, df_section, y_column, x_column='Name of the campaign', top_n=5):
    st.subheader(title)
    
    selected_months = st.multiselect(
        f"Select months for {title}",
        options=available_months,
        default=available_months,
        key=f"months_{y_column}"
    )
    
    section_filtered = df_section[
        df_section['Month'].dt.strftime('%Y-%m').isin(selected_months)
    ]
    
    aggregated_data = section_filtered.groupby('Name of the campaign').agg({
        y_column: 'mean',
        'Month': 'count'
    }).reset_index()
    
    aggregated_data = aggregated_data.rename(columns={
        y_column: f"Average {y_column}",
        'Month': 'Months Included'
    })
    
    top_data = aggregated_data.sort_values(by=f"Average {y_column}", ascending=False).head(top_n)
    
    st.dataframe(top_data, use_container_width=True)
    
    if not top_data.empty:
        fig = px.bar(top_data, 
                     y=x_column, 
                     x=f"Average {y_column}", 
                     title=f"{title} - Top {top_n} (Average)",
                     color=f"Average {y_column}",
                     color_continuous_scale='Bluered',
                     orientation='h',
                     height=400)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for selected filters.")

create_section("Top Campaigns by Contact Rate", filtered_df, "Contact Rate")
create_section("Top Campaigns by Close Rate", filtered_df, "Close rate")
create_section("Top Campaigns by Revenue per Hour", filtered_df, "Revenue per hour")

st.markdown("---")
st.markdown("Doing great work is not enough. We need to make sure that our work is visible and that we are recognized for it. - Unknown")
st.markdown("Made with ❤️ by [Eduardo Sanchez]")
