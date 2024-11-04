import pandas as pd

# Carregar os arquivos CSV
file_paths = ['/caminho/para/seu/csv']
dfs = [pd.read_csv(path, encoding='ISO-8859-1') for path in file_paths]

# Unir os DataFrames em um único DataFrame consolidado
df_consolidado = pd.concat(dfs, ignore_index=True)

# Análise 01: Tipos/nomes dos protocolos encontrados
protocolos_encontrados = df_consolidado['Protocol'].unique()

# Análise 02: Quantidade e % do total monitorado, de pacotes do tipo broadcast
total_pacotes = len(df_consolidado)
pacotes_broadcast = df_consolidado[df_consolidado['Destination'].str.lower() == 'broadcast']
qtd_broadcast = len(pacotes_broadcast)
percentual_broadcast = (qtd_broadcast / total_pacotes) * 100

# Análise 04: Total de pacotes e bytes capturados por protocolo e % do total
tabela_protocolo = df_consolidado.groupby('Protocol').agg({
    'Length': ['count', 'sum']
}).reset_index()
tabela_protocolo.columns = ['Protocol', 'Packet Count', 'Total Bytes']
tabela_protocolo['% Total Packets'] = (tabela_protocolo['Packet Count'] / total_pacotes) * 100
tabela_protocolo['% Total Bytes'] = (tabela_protocolo['Total Bytes'] / df_consolidado['Length'].sum()) * 100

# Análise 05: Consumo total da rede no período monitorado
total_bytes = df_consolidado['Length'].sum()

# Análise 06: Tabela com o tamanho dos pacotes encontrados
tabela_tamanho_pacotes = df_consolidado['Length'].value_counts().reset_index()
tabela_tamanho_pacotes.columns = ['Packet Size', 'Count']

# Análise 07: Sites mais acessados (captura de domínios com .com, .net, etc.)
sites_acessados = df_consolidado['Info'].str.extract(r'(?P<site>\b[\w\.-]+\.(com|net|org|gov|edu|br|co|uk|io|us)\b)', expand=False)
sites_acessados = sites_acessados.dropna()['site'].value_counts().reset_index()
sites_acessados.columns = ['Site', 'Access Count']

# Exibir apenas os 5 sites mais acessados
sites_acessados_top5 = sites_acessados.head(5)

print("\n07) Sites mais acessados:")
print(sites_acessados_top5)


# Exibir os resultados
print("01) Protocolos encontrados:")
print(protocolos_encontrados)
print("\n02) Quantidade e % de pacotes broadcast:")
print(f"Quantidade: {qtd_broadcast}, Percentual: {percentual_broadcast:.2f}%")
print("\n04) Total de pacotes e bytes por protocolo:")
print(tabela_protocolo)
print("\n05) Consumo total da rede:")
print(f"Total de pacotes: {total_pacotes}, Total de bytes: {total_bytes}")
print("\n06) Tabela com o tamanho dos pacotes:")
print(tabela_tamanho_pacotes)
print("\n07) Sites mais acessados:")
print(sites_acessados)
