# Importando as bibliotecas necessárias
import pandas as pd
import streamlit as st
from datetime import datetime as dt
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )

# -----------------------------------------------------------------------------------------------#

# ============================
# funções
# ============================

def traffic_order_share( df1 ):
                
    df_aux = df1.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
                    
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    df_aux['entregas%'] = df_aux['ID'] / df_aux['ID'].sum()
                    
    fig = px.pie( df_aux, values='entregas%', names='Road_traffic_density')

    return fig

def order_metric ( df1 ):
        
    cols = ['ID', 'Order_Date']
    #selecao de linhas
    df_aux = df1.loc[:, cols].groupby( 'Order_Date' ).count().reset_index()

    #desenhando o gráfico
    fig = px.bar( df_aux, x='Order_Date', y='ID' )

    return fig

def traffic_order_city ( df1 ):
    df_aux = df1.loc[:,['ID', 'City' ,'Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
            
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            
    fig = px.scatter (df_aux, x='City', y='Road_traffic_density',size='ID', color='City')

    return fig

def order_by_week ( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    
    df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line( df_aux, x='week_of_year', y='ID')
        
    return fig


def order_share_by_week ( df1 ):
            df_aux01 = df1.loc[:,['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
            
            df_aux02 = df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
            
            df_aux = pd.merge(df_aux01, df_aux02, how='inner')
            
            df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            
            fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    
            return fig

def country_maps ( df1 ):
    
    df_aux = ( df1.loc [:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
              .groupby( ['City','Road_traffic_density'])
              .median()
              .reset_index() )
        
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    map = folium.Map()
        
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City','Road_traffic_density']]).add_to( map )
        
    folium_static( map, width=1024 , height=600 )

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
# Limpando os dados
# ==================================

df1 = clean_code ( df )



# ==================================
# Sidebar
# ==================================

st.header('Marketplace - Visão cliente')

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

# print("estou aqui")

# ==================================
# # Layout do Streamlit
# ==================================


tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        # order metric
        st.markdown( '# Orders by Day' )
        fig = order_metric ( df1 )
        st.plotly_chart ( fig, use_container_width=True )
   
    with st.container():
        col1, col2 = st.columns ( 2 )

        with  col1:
            st.header('Traffic Order Share')
            st.plotly_chart ( fig, use_container_width=True )
            fig = traffic_order_share( df1 )
                
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city ( df1 )
            st.plotly_chart ( fig, use_container_width=True )

with tab2:
        with st.container():
            st.markdown( '# Order by week' )
            fig = order_share_by_week ( df1 )
            st.plotly_chart ( fig, use_container_width=True )

with st.container():
        st.markdown( '# Order share by week' )
        fig = order_share_by_week ( df1 )
        st.plotly_chart ( fig, use_container_width=True )



with tab3:
    st.markdown( '# Country Maps' )
    country_maps ( df1 )
    







# df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()

# px.line( df_aux, x='week_of_year', y='ID')







