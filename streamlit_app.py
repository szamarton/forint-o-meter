import pandas as pd
import streamlit as st
import plotly.io as pio
import plotly.express as px
import io

CATEGORY_COLOR_MAP = {
    '-': '#CD5C08', # user data
    'reference': '#C1D8C3', # reference data, TODO: categorize the data, then add the categories and colors here
}

def streamlit_config():
    st.set_page_config(layout="wide", page_title="Forint-o-meter")
    st.sidebar.title("Személyre szabás")

def import_data():
    data = pd.read_csv('data.csv', encoding='UTF-8')
    data = data.dropna()
    data = data[data['use']==1]
    all_labels_long = data['name'].values
    return data, all_labels_long

def filtering(all_labels_long):
    with st.sidebar.expander("Referencia adatok"):
        container = st.container()
        all = st.checkbox("Összes", True)
        if all:
            selected_options = container.multiselect("Válasszon referenciákat:",all_labels_long,all_labels_long)
        else:
            selected_options =  container.multiselect("Válasszon referenciákat:",all_labels_long)
        return selected_options

def get_user_input():
    with st.sidebar.expander("Egyéni adat"):
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            user_value = st.number_input("Összeg:", min_value=0.0, value=0.0, step=1.0)
        with col2:
            factor = st.selectbox('',['Milliárd', 'Millió'])
        with col3:
            factor_valuta = st.selectbox('',['HUF', 'EUR', 'USD'])
        user_label = st.text_input("Cím:", "Az én kis milliárdom", max_chars=50)

    if factor == "Milliárd":
        user_value = user_value * 1e9
    else:
        user_value = user_value * 1e6
    if factor_valuta == "EUR":
        user_value = user_value * 400
    elif factor_valuta == "USD":
        user_value = user_value * 350

    return user_value, user_label

def create_fig(viz_data):

    fig = px.treemap(
        viz_data, path=['labels_short'], values='amount', color='category', 
        title='Mit jelent egy milliárd forint?', 
        color_discrete_map=CATEGORY_COLOR_MAP,
        custom_data = ['labels_short', 'labels_long', 'amount', 'category', 'amount_str'])

    fig.update_traces(
        hovertemplate=
        '<b>%{customdata[0]}</b><br><br>' +
        'Leírás: %{customdata[1]}<br>' +
        'Összeg: %{customdata[4]}<br>' +
        'Kategória: %{customdata[3]}<br>'
        '<extra></extra>',
        hoverlabel=dict(align='left')
    )
    fig.update_layout(width=1600, height=700, font_size=18, title_font_size=24)

    return fig

def download_fig_button(fig):
    buffer = io.BytesIO()
    fig.write_image(file=buffer, format="pdf")
    st.sidebar.download_button(
        label="Ábra letöltése (PDF)",
        data=buffer,
        file_name="forint-o-meter.pdf",
        mime="application/pdf",
    )

def streamlit_credits():
    with st.sidebar.expander("Egyéb"):
        st.write("Inspiració: <a href='https://www.youtube.com/watch?v=5Zg-C8AAIGg'>The beauty of data visualization - David McCandless</a>", unsafe_allow_html=True)
        st.write("Adatok, források: <a href='https://github.com/szamarton/forint-o-meter/blob/main/data.csv'>github repo</a>", unsafe_allow_html=True)

def main():

    streamlit_config()
    data, all_labels_long = import_data()
    selected_options = filtering(all_labels_long)

    filtered_data = data[data['name'].isin(selected_options)]

    values = filtered_data['amount'].values
    labels_long = filtered_data['name'].values
    labels_short = filtered_data['short'].values
    categories = filtered_data['category'].values

    user_value, user_label = get_user_input()

    if len(selected_options) > 0:

        viz_data = pd.DataFrame()
        viz_data['labels_long'] = [*labels_long, user_label]
        viz_data['labels_short'] = [*labels_short, user_label]
        viz_data['amount'] = [*values, user_value]
        viz_data['category'] = [*categories, '-']
        viz_data['amount_str'] = viz_data['amount'].apply(lambda value: f"{round(value/1e9)} Mrd HUF")
        
        fig = create_fig(viz_data)
        st.plotly_chart(fig, config={'displayModeBar': False})
        download_fig_button(fig)

    streamlit_credits()

if __name__ == "__main__":
    main()