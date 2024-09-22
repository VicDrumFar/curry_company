# Importando as bibliotecas necessárias
import pandas as pd
import streamlit as st
from datetime import datetime as dt
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🏍️', layout='wide' )

# -----------------------------------------------------------------------------------------------#

# ============================
# funções
# ============================

def top_delivers( df1, top_asc ):
    df2 = (df1.loc[:, ['City','Delivery_person_ID','Time_taken(min)']]
           .groupby(['City','Delivery_person_ID'])
           .mean().sort_values(['City','Time_taken(min)'], ascending = top_asc)
           .reset_index() )
    
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
    df3 = pd.concat( [df_aux1, df_aux2, df_aux3] ).reset_index( drop=True)
    
    return df3

def clean_code( df1 ):

    """ Esta função tem a responsabilidade de limpar o dataframe 

    Tipos de limpeza
    1. Remoção de dados NaN
    2. Mudança de tipo da coluna de dados
    3. Remoção de espaços das variáveis de texto
    4. Formatação da coluna de datas
    5. Limpeza da coluna tempo (remoção de texto da variável numérica)

    input: dataframe
    output: dataframe    
    
    """
     
    
    # Pré-processamento dos dados
    df1 = df.copy()
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']
    df1 = df1[df1['Road_traffic_density'] != 'NaN ']
    df1 = df1[df1['City'] != 'NaN ']
    df1 = df1[df1['Festival'] != 'NaN ']
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1 = df1[df1['multiple_deliveries'] != 'NaN ']
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['ID'] = df1['ID'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['City'] = df1['City'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1]).astype(int)
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )

    return df1

#---------------------------------------- Início da estrututura lógica do código --------------------------------------

#====================================
# Import dataset
#====================================

df = pd.read_csv('dataset/train.csv')

# ==================================
# cleaning dataset
# ==================================

df1 = clean_code ( df )

# ==================================
# Sidebar
# ==================================

st.header('Marketplace - Visão entregadores')

# Carregando e exibindo a imagem no sidebar

#image_path = r'C:\Users\fomer\OneDrive - AIQFOME LTDA\repos\ftc_python\ciclo3\logo.png'

image = Image.open ('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('---')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=dt(2022, 4, 13),
    min_value=dt(2022, 2, 11),
    max_value=dt(2022, 4, 6),
    format='DD-MM-YYYY'
)
st.header(date_slider)

st.sidebar.markdown('----')

climate_options = st.sidebar.multiselect(
    'Quais as condições do climáticas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'Jam'],
)


st.sidebar.markdown('----')


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('----')
st.sidebar.markdown('### Powered by VicDrumFar')


# Filtro de data

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]


# Filtro de trânsito

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas,:]

# Filtro de clima

linhas_selecionadas = df1['Weatherconditions'].isin( climate_options )
df1 = df1.loc[linhas_selecionadas,:]



# ==================================
# # Layout
# ==================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1:

            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric( 'Maior de idade', maior_idade )

        with col2:

            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric( 'Menor de idade', menor_idade )

        with col3:

            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao', melhor_condicao )
        
        with col4:

            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric( 'Pior condicao', pior_condicao )

    with st.container():
        st.markdown( '''___''' )
        
        st.title( 'Avalicoes' )

        col1, col2, col3 = st.columns ( 3 )
        
        with col1:
            st.markdown( '##### Avaliacao media por entregador' )
            df_avg_ratings_per_deliver = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID')
                                                                                                     .mean()
                                                                                                     .reset_index())

            st.dataframe( df_avg_ratings_per_deliver )
            
        with col2:
            st.markdown( '##### Avaliacao media por transito' )

            df_avg_std_rating_by_traffic = (df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density')
                                                                                                          .agg({'Delivery_person_Ratings': ['mean','std']}))
            
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            
            
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            
            st.dataframe( df_avg_std_rating_by_traffic )

        
        with col3:
            st.markdown( '##### Avaliacao media por clima' )

            df_avg_std_rating_by_wather = (df1.loc[:, ['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions')
                                                                                                      .agg({'Delivery_person_Ratings': ['mean','std']}))
            
            df_avg_std_rating_by_wather.columns = ['delivery_mean', 'delivery_std']
            
            df_avg_std_rating_by_wather = df_avg_std_rating_by_wather.reset_index()
            
            st.dataframe( df_avg_std_rating_by_wather )

    with st.container():
        st.markdown( '''___''' )
        st.title( 'Velocidade de entrega' )
        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown( '##### Top entregadores mais rapidos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )

        with col2:
            st.markdown( '##### Top entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )






        
            


