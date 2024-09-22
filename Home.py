import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲"
)

# image_path = 'C:/Users/fomer/OneDrive - AIQFOME LTDA/repos/ftc_python/ciclo3/'
image = Image.open ('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('---')

st.header( "Curry Company Growth Dashboard" )

st.markdown(
    """
     Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
     ##### Como utilizar esse Growth Dashboard?
     - Visão empresa:
        - Visão gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
     - Visão entregador:
         - Acompanhamento dos indicadores semanais de crescimento
     - Visão restaurante:
         - Indicadores semanais de crescimento dos restaurantes

     ##### Ask for help
        - Time de Data Science no Discord
            -@vicdrumfar


    """ )
