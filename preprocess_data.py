# preprocess_data.py
import pandas as pd
import json

# --- CONFIGURAÇÃO DAS COLUNAS ---
# Garanta que estes nomes correspondem EXATAMENTE ao seu ficheiro CSV.
COLUNA_DATA = 'data da venda'
COLUNA_VALOR_VENDA = 'valor total da venda'
COLUNA_REGIONAL = 'regional'
COLUNA_CONSULTOR = 'consultor'
COLUNA_UNIDADE_NEGOCIO = 'unid negocio'
COLUNA_TRIMESTRE = 'trimestre'
COLUNA_ANO = 'ano' # Coluna para análise anual
# -----------------------------------

print("Iniciando o pré-processamento dos dados...")

# Carrega o ficheiro de dados completo
try:
    df = pd.read_csv('dados.csv', sep=';')
except Exception:
    df = pd.read_csv('dados.csv', sep=',')

print(f"Ficheiro CSV carregado. {len(df)} linhas encontradas.")

# --- LIMPEZA E PREPARAÇÃO DOS DADOS (VERSÃO MAIS SEGURA) ---

# 1. Converte a coluna de data
print("Convertendo coluna de data...")
df[COLUNA_DATA] = pd.to_datetime(df[COLUNA_DATA], dayfirst=True, errors='coerce')

# 2. Limpa e converte a coluna de valor para um formato numérico
print("Limpando e convertendo coluna de valor...")
# Garante que a coluna é do tipo texto antes de tentar limpar
df['valor_limpo'] = df[COLUNA_VALOR_VENDA].astype(str)
# Remove "R$", espaços e pontos de milhar
df['valor_limpo'] = df['valor_limpo'].str.replace('R$', '', regex=False).str.strip()
df['valor_limpo'] = df['valor_limpo'].str.replace('.', '', regex=False)
# Troca a vírgula do decimal por um ponto
df['valor_limpo'] = df['valor_limpo'].str.replace(',', '.', regex=False)
# Converte para número, tratando erros (o que não for número vira NaN)
df[COLUNA_VALOR_VENDA] = pd.to_numeric(df['valor_limpo'], errors='coerce')


# 3. Remove linhas onde a conversão de data ou valor falhou
linhas_antes = len(df)
df.dropna(subset=[COLUNA_DATA, COLUNA_VALOR_VENDA, COLUNA_TRIMESTRE, COLUNA_ANO], inplace=True)
linhas_depois = len(df)

# IMPRESSÃO DE DIAGNÓSTICO: Informa quantas linhas são válidas
print(f"Limpeza concluída. De {linhas_antes} linhas, {linhas_depois} são válidas e serão processadas.")

if linhas_depois == 0:
    print("\nATENÇÃO: Nenhuma linha de dados válida foi encontrada após a limpeza. Verifique o formato das colunas de data e valor no seu ficheiro CSV.\n")

# --- CÁLCULO DAS AGREGAÇÕES E SALVAMENTO ---

# 1. KPIs (Totais gerais)
faturamento_total = df[COLUNA_VALOR_VENDA].sum()
total_contratos = len(df)
ticket_medio = faturamento_total / total_contratos if total_contratos > 0 else 0

kpis = {
    "faturamento_total": float(faturamento_total),
    "total_contratos": int(total_contratos),
    "ticket_medio": float(ticket_medio)
}
with open('kpis.json', 'w') as f:
    json.dump(kpis, f)
print("KPIs salvos em kpis.json")

# 2. Vendas por Regional (trimestral)
df_regional_trimestral = df.groupby([COLUNA_REGIONAL, COLUNA_TRIMESTRE])[COLUNA_VALOR_VENDA].sum().reset_index()
df_regional_trimestral.to_csv('summary_regional_trimestral.csv', index=False)
print("Resumo por regional (trimestral) salvo em summary_regional_trimestral.csv")

# 3. Top 10 Consultores (total geral)
df_consultor = df.groupby(COLUNA_CONSULTOR)[COLUNA_VALOR_VENDA].sum().nlargest(10).sort_values().reset_index()
df_consultor.to_csv('summary_consultor.csv', index=False)
print("Resumo por consultor salvo em summary_consultor.csv")

# 4. Vendas por Unidade de Negócio (trimestral)
df_unidade_trimestral = df.groupby([COLUNA_UNIDADE_NEGOCIO, COLUNA_TRIMESTRE])[COLUNA_VALOR_VENDA].sum().reset_index()
df_unidade_trimestral.to_csv('summary_unidade_trimestral.csv', index=False)
print("Resumo por unidade de negócio (trimestral) salvo em summary_unidade_trimestral.csv")

# 5. Evolução Trimestral
df_trimestral = df.groupby(COLUNA_TRIMESTRE)[COLUNA_VALOR_VENDA].sum().reset_index()
# Cria colunas para ordenação correta dos trimestres (ex: 1Tri23, 2Tri23...)
df_trimestral['ano'] = '20' + df_trimestral[COLUNA_TRIMESTRE].str.extract(r'(\d+)$').fillna('0')
df_trimestral['trimestre_num'] = df_trimestral[COLUNA_TRIMESTRE].str.extract(r'(\d+)Tri').fillna('0')
df_trimestral = df_trimestral.sort_values(by=['ano', 'trimestre_num'])
df_trimestral.to_csv('summary_trimestral.csv', index=False)
print("Resumo trimestral salvo em summary_trimestral.csv")

# 6. Evolução Anual (NOVO)
df_anual = df.groupby(COLUNA_ANO)[COLUNA_VALOR_VENDA].sum().reset_index()
df_anual.to_csv('summary_anual.csv', index=False)
print("Resumo anual salvo em summary_anual.csv")

print("Pré-processamento concluído com sucesso!")
