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
st.title("🧠 Dashboard de Saúde Mental")
st.caption("Perfil demográfico, clínico e experiência com tratamento")

st.markdown("---")
st.sidebar.markdown("## 🔎 Filtros de Análise")

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
# Abas
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Perfil Demográfico",
    "Perfil Clínico",
    "Tratamento & Experiência",
    "Conclusões"
])

# =========================
# ABA 1 - PERFIL DEMOGRÁFICO
# =========================
with tab1:

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de pacientes", df_filtrado.shape[0])
    col2.metric("Idade média", f"{df_filtrado['idade'].mean():.0f} anos")
    col3.metric(
        "Faixa etária",
        f"{df_filtrado['idade'].min()} - {df_filtrado['idade'].max()}"
    )

    st.markdown("---")

    # Distribuição idade
    fig = px.histogram(
        df_filtrado,
        x="idade",
        nbins=20,
        title="Distribuição da idade dos pacientes"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gênero donut
    genero_counts = df_filtrado['genero'].value_counts().reset_index()
    genero_counts.columns = ['Gênero', 'Quantidade']

    fig = px.pie(
        genero_counts,
        names='Gênero',
        values='Quantidade',
        hole=0.5,
        title="Distribuição por gênero"
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        estado_civil_counts = df_filtrado['estado_civil'].value_counts().reset_index()
        estado_civil_counts.columns = ['Estado civil', 'Quantidade']

        fig = px.bar(
            estado_civil_counts,
            x='Estado civil',
            y='Quantidade',
            color='Estado civil',
            title="Quantidade por estado civil"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        escolaridade_counts = df_filtrado['nivel_escolaridade'].value_counts().reset_index()
        escolaridade_counts.columns = ['Escolaridade', 'Quantidade']

        fig = px.bar(
            escolaridade_counts,
            x='Escolaridade',
            y='Quantidade',
            color='Escolaridade',
            title="Quantidade por escolaridade"
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================
# ABA 2 - PERFIL CLÍNICO
# =========================
with tab2:

    # Diagnóstico horizontal
    diagnostico_counts = df_filtrado['diagnostico_principal'].value_counts().reset_index()
    diagnostico_counts.columns = ['Diagnóstico principal', 'Quantidade']

    fig = px.bar(
        diagnostico_counts,
        x='Quantidade',
        y='Diagnóstico principal',
        orientation='h',
        color='Diagnóstico principal',
        title="Quantidade de pacientes por diagnóstico"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Uso medicação donut
    uso_medicacao_counts = df_filtrado['uso_medicacao'].value_counts(normalize=True) * 100
    uso_medicacao_counts = uso_medicacao_counts.reset_index()
    uso_medicacao_counts.columns = ['Uso de medicação', 'Porcentagem']

    fig = px.pie(
        uso_medicacao_counts,
        names='Uso de medicação',
        values='Porcentagem',
        hole=0.5,
        title="Uso de medicação (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Consultas por ano",
            f"{df_filtrado['numero_consultas_ano'].mean():.0f}"
        )

    with col2:
        st.metric(
            "Nível médio de estresse",
            f"{df_filtrado['nivel_estresse_0_10'].mean():.0f}"
        )

    # Faltas
    faltas_counts = df_filtrado['faltas_consulta'].value_counts().reset_index()
    faltas_counts.columns = ['Faltas', 'Quantidade']

    fig = px.bar(
        faltas_counts,
        x='Faltas',
        y='Quantidade',
        color='Faltas',
        title="Quantidade de pacientes por número de faltas"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Estresse por diagnóstico
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

    # Boxplot estresse
    fig = px.box(
        df_filtrado,
        x="diagnostico_principal",
        y="nivel_estresse_0_10",
        color="diagnostico_principal",
        title="Distribuição do estresse por diagnóstico"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Diagnóstico x Gênero
    diag_genero = (
        df_filtrado
        .groupby(['genero', 'diagnostico_principal'])
        .size()
        .reset_index(name='Quantidade')
    )

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

    # Satisfação donut
    satisfacao_counts = df_filtrado['satisfacao_tratamento_1_5'].value_counts().reset_index()
    satisfacao_counts.columns = ['Satisfação', 'Quantidade']

    fig = px.pie(
        satisfacao_counts,
        names='Satisfação',
        values='Quantidade',
        hole=0.5,
        title="Satisfação com tratamento"
    )

    st.plotly_chart(fig, use_container_width=True)

    # consultas x satisfação
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
        title="Consultas x satisfação"
    )

    st.plotly_chart(fig, use_container_width=True)

    # heatmap
    heat = (
        df_filtrado
        .groupby(['numero_consultas_ano','satisfacao_tratamento_1_5'])
        .size()
        .reset_index(name='Quantidade')
    )

    fig = px.density_heatmap(
        heat,
        x="numero_consultas_ano",
        y="satisfacao_tratamento_1_5",
        z="Quantidade",
        title="Consultas vs Satisfação"
    )

    st.plotly_chart(fig, use_container_width=True)

    # genero x satisfação
    genero_satisfacao = (
        df_filtrado
        .groupby(['genero', 'satisfacao_tratamento_1_5'])
        .size()
        .reset_index(name='Quantidade')
    )

    genero_satisfacao['Proporção (%)'] = (
        genero_satisfacao
        .groupby('genero')['Quantidade']
        .transform(lambda x: x / x.sum() * 100)
    )

    fig = px.bar(
        genero_satisfacao,
        x='genero',
        y='Proporção (%)',
        color='satisfacao_tratamento_1_5',
        barmode='stack',
        title="Satisfação com tratamento por gênero"
    )

    st.plotly_chart(fig, use_container_width=True)

    # estresse x satisfação
    fig = px.scatter(
        df_filtrado,
        x="nivel_estresse_0_10",
        y="satisfacao_tratamento_1_5",
        color="genero",
        title="Relação entre estresse e satisfação"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# ABA 4 - CONCLUSÕES (INALTERADA)
# =========================
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
    st.markdown("----")

    st.markdown(f"""
**Autor:** Samuel de Andrade da Silva  
**Versão:** 1.0  
**Contato:** [samuelsilva00935@gmail.com](mailto:samuelsilva00935@gmail.com)

**Observação:** Dados fictícios utilizados exclusivamente para fins educacionais e prática em análise de dados.  
**Licença:** MIT
""")



































