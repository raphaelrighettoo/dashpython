# gerar_dashboard.py
import pandas as pd
import plotly.express as px
import panel as pn

# --- CONFIGURAÇÃO DAS COLUNAS ---
# Verifique se os nomes à direita correspondem EXATAMENTE aos do seu arquivo CSV.
# Esta é a etapa mais importante para evitar erros.
COL_ANO = 'ano'
COL_MES = 'mes'
COL_REGIONAL = 'regional'
COL_CONSULTOR = 'consultor'
COL_PARCEIRO = 'nome parceiro'
COL_FATURAMENTO = 'Valor total da venda'
COL_META = 'valor meta'
COL_TIPO_CONTRATO = 'modalidade'
COL_DATA_VENDA = 'data da venda'
COL_NOVOS_CLIENTES = 'novo?'
COL_UNIDADE_NEGOCIO = 'unid negocio'
# --- FIM DA CONFIGURAÇÃO ---


# Função para carregar e limpar os dados
# Esta função será executada apenas uma vez.
@pn.cache
def carregar_dados():
    """
    Carrega os dados do CSV, valida as colunas, faz a limpeza e prepara para análise.
    A função é armazenada em cache para performance.
    """
    try:
        # Tenta carregar com separador ponto e vírgula
        df = pd.read_csv('dados.csv', sep=';', encoding='utf-8')
    except FileNotFoundError:
        print("ERRO: O arquivo 'dados.csv' não foi encontrado.")
        print("Por favor, certifique-se de que o arquivo está na mesma pasta que o script.")
        exit() # Encerra o script se o arquivo não for encontrado
    except Exception:
        # Se falhar, tenta com separador vírgula
        df = pd.read_csv('dados.csv', sep=',', encoding='utf-8')

    # --- Validação das Colunas ---
    # Remove espaços em branco do início e fim dos nomes das colunas
    df.columns = df.columns.str.strip()

    # Lista de todas as colunas que o script espera encontrar
    colunas_necessarias = [
        COL_ANO, COL_MES, COL_REGIONAL, COL_CONSULTOR, COL_PARCEIRO,
        COL_FATURAMENTO, COL_META, COL_TIPO_CONTRATO, COL_DATA_VENDA,
        COL_NOVOS_CLIENTES, COL_UNIDADE_NEGOCIO
    ]

    # Verifica quais colunas estão faltando no DataFrame carregado
    colunas_faltando = [col for col in colunas_necessarias if col not in df.columns]

    if colunas_faltando:
        print("\n--- ERRO: COLUNAS NÃO ENCONTRADAS ---")
        print("Algumas colunas configuradas no script não existem no seu arquivo CSV.")
        print("\nColunas que estão faltando:")
        for col in colunas_faltando:
            print(f"  - '{col}'")
        
        print("\nColunas que foram encontradas no seu arquivo:")
        for col in df.columns:
            print(f"  - '{col}'")
            
        print("\n--> AÇÃO: Por favor, corrija os nomes na seção 'CONFIGURAÇÃO DAS COLUNAS' do script e tente novamente.")
        exit() # Encerra o script para o usuário poder corrigir

    # Limpeza e conversão de colunas numéricas
    for col in [COL_FATURAMENTO, COL_META]:
        if df[col].dtype == 'object':
            # Converte para string para garantir que os métodos .str funcionem
            df[col] = df[col].astype(str)
            df[col] = df[col].str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

    # Conversão da coluna de data
    df[COL_DATA_VENDA] = pd.to_datetime(df[COL_DATA_VENDA], dayfirst=True, errors='coerce')
    
    # Garante que as colunas de filtro não tenham valores nulos (NaN)
    for col in [COL_ANO, COL_MES, COL_REGIONAL, COL_CONSULTOR, COL_PARCEIRO, COL_TIPO_CONTRATO, COL_UNIDADE_NEGOCIO, COL_NOVOS_CLIENTES]:
        df[col] = df[col].fillna('Não informado')

    return df

# Carrega os dados usando a função cacheada
df = carregar_dados()

# --- Criação dos Widgets de Filtro ---
# As opções dos filtros são extraídas diretamente dos dados carregados.

# Opções para os filtros (adicionando 'Todos' no início)
def get_options(column_name):
    options = df[column_name].unique().tolist()
    # Converte todos os itens para string para evitar erros de ordenação com tipos mistos
    options = sorted([str(opt) for opt in options])
    return ['Todos'] + options

filtro_ano = pn.widgets.Select(name='Ano', options=get_options(COL_ANO))
filtro_mes = pn.widgets.Select(name='Mês', options=get_options(COL_MES))
filtro_regional = pn.widgets.Select(name='Regional', options=get_options(COL_REGIONAL))
filtro_consultor = pn.widgets.Select(name='Consultor', options=get_options(COL_CONSULTOR))
filtro_parceiro = pn.widgets.Select(name='Parceiro', options=get_options(COL_PARCEIRO))


# --- Função Reativa Principal ---
# Esta função é o coração do dashboard. Ela depende dos filtros
# e re-executa sempre que um filtro é alterado.
@pn.depends(
    filtro_ano.param.value,
    filtro_mes.param.value,
    filtro_regional.param.value,
    filtro_consultor.param.value,
    filtro_parceiro.param.value
)
def atualizar_dashboard(ano, mes, regional, consultor, parceiro):
    
    # 1. Filtrar os dados com base nos widgets
    df_filtrado = df.copy()
    if ano != 'Todos':
        df_filtrado = df_filtrado[df_filtrado[COL_ANO].astype(str) == ano]
    if mes != 'Todos':
        df_filtrado = df_filtrado[df_filtrado[COL_MES].astype(str) == mes]
    if regional != 'Todos':
        df_filtrado = df_filtrado[df_filtrado[COL_REGIONAL] == regional]
    if consultor != 'Todos':
        df_filtrado = df_filtrado[df_filtrado[COL_CONSULTOR] == consultor]
    if parceiro != 'Todos':
        df_filtrado = df_filtrado[df_filtrado[COL_PARCEIRO] == parceiro]

    # 2. Calcular os KPIs
    faturamento = df_filtrado[COL_FATURAMENTO].sum()
    meta = df_filtrado[COL_META].sum()
    atingimento = (faturamento / meta) * 100 if meta > 0 else 0
    num_vendas = len(df_filtrado)
    ticket_medio = faturamento / num_vendas if num_vendas > 0 else 0
    
    # Tratamento para a coluna 'novo?'
    # Converte para minúsculas para uma comparação mais robusta
    novos_clientes = len(df_filtrado[df_filtrado[COL_NOVOS_CLIENTES].astype(str).str.lower() == 'sim'])

    # 3. Criar os Indicadores (KPIs) - FORMATO CORRIGIDO
    kpi_faturamento = pn.indicators.Number(name='Faturamento', value=faturamento, format='R$ {value:,.2f}')
    kpi_meta = pn.indicators.Number(name='Meta', value=meta, format='R$ {value:,.2f}')
    kpi_atingimento = pn.indicators.Number(name='Atingimento', value=atingimento, format='{value:.2f}%')
    kpi_ticket_medio = pn.indicators.Number(name='Ticket Médio', value=ticket_medio, format='R$ {value:,.2f}')
    kpi_novos_clientes = pn.indicators.Number(name='Novos Clientes', value=novos_clientes, format='{value}')
    kpi_num_vendas = pn.indicators.Number(name='Nº de Vendas', value=num_vendas, format='{value}')
    
    # Se não houver dados, mostrar uma mensagem em vez dos gráficos
    if df_filtrado.empty:
        return pn.Column(
            pn.Row(kpi_faturamento, kpi_meta, kpi_atingimento, kpi_ticket_medio, kpi_novos_clientes, kpi_num_vendas),
            pn.pane.Markdown("### Sem dados para a seleção atual.")
        )

    # 4. Criar os Gráficos
    # Gráfico: Faturamento por Regional
    vendas_regional = df_filtrado.groupby(COL_REGIONAL)[COL_FATURAMENTO].sum().sort_values(ascending=True).reset_index()
    g_regional = px.bar(vendas_regional, x=COL_FATURAMENTO, y=COL_REGIONAL, orientation='h', title='Faturamento por Regional')
    g_regional.update_layout(yaxis={'categoryorder':'total ascending'})

    # Gráfico: Top 10 Consultores
    top_consultores = df_filtrado.groupby(COL_CONSULTOR)[COL_FATURAMENTO].sum().nlargest(10).sort_values(ascending=True).reset_index()
    g_consultores = px.bar(top_consultores, x=COL_FATURAMENTO, y=COL_CONSULTOR, orientation='h', title='Top 10 Consultores')

    # Gráfico: Faturamento por Mês
    vendas_mes = df_filtrado.groupby(COL_MES)[[COL_FATURAMENTO, COL_META]].sum().reset_index()
    g_mes = px.line(vendas_mes, x=COL_MES, y=[COL_FATURAMENTO, COL_META], title='Faturamento x Meta por Mês')
    
    # Gráfico: Faturamento por Parceiro
    vendas_parceiro = df_filtrado.groupby(COL_PARCEIRO)[COL_FATURAMENTO].sum().nlargest(10).sort_values(ascending=True).reset_index()
    g_parceiro = px.bar(vendas_parceiro, x=COL_FATURAMENTO, y=COL_PARCEIRO, orientation='h', title='Top 10 Parceiros')

    # Gráfico: Novos x Renovação
    vendas_tipo = df_filtrado.groupby(COL_TIPO_CONTRATO)[COL_FATURAMENTO].sum().reset_index()
    g_tipo = px.pie(vendas_tipo, values=COL_FATURAMENTO, names=COL_TIPO_CONTRATO, title='Faturamento: Novo x Renovação', hole=.4)

    # Gráfico: Faturamento por Unidade de Negócio
    vendas_un = df_filtrado.groupby(COL_UNIDADE_NEGOCIO)[COL_FATURAMENTO].sum().reset_index()
    g_un = px.pie(vendas_un, values=COL_FATURAMENTO, names=COL_UNIDADE_NEGOCIO, title='Faturamento por Unidade de Negócio', hole=.4)

    # 5. Montar o layout dos gráficos
    layout_graficos = pn.Column(
        pn.Row(
            pn.Card(g_regional, title='Vendas por Regional', sizing_mode='stretch_width'),
            pn.Card(g_consultores, title='Top Consultores', sizing_mode='stretch_width')
        ),
        pn.Row(
            pn.Card(g_mes, title='Desempenho Mensal', sizing_mode='stretch_width')
        ),
        pn.Row(
            pn.Card(g_parceiro, title='Top Parceiros', sizing_mode='stretch_width'),
            pn.Card(g_tipo, title='Tipo de Contrato', sizing_mode='stretch_width'),
            pn.Card(g_un, title='Unidade de Negócio', sizing_mode='stretch_width')
        )
    )

    return pn.Column(
        pn.Row(kpi_faturamento, kpi_meta, kpi_atingimento, kpi_ticket_medio, kpi_novos_clientes, kpi_num_vendas),
        pn.layout.Divider(),
        layout_graficos
    )


# --- Montagem Final do Dashboard ---
# Criamos a estrutura manualmente para evitar o erro do 'Template.save()'

# Barra Lateral com os filtros
sidebar = pn.Column(
    pn.pane.Markdown("## Filtros"),
    filtro_ano,
    filtro_mes,
    filtro_regional,
    filtro_consultor,
    filtro_parceiro,
    width=250 # Largura fixa para a barra lateral
)

# Conteúdo Principal que se atualiza
main_content = pn.Column(
    pn.pane.Markdown("## Análise de Vendas"),
    atualizar_dashboard # A função reativa é o conteúdo principal
)

# Layout final juntando a barra lateral e o conteúdo
dashboard_final = pn.Row(
    sidebar,
    main_content
)

# --- Salvar o Dashboard como um arquivo HTML estático ---
dashboard_final.save(
    'index.html',
    embed=True, # Garante que todo o JS/CSS necessário esteja no arquivo
    title="Dashboard Comercial",
    max_states=1000000 # Aumenta o limite de estados para evitar o warning
)

print("Dashboard interativo 'index.html' gerado com sucesso.")
