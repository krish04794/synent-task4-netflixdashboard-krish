import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title='Task 4 Interactive Dashboard',
    layout='wide',
    initial_sidebar_state='expanded',
)

ROOT = Path(__file__).resolve().parent
SAMPLE_PATH = ROOT.parent / 'netflix_titles.csv'

st.title('Task 4: Interactive Dashboard')
st.markdown(
    'Upload a dataset or use the sample Netflix dataset, then explore it with interactive charts.'
)

with st.sidebar:
    st.header('Dataset Controls')
    uploaded_file = st.file_uploader('Upload CSV dataset', type=['csv'])
    if uploaded_file is None:
        if SAMPLE_PATH.exists():
            st.info('Using sample dataset from `netflix_titles.csv`.')
        else:
            st.warning('No dataset uploaded and sample dataset not found.')


def load_data():
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    if SAMPLE_PATH.exists():
        return pd.read_csv(SAMPLE_PATH)
    return None


data = load_data()

if data is None:
    st.stop()

# Ensure we have consistent column names
data.columns = [str(col) for col in data.columns]

numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
categorical_columns = data.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
all_columns = data.columns.tolist()

st.sidebar.header('Chart Settings')
chart_type = st.sidebar.selectbox('Chart type', ['Bar', 'Line', 'Scatter', 'Histogram', 'Pie', 'Box'])

x_axis = st.sidebar.selectbox('X axis', all_columns, index=0)
y_axis = None
if chart_type in ['Bar', 'Line', 'Scatter', 'Box']:
    y_axis = st.sidebar.selectbox('Y axis', numeric_columns or all_columns, index=0)
color = st.sidebar.selectbox('Color', ['None'] + all_columns, index=0)

st.sidebar.header('Data Filters')
filtered_data = data.copy()

for column in numeric_columns:
    min_val = float(data[column].min())
    max_val = float(data[column].max())
    if min_val < max_val:
        selected_range = st.sidebar.slider(
            f'{column} range', min_val, max_val, (min_val, max_val), step=(max_val - min_val) / 100 if max_val != min_val else 1.0
        )
        filtered_data = filtered_data[(filtered_data[column] >= selected_range[0]) & (filtered_data[column] <= selected_range[1])]

for column in categorical_columns:
    unique_values = data[column].dropna().unique().tolist()
    if 1 < len(unique_values) <= 25:
        selected_values = st.sidebar.multiselect(f'{column} values', unique_values, default=unique_values)
        if selected_values:
            filtered_data = filtered_data[filtered_data[column].isin(selected_values)]

st.sidebar.markdown('---')
st.sidebar.write('Rows after filters:', filtered_data.shape[0])

st.subheader('Dataset Overview')
col1, col2 = st.columns(2)
col1.metric('Rows', filtered_data.shape[0])
col1.metric('Columns', filtered_data.shape[1])
col2.write('**Sample columns**')
col2.write(all_columns[:10])

with st.expander('Show raw data'):
    st.dataframe(filtered_data.head(100))

with st.expander('Summary statistics'):
    if numeric_columns:
        st.dataframe(filtered_data[numeric_columns].describe().transpose())
    else:
        st.info('No numeric columns available for summary statistics.')

st.subheader('Interactive Chart')
chart = None
chart_kwargs = {}
if color != 'None':
    chart_kwargs['color'] = color

try:
    if chart_type == 'Bar':
        if y_axis:
            chart = px.bar(filtered_data, x=x_axis, y=y_axis, **chart_kwargs)
    elif chart_type == 'Line':
        if y_axis:
            chart = px.line(filtered_data, x=x_axis, y=y_axis, **chart_kwargs)
    elif chart_type == 'Scatter':
        if y_axis:
            chart = px.scatter(filtered_data, x=x_axis, y=y_axis, **chart_kwargs)
    elif chart_type == 'Histogram':
        chart = px.histogram(filtered_data, x=x_axis, **chart_kwargs)
    elif chart_type == 'Pie':
        chart = px.pie(filtered_data, names=x_axis, title=f'Pie chart by {x_axis}')
    elif chart_type == 'Box':
        if y_axis:
            chart = px.box(filtered_data, x=x_axis, y=y_axis, **chart_kwargs)
except Exception as err:
    st.error(f'Error creating chart: {err}')

if chart is not None:
    st.plotly_chart(chart, use_container_width=True)
else:
    st.info('Select valid columns for the chosen chart type.')
