import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

st.title('S&P 500 App')

st.markdown("""
Esse app obtém uma lista de empresas que compõem o índice S&P 500 (by Wikipedia) and encontra o preço correspondente de fechamento de mercado (year-to-date)!
* **Bibliotecas Python utilizadas:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Fonte de dados:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# Web scraping do S&P 500 

@st.cache_data
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Seleção do setor
sorted_sector_unique = sorted( df['GICS Sector'].unique() )
selected_sector = st.sidebar.multiselect('Setor', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = df[ (df['GICS Sector'].isin(selected_sector)) ]

st.header('Mostrar Empresas no Setor Selecionado')
st.write('Dimensão dos dados: ' + str(df_selected_sector.shape[0]) + ' linhas e ' + str(df_selected_sector.shape[1]) + ' colunas.')
st.dataframe(df_selected_sector)

# Download S&P500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# https://pypi.org/project/yfinance/

data = yf.download(
        tickers = list(df_selected_sector[:10].Symbol),
        period = "ytd",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )

# Plotando Preço de fechamento do simbolo selecionado
def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.Date, y=df.Close, name='Closing Price', line=dict(color='skyblue', width=2)))
    fig.update_layout(
        title=f"{symbol}",
        xaxis=dict(title='Date'),
        yaxis=dict(title='Closing Price'),
        hovermode='x',
        template='plotly_white'
    )
    
    return st.plotly_chart(fig)


num_company = st.sidebar.slider('Número de Empresas', 1, 5)

if st.button('Show Plots'):
    st.header('Preço de fechamento da ação:')
    for company_symbol in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(company_symbol)