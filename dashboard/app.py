import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Saúde mental",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------
# CSS
# -------------------------
st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Carregamento de dados
# -------------------------
@st.cache_data
def load_data():
    base_path = Path(__file__).parent
    file_path = base_path / "data" / "dados_saude_mental_fake.csv"
    return pd.read_csv(file_path)

df = load_data()
# -------------------------
# Título
# -------------------------
st.title("Análise Exploratória – Perfil e Fatores Associados à Saúde Mental")
st.subheader("Estudo descritivo sobre diagnóstico, estresse e acompanhamento clínico.")


st.markdown("---")
st.sidebar.header("Filtros")

# -------------------------
# Filtros
# -------------------------
idade_min_global = int(df['idade'].min())
idade_max_global = int(df['idade'].max())

idade_min, idade_max = st.sidebar.slider(
    "Selecione a faixa etária",
    idade_min_global,
    idade_max_global,
    (idade_min_global, idade_max_global)
)

genero = st.sidebar.multiselect(
    "Selecione o gênero",
    df['genero'].unique(),
    default=df['genero'].unique()
)

estado_civil = st.sidebar.multiselect(
    "Selecione o estado civil",
    df['estado_civil'].unique(),
    default=df['estado_civil'].unique()
)

escolaridade = st.sidebar.multiselect(
    "Selecione o nível de escolaridade",
    df['nivel_escolaridade'].unique(),
    default=df['nivel_escolaridade'].unique()
)

# -------------------------
# DataFrame filtrado
# -------------------------
df_filtrado = df[
    (df['idade'].between(idade_min, idade_max)) &
    (df['genero'].isin(genero)) &
    (df['estado_civil'].isin(estado_civil)) &
    (df['nivel_escolaridade'].isin(escolaridade))
]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com esses filtros.")
    st.stop()

# -------------------------
# Abas (reduz peso de renderização)
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Perfil Demográfico", "Perfil Clínico", "Tratamento & Experiência", "Conclusões"])

# =========================
# ABA 1 - PERFIL
# =========================
with tab1:

    st.metric("Total de pacientes", df_filtrado.shape[0])
    st.metric("Idade média dos pacientes", f"{df_filtrado['idade'].mean():.0f} anos")

    st.markdown("---")

    # Gênero
    genero_counts = df_filtrado['genero'].value_counts().reset_index()
    genero_counts.columns = ['Gênero', 'Quantidade']
    fig = px.bar(genero_counts, x='Gênero', y='Quantidade', color='Gênero')
    title = "Quantidade de pacientes por gênero"
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

    # Estado civil
    estado_civil_counts = df_filtrado['estado_civil'].value_counts().reset_index()
    estado_civil_counts.columns = ['Estado civil', 'Quantidade']
    fig = px.bar(estado_civil_counts, x='Estado civil', y='Quantidade', color='Estado civil')
    title = "Quantidade de pacientes por estado civil"
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

    # Escolaridade
    escolaridade_counts = df_filtrado['nivel_escolaridade'].value_counts().reset_index()
    escolaridade_counts.columns = ['Nível de escolaridade', 'Quantidade']
    fig = px.bar(escolaridade_counts, x='Nível de escolaridade', y='Quantidade', color='Nível de escolaridade')
    title = "Quantidade de pacientes por nível de escolaridade"
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# ABA 2 - PERFIL CLÍNICO
# =========================
with tab2:

    # Diagnóstico
    diagnostico_counts = df_filtrado['diagnostico_principal'].value_counts().reset_index()
    diagnostico_counts.columns = ['Diagnóstico principal', 'Quantidade']
    fig = px.bar(diagnostico_counts,x='Diagnóstico principal',y='Quantidade', color='Diagnóstico principal')
    title = "Quantidade de pacientes por diagnóstico principal"
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

    # Uso medicação (%)
    uso_medicacao_counts = df_filtrado['uso_medicacao'].value_counts(normalize=True) * 100
    uso_medicacao_counts = uso_medicacao_counts.reset_index()
    uso_medicacao_counts.columns = ['Uso de medicação', 'Porcentagem']
    fig = px.bar(uso_medicacao_counts, x='Uso de medicação', y='Porcentagem', color='Uso de medicação')
    title = "Uso de medicação (%)"
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

    # Número médio consultas
    st.metric("Número médio de consultas por ano",
              f"{df_filtrado['numero_consultas_ano'].mean():.0f}")

    # Faltas
    faltas_counts = df_filtrado['faltas_consulta'].value_counts().reset_index()
    faltas_counts.columns = ['Faltas', 'Quantidade']
    fig = px.bar(faltas_counts, x='Faltas', y='Quantidade', color='Faltas')
    title = "Quantidade de pacientes por número de faltas"
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

    # Estresse médio
    st.metric("Nível médio de estresse",
              f"{df_filtrado['nivel_estresse_0_10'].mean():.0f}")

    # Estresse por diagnóstico (agregado)
    estresse_por_diag = (
        df_filtrado
        .groupby('diagnostico_principal')['nivel_estresse_0_10']
        .mean()
        .reset_index()
    )

    fig = px.bar(
        estresse_por_diag,
        x='diagnostico_principal',
        y='nivel_estresse_0_10',
        color='diagnostico_principal',
        title="Nível médio de estresse por diagnóstico"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Diagnóstico x Gênero

    diag_genero = (
        df_filtrado
        .groupby(['genero', 'diagnostico_principal'])
        .size()
        .reset_index(name='Quantidade')
    )

    # calcular proporção dentro de cada gênero
    diag_genero['Proporção (%)'] = (
        diag_genero
        .groupby('genero')['Quantidade']
        .transform(lambda x: x / x.sum() * 100)
    )

    fig = px.bar(
        diag_genero,
        x='genero',
        y='Proporção (%)',
        color='diagnostico_principal',
        barmode='stack',
        title="Proporção de pacientes por diagnóstico e gênero"
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================
# ABA 3 - TRATAMENTO
# =========================

with tab3:

# Satisfação
    satisfacao_counts = df_filtrado['satisfacao_tratamento_1_5'].value_counts().reset_index()
    satisfacao_counts.columns = ['Satisfação com tratamento', 'Quantidade']
    fig = px.bar(satisfacao_counts,x='Satisfação com tratamento',y='Quantidade',color='Satisfação com tratamento')
    title = "Quantidade de pacientes por satisfação com tratamento"
    fig.update_layout(title=title)

    st.plotly_chart(fig, use_container_width=True)

    # Relação consultas x satisfação (CORRIGIDO - AGREGADO)
    relacao = (
        df_filtrado
        .groupby('numero_consultas_ano')['satisfacao_tratamento_1_5']
        .mean()
        .reset_index()
    )

    fig = px.bar(
        relacao,
        x='numero_consultas_ano',
        y='satisfacao_tratamento_1_5',
        color='numero_consultas_ano',
        title="Relação entre número de consultas e satisfação com tratamento"
        
    )

    st.plotly_chart(fig, use_container_width=True)

    # genero x satisfação
    genero_satisfacao = (
        df_filtrado
        .groupby(['genero', 'satisfacao_tratamento_1_5'])
        .size()
        .reset_index(name='Quantidade')
    )

    # calcular proporção dentro de cada gênero
    genero_satisfacao = genero_satisfacao.groupby('genero')['Quantidade'].sum().reset_index()
    genero_satisfacao['Proporção (%)'] = (
        genero_satisfacao['Quantidade'] / genero_satisfacao['Quantidade'].sum() * 100
    )
    genero_satisfacao = genero_satisfacao.sort_values(by='Proporção (%)', ascending=False)

    fig = px.bar(
        genero_satisfacao,
        x='genero',
        y='Proporção (%)',
        color='genero',
        title="Proporção de pacientes por gênero e satisfação com tratamento"
        
    )

    st.plotly_chart(fig, use_container_width=True)

with tab4:

    st.markdown("""
A presente análise exploratória foi conduzida com base em uma amostra fictícia composta por 2.000 pacientes, com idade média aproximada de 44 anos. A distribuição por gênero mostrou equilíbrio entre os grupos masculino e feminino, enquanto o grupo não binário apresentou menor representatividade na amostra.

Em relação ao estado civil, observou-se maior concentração de pacientes solteiros e casados, sendo o grupo de viúvos o menos frequente. Quanto ao nível de escolaridade, indivíduos com ensino superior completo (graduação) representaram a maior parcela da amostra, enquanto pacientes com ensino médio apresentaram menor proporção relativa.

No que se refere ao diagnóstico principal, o Transtorno de Estresse Pós-Traumático (TEPT) apresentou a maior incidência entre os pacientes, seguido por quadros de depressão. O Transtorno do Pânico foi o diagnóstico menos frequente na amostra analisada.

A análise do uso de medicação indicou que aproximadamente 55,65% dos pacientes fazem uso de tratamento farmacológico, evidenciando predominância dessa abordagem terapêutica na amostra. O nível médio de estresse reportado foi 5 em uma escala de 0 a 10, indicando intensidade moderada.

Em relação à adesão ao tratamento, verificou-se que a maioria dos pacientes registrou apenas uma falta anual, não sendo observado padrão crítico de evasão. Quanto à intensidade do estresse por diagnóstico, pacientes com diagnóstico de ansiedade apresentaram os maiores níveis médios de estresse.

A distribuição proporcional dos diagnósticos por gênero revelou maior incidência de ansiedade e transtorno bipolar na população não binária, enquanto o TEPT apresentou maior concentração relativa entre mulheres. No que se refere à satisfação com o tratamento (escala de 1 a 5), a maioria dos pacientes atribuiu nota 4, indicando percepção predominantemente positiva (entre "bom" e "muito bom"). Entretanto, o grupo não binário apresentou níveis médios de satisfação inferiores aos demais grupos.

De modo geral, os resultados indicam padrões coerentes entre diagnóstico, percepção de estresse, uso de medicação e satisfação com o tratamento, permitindo uma compreensão estruturada do perfil clínico da amostra analisada.
""")
st.markdown("---")

st.markdown(f"""
**Autor:** Samuel de Andrade da Silva  
**Versão:** 1.0  
**Contato:** [samuelsilva00935@gmail.com](mailto:samuelsilva00935@gmail.com)

**Observação:** Dados fictícios utilizados exclusivamente para fins educacionais e prática em análise de dados.  
**Licença:** MIT
""")




    
























































