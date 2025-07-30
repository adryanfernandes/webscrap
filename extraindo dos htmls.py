from bs4 import BeautifulSoup

dados = []
links=2
for i in range(1, len(links)+1):
    arquivo = f'anuncios_html/anuncio_{i}.html'
    with open(arquivo, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Título
    titulo = soup.select_one('span.olx-text--title-medium')
    titulo = titulo.text.strip() if titulo else 'N/A'

    # Preço
    preco = soup.select_one('span.olx-text--title-medium')
    preco = preco.text.strip() if preco else 'N/A'

    # Data
    data_hora = soup.select_one('span.olx-text--caption')
    data_hora = data_hora.text.strip() if data_hora else 'N/A'

    # Área
    area = 'N/A'
    spans = soup.find_all('span')
    for s in spans:
        texto = s.text.strip()
        if texto.endswith('m²'):
            area = texto
            break

    # Quartos
    quartos = 'N/A'
    for s in spans:
        texto = s.text.lower()
        if 'quarto' in texto and any(c.isdigit() for c in texto):
            quartos = texto
            break

    # Vagas
    vagas = 'N/A'
    for s in spans:
        texto = s.text.lower()
        if 'vaga' in texto and any(c.isdigit() for c in texto):
            vagas = texto
            break

    # Coleta final
    dados.append({
        'arquivo': arquivo,
        'titulo': titulo,
        'preco': preco,
        'data_hora': data_hora,
        'area': area,
        'quartos': quartos,
        'vagas': vagas,
    })

# Exporta para Excel
df_final = pd.DataFrame(dados)
df_final.to_excel('anuncios_extraidos.xlsx', index=False)
print("Dados extraídos salvos em 'anuncios_extraidos.xlsx'")
