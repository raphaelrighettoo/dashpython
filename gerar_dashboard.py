# gerar_dashboard.py
import pandas as pd
import plotly.express as px
import panel as pn

# --- CONFIGURAÇÃO DAS COLUNAS ---
# ATENÇÃO: Verifique se os nomes abaixo correspondem EXATAMENTE
# aos nomes das colunas no seu arquivo CSV.
COLUNA_DATA = 'Data da Venda'
COLUNA_VALOR_VENDA = 'Valor total da venda'
COLUNA_REGIONAL = 'regional'
COLUNA_CONSULTOR = 'consultor'
COLUNA_UNIDADE_NEGOCIO = 'unid negocio'
COLUNA_TIPO_CONTRATO = 'se é novo ou renovação'
# -----------------------------------

# Garante que a extensão do Plotly seja carregada
pn.extension('plotly')

# Carrega os dados do seu arquivo CSV
try:
    df = pd.read_csv('dados.csv', sep=';')
except Exception:
    df = pd.read_csv('dados.csv', sep=',')

# --- LIMPEZA E PREPARAÇÃO DOS DADOS (VERSÃO OTIMIZADA) ---

# 1. Converte a coluna de data para o formato de data, esperando o dia primeiro
df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], dayfirst=True, errors='coerce')

# 2. Converte a coluna de valor para um formato numérico diretamente.
#    Esta é a principal otimização para evitar o timeout.
#    IMPORTANTE: Isso assume que a coluna de valor no seu CSV já é um número
#    (ex: 1234.56) e não contém "R$", pontos de milhar ou vírgulas para decimais.
df[COLUNA_VALOR_VENDA] = pd.to_numeric(df[COLUNA_VALOR_VENDA], errors='coerce')

# Remove linhas onde a conversão de data ou valor falhou, garantindo a integridade
df.dropna(subset=[COLUNA_DATA, COLUNA_VALOR_VENDA], inplace=True)


# --- CÁLCULO DOS KPIs ---
faturamento_total = df[COLUNA_VALOR_VENDA].sum()
total_contratos = len(df)
ticket_medio = faturamento_total / total_contratos if total_contratos > 0 else 0

# --- CRIAÇÃO DOS GRÁFICOS ---
vendas_regional = px.bar(
    df.groupby(COLUNA_REGIONAL)[COLUNA_VALOR_VENDA].sum().sort_values(ascending=False).reset_index(),
    x=COLUNA_REGIONAL, y=COLUNA_VALOR_VENDA,
    title='Faturamento por Regional', text_auto='.2s'
).update_layout(yaxis_title='Faturamento (R$)', xaxis_title='Regional')

top_10_consultores = df.groupby(COLUNA_CONSULTOR)[COLUNA_VALOR_VENDA].sum().nlargest(10).sort_values().reset_index()
vendas_consultor = px.bar(
    top_10_consultores,
    x=COLUNA_VALOR_VENDA, y=COLUNA_CONSULTOR,
    title='Top 10 Consultores por Faturamento', text_auto='.2s', orientation='h'
).update_layout(xaxis_title='Faturamento (R$)', yaxis_title='Consultor')

vendas_unidade_negocio = px.pie(
    df, names=COLUNA_UNIDADE_NEGOCIO, values=COLUNA_VALOR_VENDA,
    title='Faturamento por Unidade de Negócio', hole=0.4
)

df_mensal = df.set_index(COLUNA_DATA).groupby(pd.Grouper(freq='ME'))[COLUNA_VALOR_VENDA].sum().reset_index()
evolucao_vendas = px.line(
    df_mensal, x=COLUNA_DATA, y=COLUNA_VALOR_VENDA,
    title='Evolução Mensal do Faturamento', markers=True
).update_layout(xaxis_title='Mês', yaxis_title='Faturamento (R$)')


# --- MONTAGEM DO LAYOUT DO DASHBOARD ---
kpi_faturamento = pn.indicators.Number(name='Faturamento Total', value=faturamento_total, format='R$ {value:,.2f}')
kpi_ticket_medio = pn.indicators.Number(name='Ticket Médio', value=ticket_medio, format='R$ {value:,.2f}')
kpi_total_contratos = pn.indicators.Number(name='Total de Contratos', value=total_contratos, format='{value:,.0f}')

dashboard = pn.Column(
    pn.Row(
        pn.pane.Markdown("# Dashboard de Vendas Estratégico", styles={'font-size': '24pt', 'margin-left': '20px'}),
        align='center'
    ),
    pn.Row(
        kpi_faturamento, kpi_ticket_medio, kpi_total_contratos,
        align='center', styles={'gap': '2em'}
    ),
    pn.layout.Divider(),
    pn.Row(
        pn.Column(vendas_regional, evolucao_vendas),
        pn.Column(vendas_consultor, vendas_unidade_negocio)
    ),
    sizing_mode='stretch_width'
)

# --- SALVAR O DASHBOARD ---
dashboard.save(
    'index.html',
    embed=True,
    title='Dashboard de Vendas'
)

print("Dashboard 'index.html' gerado com sucesso.")
