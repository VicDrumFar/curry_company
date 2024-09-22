# Importando as bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime as dt
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static
from haversine import haversine
import plotly.graph_objects as go

st.set_page_config( page_title='Visão restaurantes', page_icon='🧑‍🍳', layout='wide' )

# -----------------------------------------------------------------------------------------------#

# ============================
# funções
# ============================

def distance (df1, fig):
    if fig == False:
        cols =["Delivery_location_latitude", "Delivery_location_longitude", "Restaurant_latitude", "Restaurant_longitude"]
        
        df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                                 haversine( (x['Restaurant_latitude'], x["Restaurant_longitude"]),
                                                 (x['Delivery_location_latitude'], x["Delivery_location_longitude"]) ), axis=1 )
        avg_distance = np.round(df1['distance'].mean(),2)
        return avg_distance
    
    else: cols =["Delivery_location_latitude", "Delivery_location_longitude", "Restaurant_latitude", "Restaurant_longitude"]
    df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                             haversine( (x['Restaurant_latitude'], x["Restaurant_longitude"]),
                                                        (x['Delivery_location_latitude'], x["Delivery_location_longitude"]) ), axis=1 )
    
    avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
    fig = go.Figure( data=[go.Pie( labels = avg_distance ['City'], values = avg_distance['distance'], pull=[0,0.1,0])])
    return fig



def avg_std_delivery_time (df1, festival , op):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega
    Parâmetros:
        Input:
            - df: Dataframe com os dados necessários para o cálculo
            - op: Tipo de operação que precisa ser calculado
            'avg_time': Calcula o tempo médio
            'std_time': Calcula o desvio padrão do tempo
    
        Output:
            - df: Dataframe com 2 colunas e 1 linha.

    """    
    df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
              .groupby( 'Festival')
              .agg( { 'Time_taken(min)' : [ 'mean', 'std' ]} ) )
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    df_aux = df_aux.loc[df_aux['Festival'] == 'Yes', op].mean()
    df_aux = np.round(df_aux, 2)

    return df_aux

def avg_std_time_graph ( df1 ):
    cols = ['City','Time_taken(min)']
    df_aux = df1.loc[:, cols].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux[ 'City' ], y=df_aux['avg_time'],
                        error_y=dict( type='data', array=df_aux['std_time'] ) ) )

    fig.update_layout(barmode='group')

    return fig


def avg_std_time_on_traffic ( df1 ):
    cols = ['City','Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby( ['City', 'Road_traffic_density']).agg( {'Time_taken(min)' : ['mean','std']})

    df_aux.columns = ['avg_time','std_time']

    df_aux = df_aux.reset_index()

    fig = px.sunburst (df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                       color='std_time', color_continuous_scale='RdBu',
                        color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    return fig



# cleaning_code

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

st.header('Marketplace - Visão restaurantes')

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
            st.title("Overall Metrics")

            col1, col2, col3, col4, col5, col6 = st.columns ( 6 )

            with col1:

                delivery_unique = len( df1.loc[:, 'Delivery_person_ID'].unique() )
                col1.metric ('Entregadores únicos', delivery_unique )

            
            with col2:
                avg_distance = distance ( df1, fig=False )
                col2.metric( 'A distancia média das entregas ', avg_distance )

                                
            with col3:
                df_aux = avg_std_delivery_time (df1,'Yes', 'avg_time')
                col3.metric( 'Tempo médio', df_aux )

            with col4:
                df_aux = avg_std_delivery_time (df1,'Yes', 'std_time')
                col4.metric( 'Std entrega', df_aux )
        
            with col5:
                df_aux = avg_std_delivery_time (df1,'No', 'avg_time')
                col5.metric( 'Tempo médio', df_aux )
                
            with col6:
                df_aux = avg_std_delivery_time (df1,'No', 'std_time')  
                col6.metric( 'Std entrega', df_aux )              


            with st.container():
                st.markdown("""___""")
    
                col1, col2 = st.columns(2)

            
            with col1:
                fig = distance( df1, fig=True )
                st.plotly_chart ( fig )
                
                
            with col2:
                st.title("Distribuição da distância")
    
                cols = ['City', 'Time_taken(min)', 'Type_of_order']
                df_aux = df1.loc[:,cols].groupby( ['City', 'Type_of_order']).agg( {'Time_taken(min)' : ['mean','std']})            
    
                df_aux.columns = ['avg_time','std_time']
    
                df_aux = df_aux.reset_index()
    
                st.dataframe ( df_aux )


    
        with st.container():
            st.markdown("""___""")
            st.title("Distribuição do tempo")

            col1, col2 = st.columns (2)

            with col1:
                fig = avg_std_time_graph ( df1 )
                st.plotly_chart ( fig )

            
            with col2:
                fig = avg_std_time_on_traffic ( df1 )
                st.plotly_chart ( fig )




        

        
