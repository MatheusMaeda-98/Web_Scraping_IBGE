import os
import time
import shutil
import threading #bot para organizar os arquivos para as pastas
from queue import Queue
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium import webdriver #pip install selenium
from selenium.webdriver.edge.options import Options as EdgeOptions #necessário estar usando microsoft edge atualizado
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager #pip install webdriver-manager, atualiza o webdriver automaticamente
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
downloads_path = str(Path.home() / "Downloads" / "Acesso_a_internet")



def organizador_ativo(diretorio_alvo, fila_destinos, extensoes=(".zip", ".pdf", ".xls", ".xlsx", ".ods", ".txt")):
    print("🧭 Organizador com subpastas iniciando...\n")
    arquivos_mapeados = set()


    while True:
        if not fila_destinos.empty(): # recebimento da fila destino do selenium
            pasta_destino = fila_destinos.get()
            print(f"📦 Novo caminho solicitado:\n   👉 {pasta_destino}")
            
            # Captura o estado atual da pasta
            existentes = {f.name for f in Path(diretorio_alvo).glob("*")} # comparativo com os novos arquivos que chegarem


            tempo_inicial = time.time() # congela o tempo
            tempo_limite = 30  # segundos , tempo limite para receber um novo arquivo

            while time.time() - tempo_inicial < tempo_limite:
                arquivos_atuais = list(Path(diretorio_alvo).glob("*"))
                novos = [f for f in arquivos_atuais if f.name not in existentes and f.suffix.lower() in extensoes and f.stat().st_size > 0]

                if novos:
                    novo_arquivo = max(novos, key=lambda f: f.stat().st_birthtime)
                    destino = Path(pasta_destino) / novo_arquivo.name
                    Path(pasta_destino).mkdir(parents=True, exist_ok=True)

                    print(f"📄 Novo arquivo identificado: {novo_arquivo.name} ({novo_arquivo.stat().st_size} bytes)")
                    print(f"📍 Destino planejado: {destino}")

                    try:
                        if destino.exists():
                            if destino.is_dir():
                                print(f"⚠️ Conflito: já existe PASTA chamada '{destino.name}'. Removendo...")
                                shutil.rmtree(destino)
                            else:
                                print(f"↪️ Substituindo arquivo existente: {destino.name}")
                                destino.unlink()

                        shutil.move(str(novo_arquivo), str(destino)) # se pasta for de mesmo nome apagar o que estiver lá
                        print(f"✅ Arquivo movido com sucesso")
                        arquivos_mapeados.add(novo_arquivo)
                        break
                    except Exception as e:
                        print(f"❌ Erro ao mover '{novo_arquivo.name}': {e}")
                        break
                else:
                    time.sleep(1)

            else:
                print("⌛ Nenhum novo arquivo encontrado em tempo hábil.\n")
        else:
            time.sleep(0.5)


# Cria a pasta local
def criar_pasta_local(caminho):
    if not os.path.exists(caminho): # se caminho nao existe, criar
        os.makedirs(caminho)

# Baixa o arquivo dado um href
# Exploração recursiva da árvore
def explorar(driver, xpath_atual, pasta_local, fila_destinos, nivel=0):
    i = 1
    

    while True:
        xpath_filho = f"{xpath_atual}/li[{i}]/a"
        try:
            el = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath_filho))
            )

            nome = el.text.strip().replace("/", "_").replace("\\", "_") #nome do elemento fica no text do html
            prefixo_visual = "│   " * nivel + "├── "
            print(prefixo_visual + (nome if nome else "[sem título]"))

            # Avaliação do botão
            if nome.lower().endswith((".zip", ".pdf", ".xls", ".xlsx", ".ods", ".txt")): # se arquivo
                print(f"📨 Enfileirando destino baseado no nome: {pasta_local}")
                fila_destinos.put(pasta_local)

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                driver.execute_script("arguments[0].click();", el)
                time.sleep(1.2)
                print(f"✅ Clique acionado para: {nome}")
                time.sleep(2)

            else: # se for pasta
                nova_pasta = os.path.join(pasta_local, nome if nome else f"subpasta_{i}") #cria a pasta no pc
                criar_pasta_local(nova_pasta)

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                driver.execute_script("arguments[0].click();", el)
                time.sleep(1.2)

                xpath_sem_a = xpath_filho.rsplit("/", 1)[0]
                xpath_ul_filho = xpath_sem_a + "/ul"
                explorar(driver, xpath_ul_filho, nova_pasta, fila_destinos, nivel + 1)

        except Exception as e:
            break  # fim da lista
        i+=1



# Main
if __name__ == "__main__":
    from queue import Queue #criação da fila de destinos dos arquivos
    fila_destinos = Queue()
    t_watcher = threading.Thread(target=organizador_ativo, args=(Path.home() / "Downloads", fila_destinos), daemon=True) #nova thread para trabalhar 
    #em paralelo organizador e webscraping, se script terminar, a thread será encerrado (daemon = true)
    t_watcher.start()

    prefs = { #Essas configurações ajudam a baixar arquivos de forma automática, sem janelas de confirmação
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False
    }
    options = webdriver.EdgeOptions()
    perfil_local = os.path.join(os.path.dirname(__file__), "EdgeProfileKit") #importante: usar o perfil salvo na mesma pasta do main.py
    options.add_argument(f"--user-data-dir={perfil_local}")
    options.add_experimental_option("prefs", {
    "profile.default_content_settings.popups": 0,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": False
    })



    service = EdgeService(EdgeChromiumDriverManager().install())
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(service=service, options = options)
    driver.minimize_window()
    driver.get("edge://settings/downloads")
    time.sleep(2)


    url = "https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html"
    driver.get(url)
    time.sleep(3)

    try:
        WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.ID, "cookie-btn"))
        ).click()
    except:
        pass

    try:
        # Espera a seção "Acesso à Internet" ficar disponível
        raiz_xpath = "/html/body/main/section/div[2]/div/div/section/div/div[2]/ul/li/ul/li[1]/a"
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, raiz_xpath)))
        downloads = str(Path.home() / "Downloads")
        nome_raiz = os.path.join(downloads, "Acesso_a_internet")
        criar_pasta_local(nome_raiz)
        elemento_raiz = driver.find_element(By.XPATH, raiz_xpath)
        time.sleep(0.5)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento_raiz)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", elemento_raiz)
        time.sleep(1)
        
        xpath_sem_a = raiz_xpath.rsplit("/", 1)[0]  # remove o /a final
        xpath_ul = xpath_sem_a + "/ul"
        explorar(driver, xpath_ul, nome_raiz, fila_destinos)



    finally:
        driver.quit()