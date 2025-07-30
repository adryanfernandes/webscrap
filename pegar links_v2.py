import os
import time
import random
import pandas as pd
import logging
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração de log
logging.basicConfig(filename='coleta_olx.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Carrega links anteriores se houver
def carregar_links_existentes(caminho='links_olx.xlsx'):
    if os.path.exists(caminho):
        df_existente = pd.read_excel(caminho)
        return set(df_existente['link'].dropna().tolist())
    return set()

# Configura o driver do Firefox
def configurar_driver(headless=True):
    options = Options()
    options.headless = headless
    options.set_preference("intl.accept_languages", "pt-BR,pt")
    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0")
    service = Service()
    return webdriver.Firefox(service=service, options=options)

# Salva a página atual em um arquivo
def salvar_pagina_atual(pagina, caminho='pagina_atual.txt'):
    with open(caminho, 'w') as f:
        f.write(str(pagina))

# Carrega a última página salva, se houver
def carregar_pagina_atual(caminho='pagina_atual.txt'):
    if os.path.exists(caminho):
        with open(caminho, 'r') as f:
            return int(f.read().strip())
    return 1

# Coleta os links de todas as páginas
def coletar_links(driver, url_base, links_existentes):
    todos_links = set(links_existentes)
    pagina = carregar_pagina_atual()
    logging.info(f"Iniciando da página {pagina}")

    while True:
        url = f"{url_base}&o={pagina}" if "?" in url_base else f"{url_base}?o={pagina}"
        logging.info(f"Acessando: {url}")

        # Tenta acessar a página com 3 tentativas
        for tentativa in range(3):
            try:
                driver.get(url)
                break
            except Exception as e:
                logging.warning(f"Tentativa {tentativa+1} falhou: {e}")
                time.sleep(5)

        time.sleep(3)

        # Scroll para forçar carregamento
        for _ in range(random.randint(3, 7)):
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(1, 2))

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-testid='adcard-link']"))
            )
        except:
            logging.warning(f"Página {pagina} não carregou corretamente. Encerrando.")
            break

        # Coleta de links com barra de progresso
        elementos = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='adcard-link']")
        novos_links = []
        for el in tqdm(elementos, desc=f"Página {pagina}", unit="link"):
            href = el.get_attribute('href')
            if href and href not in todos_links:
                novos_links.append(href)

        if not novos_links:
            logging.info(f"Sem novos links na página {pagina}. Encerrando.")
            break

        todos_links.update(novos_links)
        logging.info(f"{len(novos_links)} novos links coletados na página {pagina} (Total: {len(todos_links)}).")

        # Salva progresso da página atual
        salvar_pagina_atual(pagina)

        # Backup a cada 5 páginas
        if pagina % 5 == 0:
            df_temp = pd.DataFrame({'link': list(todos_links)})
            df_temp.to_excel('links_olx_backup.xlsx', index=False)
            logging.info(f"Backup salvo com {len(todos_links)} links.")

        # Verifica se há próxima página
        try:
            driver.find_element(By.LINK_TEXT, "Próxima página")
            pagina += 1
            time.sleep(random.uniform(2, 4))
        except:
            logging.info("Não há próxima página.")
            break

    return list(todos_links)

# Função principal
def main():
    base_url = "https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/estado-rn?lis=home_body_search_bar_2020"
    links_existentes = carregar_links_existentes()

    driver = configurar_driver(headless=False)  # Use True no servidor
    try:
        logging.info("Iniciando coleta de links...")
        links = coletar_links(driver, base_url, links_existentes)
        logging.info(f"Total final: {len(links)} links únicos coletados.")

        df = pd.DataFrame({'link': links})
        df.to_excel('links_olx.xlsx', index=False)
        logging.info('✅ Links salvos com sucesso em "links_olx.xlsx".')

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
