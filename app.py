from PIL import Image
import streamlit as st
import pandas as pd
import plotly.express as px


def plot_top_n_by_year(df, year, chart_type, top_n):
    column_name = f"{year} Population"
    
    if column_name not in df.columns:
        st.warning(f"{column_name} not found in dataset.")
        return pd.DataFrame() 

    top_df = df.nlargest(top_n, column_name).copy()

    hover_data = {
        column_name: True,
        "World Population Percentage": True
    }

    if chart_type == "Bar Chart":
        fig = px.bar(
        top_df.sort_values(by=column_name, ascending=False),
        x="Country/Territory",
        y=column_name,
        title=f"Top {top_n} Countries by Population in {year}",
        labels={column_name: "Population", "Country/Territory": "Country"},
        hover_data=hover_data,
    )
        fig.update_layout(xaxis_tickangle=-45)


    else:  
        fig = px.pie(
            top_df,
            values=column_name,
            names="Country/Territory",
            title=f"Top {top_n} Countries by Population in {year}",
            hole=0.3,  
            hover_data=hover_data,
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig, use_container_width=True)

    return top_df  


@st.cache_data
def load_data():
    df = pd.read_csv("world_population.csv")  
    return df

df = load_data()

st.set_page_config(page_title="World Population Dashboard", layout="wide")
st.title("🌍 World Population Insights Dashboard")
st.markdown("""
Welcome to the World Population Dashboard powered by **Plotly** and **Streamlit**.

- 🗺️ Explore population trends across decades  
- 📊 Compare metrics like **area**, **density**, **growth rate** and **global share**  
- 🔎 Interact with maps and bar charts for deeper insights  

""")

st.sidebar.title("Navigation")
st.sidebar.markdown("Use the main page to explore visualizations.")

tab1, tab2, tab3 = st.tabs(["🌐 World Map", "📅 Top 20 by Year", "📈 Metric Rankings"])

with tab1:
    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("🌐 Interactive World Map - 2022 Population")

    fig = px.choropleth(
        df,
        locations="CCA3",           
        color="2022 Population",         
        hover_name="Country/Territory",           
        hover_data={
            "Capital": True,
            "Area (km²)": True,
            "2022 Population": True,
            "CCA3": False           
        },
        color_continuous_scale="Viridis",  
        projection="natural earth",
        title="World Population by Country (2022)"
    )

    st.plotly_chart(fig, use_container_width=True)


with tab2:
    st.subheader("📊 Top N Countries by Population")

    selected_year = st.selectbox("Select Year", [2022, 2020, 2015, 2010, 2000, 1990, 1980, 1970])
    chart_type = st.radio("Select Chart Type", ["Bar Chart", "Pie Chart"], horizontal=True)
    top_n = st.slider("Select Top N Countries", min_value=5, max_value=50, step=5, value=10)

    filtered_df = plot_top_n_by_year(df, selected_year, chart_type, top_n)

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Top Countries as CSV",
        data=csv,
        file_name=f"top_{top_n}_countries_{selected_year}.csv",
        mime='text/csv',
    )

with tab3:
    st.subheader("🌍 Global Choropleth Map by Metric")

    metric_options = {
        "Area (km²)": "Area (km²)",
        "Density (per km²)": "Density (per km²)",
        "Growth Rate": "Growth Rate",
        "World Population Percentage": "World Population Percentage",
        "2022 Population": "2022 Population",
    }

    selected_metric_label = st.selectbox("Select a metric to visualize:", list(metric_options.keys()))
    selected_metric = metric_options[selected_metric_label]

    if selected_metric not in df.columns:
        st.warning(f"{selected_metric} not found in dataset.")

    selected_metric_label = selected_metric

    if selected_metric in ["Density (per km²)", "Growth Rate"]:
        low = df[selected_metric].quantile(0.05)
        high = df[selected_metric].quantile(0.95)
        range_color = [low, high]
    else:
        range_color = [df[selected_metric].min(), df[selected_metric].max()]

    fig = px.choropleth(
        df,
        locations="Country/Territory",
        locationmode="country names",
        color=selected_metric,
        hover_name="Country/Territory",
        color_continuous_scale="Viridis",
        range_color=range_color,
        title=f"World Map by {selected_metric_label}",
    )


    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)

image = Image.open("logo.jpg")  
st.sidebar.image(image, caption='By Ahmad Tanveer', use_container_width=True)

st.markdown("---")
st.markdown("Made with ❤️ by **Ahmad Tanveer** | Powered by Streamlit & Plotly")
