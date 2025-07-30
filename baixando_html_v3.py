import os
import time
import random
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Cria a pasta de destino se não existir
os.makedirs('anuncios_html', exist_ok=True)

# Lê os links do Excel
df = pd.read_excel('links_olx.xlsx')
links = df['link'].tolist()

# Padrão para validar links aceitáveis
padrao_aceito = re.compile(
    r'^https://rn\.olx\.com\.br/rio-grande-do-norte/autos-e-pecas/carros-vans-e-utilitarios/.+-\d+$'
)

# Filtra os links válidos e que ainda não foram baixados
links_validos = [
    (i, link) for i, link in enumerate(links, 1)
    if padrao_aceito.match(link) and not os.path.exists(f"anuncios_html/anuncio_{i}.html")
]

# Função para configurar o driver
def configurar_driver():
    options = Options()
    options.headless = True
    options.set_preference("intl.accept_languages", "pt-BR,pt")
    options.set_preference("general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    service = Service()
    driver = webdriver.Firefox(service=service, options=options)
    return driver

# Função que baixa um único anúncio
def baixar_anuncio(i, link):
    inicio = time.time()
    nome_arquivo = f"anuncios_html/anuncio_{i}.html"

    try:
        print(f"{i}/{len(links)} - acessando {link}")
        driver = configurar_driver()
        driver.get(link)
        time.sleep(random.uniform(1, 2))  # Espera carregar

        html = driver.page_source
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(html)

        with open("log_downloads.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"{i}/{len(links)} - Sucesso: {link}\n")

        print(f"✅ Salvo: {nome_arquivo}")

    except Exception as e:
        print(f"❌ Erro ao processar {link}: {e}")
        with open("falhas.txt", "a", encoding="utf-8") as fail_file:
            fail_file.write(link + "\n")
    finally:
        try:
            driver.quit()
        except:
            pass

    fim = time.time()
    return fim - inicio  # retorna a duração

# Tempo total e início
tempo_total = 0
inicio_total = time.time()

# Usa ThreadPoolExecutor com 2 navegadores paralelos
with ThreadPoolExecutor(max_workers=6) as executor:
    futuros = {executor.submit(baixar_anuncio, i, link): (i, link) for i, link in links_validos}

    processados = 0
    for futuro in as_completed(futuros):
        duracao = futuro.result()
        tempo_total += duracao
        processados += 1
        restante = len(links_validos) - processados
        tempo_medio = tempo_total / processados
        estimado_restante = tempo_medio * restante
        horas, resto = divmod(int(estimado_restante), 3600)
        minutos, segundos = divmod(resto, 60)
        print(f"⏳ Estimativa de término: ~{horas}h {minutos}min {segundos}s restantes")
