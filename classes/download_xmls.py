import time
import logging
import os 
import glob
import zipfile
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Download_XML:

    def __init__(self, nav, wait_time=20):
        """
        Construtor da classe. Recebe o navegador já logado.
        Configura e cria as pastas de download.
        """
        self.nav = nav
        self.wait = WebDriverWait(self.nav, wait_time)
        self.download_path = Path.home() / "XML- Robô Innovaro/arquivos-xmls"
        os.makedirs(self.download_path, exist_ok=True)
        try:
            print(f"Configurando pasta de download do Chrome para: {self.download_path}")
            self.nav.execute_cdp_cmd(
                'Page.setDownloadBehavior',
                {'behavior': 'allow', 'downloadPath': str(self.download_path)}
            )
            print("Pasta de download configurada com sucesso via CDP.")
        except Exception as e:
            print(f"AVISO: Não foi possível configurar a pasta de download via CDP: {e}")
            self.download_path = Path.home() / "Downloads"
        self.pasta_destino_drive = self.download_path
        print(f"Monitorando downloads em: {self.download_path}")
        print(f"Arquivos XML serão salvos em: {self.pasta_destino_drive}")

    
    def preencher_variaveis_manifesto(self):
        try:
            # --- Data Inicial ---
            print("Preenchendo Data Inicial...")
            xpath_data_inicial = '//*[@id="vars"]/tbody/tr[1]/td[1]/table/tbody/tr/td/table/tbody/tr[1]/td[2]/table/tbody/tr/td[1]/input'
            campo_data_inicial = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_data_inicial))
            )
            campo_data_inicial.click()
            time.sleep(2)
            campo_data_inicial.send_keys(Keys.CONTROL, 'a')
            campo_data_inicial.send_keys('-1')
            time.sleep(2)
            
            # --- Data Final ---
            print("Preenchendo Data Final...")
            xpath_data_final = '//*[@id="vars"]/tbody/tr[1]/td[1]/table/tbody/tr/td/table/tbody/tr[3]/td[2]/table/tbody/tr/td[1]/input'
            campo_data_final = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_data_final))
            )
            campo_data_final.click()
            time.sleep(2)
            campo_data_final.send_keys(Keys.CONTROL, 'a')
            campo_data_final.send_keys('-1')
            time.sleep(2)
            campo_data_final.send_keys(Keys.TAB)
            time.sleep(2)
            
            print("Datas preenchidas com '-1'.")

        except Exception as e:
            print(f"Ocorreu um erro durante o preenchimento da data inicial e final: {e}")
            logging.error(f"Ocorreu um erro durante o preenchimento da data inicial e final: {e}")
    
    
    def _esperar_download_concluir(self, timeout=60):
        """
        Método auxiliar para esperar o download ser concluído.
        Verifica a pasta de download por arquivos .zip e .crdownload.
        """
        print(f"Aguardando download na pasta: {self.download_path}")
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # Converte self.download_path para string para o os.path.join
            path_str = str(self.download_path)
            
            # Procura por arquivos .crdownload (download em andamento do Chrome)
            crdownload_files = glob.glob(os.path.join(path_str, "*.crdownload"))
            
            if not crdownload_files:
                # Se não houver .crdownload, procura por .zip
                zip_files = glob.glob(os.path.join(path_str, "*.zip"))
                if zip_files:
                    # Encontrou um .zip e nenhum download em andamento
                    arquivo_zip_path = zip_files[0] # Pega o primeiro .zip encontrado
                    
                    time.sleep(2) # Espera extra para o S.O. liberar o arquivo
                    print(f"Download concluído: {arquivo_zip_path}")
                    return arquivo_zip_path
            
            time.sleep(1) # Espera 1 segundo antes de verificar novamente
            
        raise Exception(f"Tempo esgotado ({timeout}s). Nenhum arquivo .zip concluído foi encontrado.")

    
    def _descompactar_zip(self, arquivo_zip_path):
        """
        Método auxiliar para descompactar arquivos .zip, pulando os que já existem.
        Informa a contagem de arquivos totais e importados.
        """
        try:
            print(f"Processando '{arquivo_zip_path}' para '{self.pasta_destino_drive}'...")
            
            # --- NOVOS CONTADORES ---
            total_arquivos_no_zip = 0
            arquivos_importados = 0
            
            with zipfile.ZipFile(arquivo_zip_path, 'r') as zip_ref:
                
                # Pega a lista de todos os arquivos dentro do .zip
                lista_de_arquivos = zip_ref.infolist()
                
                for file_info in lista_de_arquivos:
                    # Pula diretórios (ex: pastas dentro do zip)
                    if file_info.is_dir():
                        continue
                        
                    # É um arquivo, conta ele
                    total_arquivos_no_zip += 1
                    
                    # Pega apenas o nome do arquivo (ex: 'nota.xml')
                    # Ignora a estrutura de pastas de dentro do .zip
                    nome_arquivo = Path(file_info.filename).name
                    
                    # Monta o caminho de destino final
                    caminho_destino_completo = self.pasta_destino_drive / nome_arquivo
                    
                    # --- LÓGICA DE VERIFICAÇÃO ---
                    if caminho_destino_completo.exists():
                        print(f"  -> Ignorando '{nome_arquivo}': Arquivo já existe.")
                    else:
                        print(f"  -> Importando '{nome_arquivo}': Novo arquivo.")
                        
                        # Extrai o arquivo individualmente
                        # Lendo e escrevendo para "achatar" a estrutura do zip
                        dados_do_arquivo = zip_ref.read(file_info.filename)
                        with open(caminho_destino_completo, 'wb') as f_out:
                            f_out.write(dados_do_arquivo)
                            
                        arquivos_importados += 1
            
            # --- RELATÓRIO FINAL ---
            print("="*30)
            print("Relatório de Descompactação:")
            print(f"Total de arquivos no .zip: {total_arquivos_no_zip}")
            print(f"Arquivos novos importados:  {arquivos_importados}")
            print(f"Arquivos ignorados (já existem): {total_arquivos_no_zip - arquivos_importados}")
            print("="*30)

            # Remove o arquivo .zip após descompactar
            os.remove(arquivo_zip_path)
            print(f"Arquivo .zip removido: {arquivo_zip_path}")
            
            return str(self.pasta_destino_drive) # Retorna o caminho como string

        except zipfile.BadZipFile:
            print(f"Erro: O arquivo '{arquivo_zip_path}' não é um ZIP válido ou está corrompido.")
            logging.error(f"Erro de BadZipFile em {arquivo_zip_path}")
        except Exception as e:
            print(f"Erro ao descompactar o arquivo: {e}")
            logging.error(f"Erro ao descompactar: {e}")
            return None
    

    def download_xml_manifestados(self):
        """
        Clica no botão de download, espera a conclusão e descompacta os arquivos.
        """
        try:
            # (CORREÇÃO: Corrigi o nome da variável, antes estava 'campo_data_final')
            xpath_download_button = '//*[@id="lid-0"]/tbody/tr[1]/td/a'
            
            print("Clicando no botão de download...")
            botao_download = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_download_button))
            )
            
            botao_download.click()
            
            # --- Lógica de Download e Extração ---
            
            # 1. Espera o arquivo .zip aparecer na pasta (ex: C:\Users\TI\arquivos-xmls)
            arquivo_zip_completo = self._esperar_download_concluir()
            
            # 2. Descompacta o arquivo na mesma pasta
            pasta_dos_xmls = self._descompactar_zip(arquivo_zip_completo)
            
            print(f"Processo finalizado. XMLs estão em: {pasta_dos_xmls}")
            
            return pasta_dos_xmls # Retorna o caminho dos arquivos extraídos

        except Exception as e:
            print(f"Ocorreu um erro durante o processo de download e extração: {e}")
            logging.error(f"Ocorreu um erro durante o processo de download e extração: {e}")
            return None