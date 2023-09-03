###############################################################################################################################################
## --------------------------------------------------------Bibliotecas-------------------------------------------------------------------------
###############################################################################################################################################

import pandas as pd
import re
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from datetime import datetime as dt
from PIL import Image
from streamlit_folium import folium_static
import numpy
import inflection
import leafmap
from folium.plugins import MarkerCluster

###############################################################################################################################################
## -----------------------------------------------Leitura/Backup do DataFrame------------------------------------------------------------------
###############################################################################################################################################

df_raw = pd.read_csv('df_pa1.csv')

# Fazendo uma cópia do DataFrame Lido
df = df_raw.copy()

###############################################################################################################################################
## ------------------------------------------------------------Funções-------------------------------------------------------------------------
############################################################################################################################################### 

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]

def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def create_delivery(delivery):
    if delivery == 0:
        return "no"
    else:
        return "yes"

def create_booking(booking):
    if booking == 0:
        return "no"
    else:
        return "yes"
def create_online(delivery_online):
    if delivery_online == 0:
        return "no"
    else:
        return "yes"
def adjust_columns_order(dataframe):
    df = dataframe.copy()

    new_cols_order = [
        "restaurant_id",
        "restaurant_name",
        "country",
        "city",
        "address",
        "locality",
        "locality_verbose",
        "longitude",
        "latitude",
        "cuisines",
        "price_type",
        "average_cost_for_two",
        "currency",
        "has_table_booking",
        "has_online_delivery",
        "is_delivering_now",
        "aggregate_rating",
        "rating_color",
        "color_name",
        "rating_text",
        "votes",
    ]

    return df.loc[:, new_cols_order]
df.rename(columns={"rating_color":"color_name"})

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

def rename_columns(df):
    df = df.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df
df.rename(columns={"rating_color":"color_name"})

def clean_code(df):
    df['Restaurant ID'] = df['Restaurant ID'].astype( int )
    df['Country Code'] = df['Country Code'].astype( int )
    df['Average Cost for two'] = df['Average Cost for two'].astype( int )
    df['Aggregate rating'] = df['Aggregate rating'].astype( float )
    df['Votes'] = df['Votes'].astype( int )
    df['Cuisines'] = df['Cuisines'].astype( str )
    df["Cuisines"] = df.loc[:, "Cuisines"].apply(lambda x: x.split(",")[0])  
    df = rename_columns(df)
    df['country_code'] = df.loc[:, 'country_code'].apply(lambda x: country_name(x))
    df['color_name'] = df.loc[:, 'rating_color'].apply(lambda x: color_name(x))
    df['price_range'] = df.loc[:, 'price_range'].apply(lambda x: create_price_tye(x))
    df['is_delivering_now'] = df.loc[:, 'is_delivering_now'].apply(lambda x: create_delivery(x))
    df['has_table_booking'] = df.loc[:, 'has_table_booking'].apply(lambda x: create_booking(x))
    df['has_online_delivery'] = df.loc[:, 'has_online_delivery'].apply(lambda x: create_online(x))
    return df
    
###############################################################################################################################################
## --------------------------------------------Configuração da Página-------------------------------------------------------------------------
###############################################################################################################################################

df = clean_code(df)

st.set_page_config(layout="wide")

###############################################################################################################################################
## -----------------------------------------------Barra Lateral--------------------------------------------------------------------------------
###############################################################################################################################################

image_path='logo.png'
image=Image.open(image_path)
st.sidebar.image(image, width=300)


st.sidebar.markdown("""---""")
st.sidebar.header("Filtros")

country_options=st.sidebar.multiselect('Paises',
                      ["India","Australia","Brazil","Canada","Indonesia","Indonesia","New Zeland","Philippines","Qatar","Singapure","South Africa","Sri Lanka","Turkey","United Arab Emirates","England","United States of America"],
                      default=["India","Australia","Brazil","Canada"])

t10 = st.sidebar.slider('Selecione a quantidade de Restaurantes que deseja visualizar', 0, 5, 10)

st.sidebar.markdown("""---""")

cuirsines_options=st.sidebar.multiselect('Selecione o tipo culinário',
                      df.loc[:, "cuisines"].unique().tolist(),
                      default=["Home-made","BBQ","Japanese","Brazilian","Arabian","American","Italian",])

st.sidebar.markdown("""---""")

line=df['country_code'].isin(country_options)
df=df.loc[line,:]

line_td = df['cuisines'].isin(cuirsines_options)
df=df.loc[line_td,:]

###############################################################################################################################################
## --------------------------------------------Layout Dashboard--------------------------------------------------------------------------------
###############################################################################################################################################

with st.container():
    
    st.markdown("# 🦐Gastronomias dos Bares/Restaurantes!")
    st.markdown("## Melhores Restaurantes dos tipos Gastronomicos")
    
with st.container():
    col1, col2, col3, col4, col5 = st.columns(5, gap='large')
    with col1:
        
        df_rank = pd.DataFrame(df.loc[:,["restaurant_name","aggregate_rating","cuisines"]].groupby(['restaurant_name','cuisines']).max().reset_index().sort_values('aggregate_rating', ascending=False))
        df_rank.head(5).reset_index()
        df_02= (f'{df_rank.iloc[0,2]}/5.0')
        col1.metric("Dinner By Heston : British", df_02 )
        
    with col2:
        
        df_rank = pd.DataFrame(df.loc[:,["restaurant_name","aggregate_rating","cuisines"]].groupby(['restaurant_name','cuisines']).max().reset_index().sort_values('aggregate_rating', ascending=False))
        df_rank.head(5).reset_index()
        df_12= (f'{df_rank.iloc[1,2]}/5.0')
        col2.metric("Phil's Bbq : BBQ", df_12 )
        
    with col3:
        
        df_rank = pd.DataFrame(df.loc[:,["restaurant_name","aggregate_rating","cuisines"]].groupby(['restaurant_name','cuisines']).max().reset_index().sort_values('aggregate_rating', ascending=False))
        df_rank.head(5).reset_index()
        df_22= (f'{df_rank.iloc[2,2]}/5.0')
        col3.metric("Bel Punto : Seafood", df_22 )
        
    with col4:
        
        df_rank = pd.DataFrame(df.loc[:,["restaurant_name","aggregate_rating","cuisines"]].groupby(['restaurant_name','cuisines']).max().reset_index().sort_values('aggregate_rating', ascending=False))
        df_rank.head(5).reset_index()
        df_32= (f'{df_rank.iloc[3,2]}/5.0')
        col4.metric("Nando's : Portuguese", df_32 )
        
    with col5:
        
        df_rank = pd.DataFrame(df.loc[:,["restaurant_name","aggregate_rating","cuisines"]].groupby(['restaurant_name','cuisines']).max().reset_index().sort_values('aggregate_rating', ascending=False))
        df_rank.head(5).reset_index()
        df_42= (f'{df_rank.iloc[4,2]}/5.0')
        col5.metric("La Colombe : French", df_42 )
with st.container():
    
    st.markdown(f'## Top {t10} Restaurantes')
    df10 = df.loc[:,["restaurant_id","restaurant_name", "country_code", "city", "cuisines", "average_cost_for_two", "aggregate_rating", "votes"]].groupby(['restaurant_name','cuisines']).max().reset_index().sort_values('aggregate_rating', ascending=False)
    df10.columns= [" Nome_Restaurante", "Gastronomia", "ID_Restaurante", "Pais", "Cidade", "Valor para 2", "Avaliações", "Votos"]
    df_selec = df10.head(t10)
    st.dataframe(df_selec, use_container_width=True)
    
with st.container():
    
    col1, col2 = st.columns(2, gap='large')
    
    with col1:
        st.markdown(f'### Top {t10} Melhores Tipos Culinários')
        melhores10 = top = round(df.loc[:,["aggregate_rating","cuisines"]].groupby(['cuisines']).mean().reset_index().sort_values('aggregate_rating', ascending=False),1)
        df_m10 = melhores10.head(10)
        df_m10.columns = ['Tipos Culinários', 'Média de Avaliação']
        fig = px.bar(df_m10, x='Tipos Culinários', y='Média de Avaliação')
        fig.update_traces(texttemplate='%{y}', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f'### Top {t10} Piores Tipos Culinários')
        pior10 = top = round(df.loc[:,["aggregate_rating","cuisines"]].groupby(['cuisines']).mean().reset_index().sort_values('aggregate_rating', ascending=True),1)
        df_p10 = pior10.head(10)
        df_p10.columns = ['Tipos Culinários', 'Média de Avaliação']
        fig = px.bar(df_p10, x='Tipos Culinários', y='Média de Avaliação')
        fig.update_traces(texttemplate='%{y}', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    






















