import numpy as np
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit.proto.DataFrame_pb2 import DataFrame
from streamlit.state.session_state import Value
import plotly.express as px
import folium
from folium.plugins import MarkerCluster, marker_cluster
from streamlit_folium import folium_static
import geopandas as gpd


st.set_page_config( layout='wide')

st.image('dados/banner.jpg', use_column_width= 'always')

st.header ( 'Roubo de Veículos no Estado de São Paulo ' )

paginas = ['Metodologia','Dados e Gráficos', 'Mapas' ]

pagina = st.sidebar.selectbox('Selecione a Página  que você deseja', paginas)


#######################
# carregando os dados #
#######################

@st.cache(allow_output_mutation=True)
def get_data(path):
    dados = pd.read_csv(path)
    
    return dados

path = 'dados/gdf_roubos.csv'
dados = get_data(path)

dados = dados.drop(columns=['Unnamed: 0','DATA DA OCORRENCIA', 'HORA DA OCORRENCIA', 'NUMERO', 'DATACOMUNICACAO', 'DATAELABORACAO', 'geometry' ])
dados.rename(columns={ 'DATAOCORRENCIA': 'DATA DA OCORRENCIA', 'HORAOCORRENCIA' : 'HORA DA OCORRENCIA', 'PERIDOOCORRENCIA': 'PERIODO DA OCORRENCIA'}, inplace=True)


#############################
########## DADOS ############
#############################


if pagina == 'Dados e Gráficos':
    
    

    
    dados['DATA DA OCORRENCIA'] = pd.to_datetime(dados['DATA DA OCORRENCIA'],errors='coerce').dt.strftime("%d/%m/%Y")
    total = dados.shape[0]
            
    
    
    chek = st.checkbox('Mostrar DataFrame Completo')
    
    
    if chek:
    
        st.dataframe(dados, height= 800)
        st.write("Total de Ocorrências", total)

    st.markdown('')
    st.markdown('')
    st.markdown(' ### ** Detalhes das Ocorrências **')
    st.markdown('')
    
    col1, col2 = st.columns(2)
            
    with col1 :
        var = st.selectbox('Selecione uma coluna para ter mais detalhes da Ocorrência', ['RUBRICA', 'ESPÉCIE', 'SOLUÇÃO'])

    if var == 'RUBRICA': 
        st.markdown(' #### ** Natureza Jurídica da Ocorrêndia **')
        mostrass = dados['RUBRICA'].value_counts()
        st.dataframe(mostrass, width=1000  ,height= 800)

    elif var == 'ESPÉCIE':
        st.markdown(' #### ** Circunstância que Qualifica a Ocorrência **') 

        mostrass = dados['ESPECIE'].value_counts()
        st.dataframe(mostrass, width=1000  ,height= 800)   


    elif var == 'SOLUÇÃO': 
        st.markdown(' #### ** Tipo de Resolução da Ocorrência **')
        mostrass = dados['SOLUCAO'].value_counts()
        st.dataframe(mostrass, width=1000  ,height= 800)

    
    
    
    
    st.markdown('')
    st.markdown('')


    st.markdown(' ### ** Gráficos **')
    st.markdown('')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1 :
        
        df3 = dados['PERIODO DA OCORRENCIA'].value_counts()
        fig = px.bar(df3, y=['PERIODO DA OCORRENCIA'], title=" Período da Ocorrência ")
        st.write(fig, use_container_width=False, sharing='streamlit')


    with col3 :
        
        fig = px.pie(dados, "FLAGRANTE", title='Ocorrências em Flagrante', width=500, height=500)
        st.plotly_chart(fig, use_container_width=False, sharing='streamlit')
        flagnt = dados['FLAGRANTE'].value_counts()
        
    col1, col2, col3 = st.columns(3)
    
    with col3:
        mstr = st.checkbox('Exibir Quantidade de Flagrantes')
        if mstr:    
            st.write(flagnt)

    
    st.markdown('')

    st.markdown(' ### ** Quantidade de Ocorrência por Data **')
    
    st.markdown('')
    
    grafico = ['Dia', 'Mês']
    graficos = st.radio('Filtrar Por:', grafico)

    if graficos == 'Dia':
        
        st.markdown(' ##### ** Ocorrências Agrupada por Dia **')
        
        data1 = dados['DIA DA OCORRENCIA'] = pd.to_datetime(dados['DATA DA OCORRENCIA']).dt.strftime('%d')
        data1 = (dados['DIA DA OCORRENCIA'] >= '01' ) & (dados['DIA DA OCORRENCIA'] <= '31' )
        data12 = data1.loc[data1].sort_index()
        data12 = data12.groupby(dados['DIA DA OCORRENCIA']).count()
        
        df2 = data12
        
        fig = px.line(df2, y=["DIA DA OCORRENCIA"], color_discrete_sequence= px.colors.qualitative.G10, markers=True)
        fig.update_xaxes(tickangle=0)
        st.plotly_chart(fig)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(' ##### ** Total de Ocorrências Agrupada por Dia **')
            st.dataframe(df2, width=500, height= 600)
        
        with col3:
            st.markdown(' #### ** Estatística Descritiva **')
            st.write(df2.describe().astype(int),width=500, height= 600)
        
    elif graficos == 'Mês':
        
        st.markdown(' ##### ** Ocorrências Agrupada por Mês **')
        
        data2 = dados['MES DA OCORRENCIA'] = pd.to_datetime(dados['DATA DA OCORRENCIA']).dt.strftime('%m')
        data2 = (dados['MES DA OCORRENCIA'] >= '01' ) & (dados['MES DA OCORRENCIA'] <= '11' )
        data21 = data2.loc[data2].sort_index()
        data21 = data21.groupby(dados['MES DA OCORRENCIA']).count()
        
        df4 = data21
        
        fig = px.line(df4, y=["MES DA OCORRENCIA"], color_discrete_sequence= px.colors.qualitative.G10, markers=True)
        fig.update_xaxes(tickangle=0)
        st.plotly_chart(fig, width=900, height= 600)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(' ##### ** Total de Ocorrências Agrupada por Mês **')
            st.dataframe(df4, width=500, height= 600)
        
        with col3:
            st.markdown(' #### ** Estatística Descritiva **')
            st.dataframe(df4.describe().astype(int), width=500, height= 600)    
        
        



#############################
########## MAPAS ############
#############################

if pagina == 'Mapas':
    
    
    st.markdown('')
    st.markdown('### ** Mapa com a Geolocalização das Ocorrências **')
    st.markdown('')
    
    col1, col2 = st.columns(2)


    with col1: 
        quant_dados = st.select_slider('Quatidade de Ocorrências', options=[100,1000,10000,20000])

    if quant_dados == 100:
        df = dados.head(100)

    elif quant_dados == 1000:
        df = dados.head(1000)

    elif quant_dados == 10000:
        df = dados.head(10000)
        
    elif quant_dados == 20000:
        df = dados.head(20000)

    dados['DATA DA OCORRENCIA'] = pd.to_datetime(dados['DATA DA OCORRENCIA'],errors='coerce').dt.strftime("%d/%m/%Y")
    
    roubo_map = folium.Map(location=[dados['LATITUDE'].mean(), dados['LONGITUDE'].mean()], defaut_zoom_start=15, tiles='cartodbpositron')

    marker_cluster = MarkerCluster().add_to(roubo_map)
    for name, row in df.iterrows():
        folium.Marker( [row['LATITUDE'], row['LONGITUDE'] ],
                    popup= """ <b> DADOS DA OCORRÊNCIA</b>  <br> <br><b> Local:</b>  {0} <br> <b> Data:</b>  {1} <br> <b> Hora:</b>  {2} <br> <b>Periodo:</b>  {3} <br> <b>Flagrante:</b> 
                    {4} <br> <b>Delegacia:</b> {5} <br> <b>Status:</b> {6} <br> <b>Rubrica:</b> {7} <br> <b>Solução:</b> {8} <br>  """.format(row['LOGRADOURO'], row['DATA DA OCORRENCIA'],
                                                                                                            row['HORA DA OCORRENCIA'],
                                                                                                            row['PERIODO DA OCORRENCIA'],
                                                                                                            row['FLAGRANTE'],
                                                                                                            row['DELEGACIA_CIRCUNSCRICAO'],
                                                                                                            row['STATUS'],
                                                                                                            row['RUBRICA'],
                                                                                                            row['SOLUCAO']), max_width=500).add_to( marker_cluster )
    folium_static( roubo_map, width=1000, height= 600 )


   

    #########################
    ####### MAPA 2 ##########
    #########################
    
    
    col1, col2 = st.columns(2)

    gdf_roubos = gpd.read_file("dados/gdf_roubos_veiculos1.json", driver='GeoJSON')
    filename = 'dados/municipios_grande_sp.json'
    gdf_mun_grande_sp = gpd.read_file(filename, driver='GeoJSON')

    for index, municipio in gdf_mun_grande_sp.iterrows():
        
        qntd_roubos = len(gdf_roubos[gdf_roubos.intersects(municipio.geometry)])
        
        gdf_mun_grande_sp.loc[index,'qntd_roubos'] = qntd_roubos
        

    media_latitude_gsp = gdf_roubos['LATITUDE'].mean()
    media_logitude_gsp = gdf_roubos['LONGITUDE'].mean()

    fmap = folium.Map(location=[media_latitude_gsp, media_logitude_gsp], tiles='cartodbpositron')

    for _, municipio in gdf_mun_grande_sp.iterrows():
        
        municipio_geojson = folium.features.GeoJson(municipio.geometry,
                                                    style_function= lambda features:{
                                                        'color': 'blue',
                                                        'weight': 2,
                                                        'fillOpacity': 0.1
                                                    })
        popup = folium.Popup("""
                                Município: {} <br>
                                Total de Ocorrências registradas: {}
                                """.format(municipio.NM_MUN, str(int(municipio.qntd_roubos))), max_width=300)
        
        popup.add_to(municipio_geojson)
        
        municipio_geojson.add_to(fmap)

    with col1:
        mmps = st.checkbox('Exibir Mapa com Ocorrências agrupado por Municípios da Grande São Paulo ')
    
    if mmps:
        st.markdown('')
        st.markdown('### ** Mapa com Total Ocorrências por Munícipio da Grande São Paulo **')
        st.markdown('')
    
        
        folium_static(fmap, width=1000, height= 700)
    


#############################
######### METODO ############
#############################
    
    
if pagina == 'Metodologia':

    st.markdown('## METODOLOGIA PARA INTERPRETAÇÃO DOS DADOS')

    '''





    #### ** Para a correta interpretação dos dados é importante observar as seguintes informações:**

    1. Os dados constantes da resposta foram extraídos do sistema de Registro Digital de Ocorrências (R.D.O.) que é a ferramenta de registro dos boletins de ocorrência nas delegacias de polícia. 
    
        1.1. Com relação ao sistema R.D.O. é importante esclarecer que sua implantação foi concretizada de modo gradual nas diversas unidades policiais do Estado

    ​

    2. Cada linha constante na tabela registra os dados de uma pessoa, natureza ou objeto relacionado no boletim. Assim, um boletim que possua a identificação de mais de uma pessoa, natureza ou objeto (a depender da pesquisa solicitada) terá os dados da ocorrência multiplicados pelos indexadores solicitados, ou seja, várias linhas podem se referir ao mesmo boletim. 

    ​

    3. O número total de boletins de ocorrências registrados sob uma natureza criminal não representa a estatística criminal do Estado ou de determinada área ou região. A estatística em São Paulo é contabilizada de acordo com os procedimentos estabelecidos pela Resolução SSP nº 160/01 de 08 de maio de 2001, que criou o Sistema Estadual de Coleta de Estatísticas Criminais e pode ser consultada através do endereço eletrônico [SSP.SP.GOV](www.ssp.sp.gov.br)."





    ​
    ​


    A PRESENTE TABELA TEM POR FINALIDADE ESCLARECER OS CAMPOS CONTIDOS NA BASE DE DADOS


    ​
    ​



    |         Campos          |                Descrição                 |
    | :---------------------: | :--------------------------------------: |
    |                         |             Index dos dados              |
    |         ANO_BO          |                Ano do BO                 |
    |       BO_INICIADO       | Hora e data do Inicio da abertura do BO  |
    |       BO_EMETIDO        |       Hora e data do emisão do BO        |
    |   DATA DA OCORRENCIA    |            Data da Ocorrência            |
    |   HORA DA OCORRENCIA    |            Hora da Ocorrência            |
    |   PERIODO OCORRENCIA    |          Período da Ocorrência           |
    |        FLAGRANTE        | Indica se houve flagrante ( sim ou não)  |
    |       LOGRADOURO        |           Logradouro dos fatos           |
    |         CIDADE          |            Cidade de Registro            |
    |        LATITUDE         |          Latitude da Ocorrência          |
    |        LONGITUDE        |         Longitude da Ocorrência          |
    |     DESCRICAOLOCAL      | Descreve de tipos de locais onde se deu o fato |
    |         SOLUCAO         | Descreve tipo de resolução da Ocorrência |
    |     DELEGACIA_NOME      |   Delegacia responsável pelo registro    |
    | DELEGACIA_CIRCUNSCRICAO |      Departamento de Circunscrição       |
    |         ESPECIE         | Circunstancia que qualifica a ocorrência |
    |         RUBRICA         |     Natureza jurídica da ocorrência      |
    |         STATUS          |  Indica se é crime consumado ou tentado  |

    ​
    ​

    Período de Coleta dos dados: ** 01/01/2021 a 30/11/2021* ** (Data da emisão do BO)
    
    Fonte: [Governo de São Paulo](http://www.ssp.sp.gov.br/transparenciassp/Consulta.aspx)
    '''