# gerar_dashboard.py
import pandas as pd
import plotly.express as px
import panel as pn
import json

# --- CONFIGURAÇÃO DAS COLUNAS ---
# Os nomes aqui devem corresponder aos nomes definidos no script de pré-processamento.
COLUNA_DATA = 'data da venda'
COLUNA_VALOR_VENDA = 'Valor total da venda'
COLUNA_REGIONAL = 'regional'
COLUNA_CONSULTOR = 'consultor'
COLUNA_UNIDADE_NEGOCIO = 'unid negocio'
# -----------------------------------

print("Iniciando a geração do dashboard a partir dos dados pré-processados...")

# Garante que a extensão do Plotly seja carregada
pn.extension('plotly')

# --- CARREGAMENTO DOS DADOS PRÉ-PROCESSADOS ---
with open('kpis.json', 'r') as f:
    kpis = json.load(f)

df_regional = pd.read_csv('summary_regional.csv')
df_consultor = pd.read_csv('summary_consultor.csv')
df_unidade = pd.read_csv('summary_unidade.csv')
df_mensal = pd.read_csv('summary_mensal.csv')
print("Arquivos de resumo carregados.")

# --- CRIAÇÃO DOS GRÁFICOS (AGORA MUITO MAIS RÁPIDA) ---

vendas_regional = px.bar(
    df_regional, x=COLUNA_REGIONAL, y=COLUNA_VALOR_VENDA,
    title='Faturamento por Regional', text_auto='.2s'
).update_layout(yaxis_title='Faturamento (R$)', xaxis_title='Regional')

vendas_consultor = px.bar(
    df_consultor, x=COLUNA_VALOR_VENDA, y=COLUNA_CONSULTOR,
    title='Top 10 Consultores por Faturamento', text_auto='.2s', orientation='h'
).update_layout(xaxis_title='Faturamento (R$)', yaxis_title='Consultor')

vendas_unidade_negocio = px.pie(
    df_unidade, names=COLUNA_UNIDADE_NEGOCIO, values=COLUNA_VALOR_VENDA,
    title='Faturamento por Unidade de Negócio', hole=0.4
)

evolucao_vendas = px.line(
    df_mensal, x=COLUNA_DATA, y=COLUNA_VALOR_VENDA,
    title='Evolução Mensal do Faturamento', markers=True
).update_layout(xaxis_title='Mês', yaxis_title='Faturamento (R$)')
print("Gráficos criados.")

# --- MONTAGEM DO LAYOUT DO DASHBOARD ---
kpi_faturamento = pn.indicators.Number(name='Faturamento Total', value=kpis['faturamento_total'], format='R$ {value:,.2f}')
kpi_ticket_medio = pn.indicators.Number(name='Ticket Médio', value=kpis['ticket_medio'], format='R$ {value:,.2f}')
kpi_total_contratos = pn.indicators.Number(name='Total de Contratos', value=kpis['total_contratos'], format='{value:,.0f}')

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

print("Dashboard 'index.html' gerado com sucesso!")
