import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

try:
    from utils import verificar_chrome_driver
except ImportError:
    print("Atenção: Arquivo 'utils.py' não encontrado. O fallback de download do driver não funcionará.")
    # Define uma função 'dummy' para não quebrar o código
    def verificar_chrome_driver():
        return None

class Innovaro:
    """
    Classe de automação para interagir com o sistema Innovaro.
    Gerencia o driver do Selenium e encapsula as ações comuns
    como login, navegação em menus e manipulação de iframes.
    """

    def __init__(self, usuario, senha, url='http://192.168.3.141/sistema', wait_time=20):
        """
        Construtor da classe.
        Inicializa o navegador, define o tempo de espera e 
        executa o login no sistema Innovaro.
        """
        print(f"Iniciando automação no Innovaro: {url}")
        
        try:
            # Tenta iniciar o Chrome (assume que o driver está no PATH)
            self.nav = webdriver.Chrome()
        except Exception as e:
            print(f"Erro ao iniciar Chrome. Tentando com 'verificar_chrome_driver()'. Erro: {e}")
            try:
                # Substitua pela sua função real se necessário
                chrome_driver_path = verificar_chrome_driver() 
                self.nav = webdriver.Chrome(chrome_driver_path)
                
                # Simplesmente relançando o erro por enquanto, 
                # já que a função não foi definida
                raise e
            except Exception as e_inner:
                logging.error(f"Falha total ao iniciar o WebDriver: {e_inner}")
                return

        # Armazena o objeto de espera (Wait) para reuso
        self.wait = WebDriverWait(self.nav, wait_time)
        self.wait_load = WebDriverWait(self.nav, 3)
        
        # Lógica de login (original de acessar_innovaro_login)
        self.nav.maximize_window()
        self.nav.get(url)
        time.sleep(1)

        try:
            self.nav.find_element(By.ID, 'username').send_keys(usuario)
            time.sleep(1) # Reduzi o tempo, pode ajustar se necessário
            self.nav.find_element(By.ID, 'password').send_keys(senha)
            time.sleep(1)
            self.nav.find_element(By.ID, 'submit-login').click()
            print("Login realizado com sucesso.")
            self.carregamento()
        except Exception as e:
            print(f"Erro durante o login: {e}")
            logging.error(f"Erro durante o login: {e}")

    # --- Métodos de Navegação (Iframes) ---

    def iframes(self):
        """
        Itera sobre os iframes da classe 'tab-frame' e 
        tenta entrar no último disponível.
        """
        try:
            iframe_list = self.nav.find_elements(By.CLASS_NAME, 'tab-frame')
            
            for iframe_index in range(len(iframe_list)):
                time.sleep(1)
                try:
                    self.saida_iframe() # Garante que estamos no contexto padrão
                    self.nav.switch_to.frame(iframe_list[iframe_index])
                    print(f"Trocado para o iframe {iframe_index}")
                except Exception as e_inner:
                    print(f"Não foi possível trocar para o iframe {iframe_index}: {e_inner}")
                    pass
        except Exception as e:
            print(f"Erro ao buscar lista de iframes: {e}")

    def saida_iframe(self):
        """
        Retorna o foco do driver para o conteúdo principal (fora de qualquer iframe).
        """
        try:
            self.nav.switch_to.default_content()
        except Exception as e:
            print(f"Erro ao sair do iframe: {e}")
    
    
    def carregamento(self):
        cont_load = 0
        self.saida_iframe()

        print('procurando carregamento 1')
        try:
            # Espera inicial para verificar se a mensagem de carregamento existe
            carregamento = self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="statusMessageBox"]')))
            
            # Enquanto o elemento existir, continue verificando
            while True:
                print("Carregando...")
                try:
                    # Aguarde novamente pela presença do elemento
                    carregamento = self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="statusMessageBox"]')))
                
                except TimeoutException:
                    cont_load+=1
                    break
        except TimeoutException:
            # Não há mensagem de carregamento inicial
            pass    

        print('procurando carregamento 2')
        try:
            # Espera inicial para verificar se a mensagem de carregamento existe
            carregamento =  self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="waitMessageBox"]')))
            
            
            # Enquanto o elemento existir, continue verificando
            while True:
                print("Carregando...")
                try:
                    # Aguarde novamente pela presença do elemento
                    carregamento =  self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="waitMessageBox"]')))
                except TimeoutException:
                    # Se o elemento não for encontrado, interrompa o loop
                    cont_load+=1
                    break
        except TimeoutException:
            # Não há mensagem de carregamento inicial
            pass  

        print('procurando carregamento 3')
        try:
            # Espera inicial para verificar se a mensagem de carregamento existe
            carregamento =  self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="progressMessageBox"]')))
            
            # Enquanto o elemento existir, continue verificando
            while True:
                print("Carregando...")
                try:
                    # Aguarde novamente pela presença do elemento
                    carregamento =  self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="progressMessageBox"]')))
                except TimeoutException:
                    # Se o elemento não for encontrado, interrompa o loop
                    cont_load+=1
                    break
        except TimeoutException:
            # Não há mensagem de carregamento inicial
            pass    

        print('procurando carregamento 4')
        try:
            # Espera inicial para verificar se a mensagem de carregamento existe
            carregamento = self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_waitMessageBox"]')))
            cont_load+=1
            
            # Enquanto o elemento existir, continue verificando
            while True:
                print("Carregando...")
                try:
                    # Aguarde novamente pela presença do elemento
                    carregamento = self.wait_load.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content_waitMessageBox"]')))
                except TimeoutException:
                    # Se o elemento não for encontrado, interrompa o loop
                    cont_load+=1
                    break
        except TimeoutException:
            # Não há mensagem de carregamento inicial
            self.iframes()
            pass 

        self.iframes()
        print("quantidade de carregamentos: ",cont_load)
        return cont_load


    # --- Métodos de Interação com Menu ---

    def listar(self, classe):
        """
        Lista elementos de uma classe, filtra vazios e retorna:
        1. A lista de web elements originais.
        2. Um DataFrame do Pandas com os textos.
        """
        lista_menu = self.nav.find_elements(By.CLASS_NAME, classe)
        elementos_menu = []

        for elemento in lista_menu:
            elementos_menu.append(elemento.text)

        test_lista = pd.DataFrame(elementos_menu, columns=['texto'])
        test_lista = test_lista.loc[test_lista['texto'] != ""].reset_index()

        return lista_menu, test_lista

    def listar_menu_click(self, item_menu):
        """
        Busca por um texto específico no menu e clica nele.
        Usa a classe 'webguiTreeNodeLabel' como padrão.
        """
        print(f"Buscando e clicando no item de menu: '{item_menu}'")
        try:
            lista_menu, test_list = self.listar('webguiTreeNodeLabel')
            time.sleep(1)
            
            # Encontra o índice do item no DataFrame
            item_encontrado = test_list.loc[test_list['texto'] == item_menu]
            
            if item_encontrado.empty:
                print(f"Erro: Item de menu '{item_menu}' não encontrado.")
                return

            click_index = item_encontrado.iloc[0]['index']
            
            # Clica no web element correspondente
            lista_menu[click_index].click()
            time.sleep(2)
            print(f"Clicado com sucesso.")
        except Exception as e:
            print(f"Erro ao clicar no menu '{item_menu}': {e}")
            logging.error(f"Erro ao clicar no menu '{item_menu}': {e}")


    def menu_innovaro(self):
        """
        Clica no botão principal de Menu do sistema.
        """
        try:
            # Tenta sair de qualquer iframe primeiro
            self.saida_iframe()
            
            time.sleep(2)
            # Usa o 'self.wait' definido no __init__
            xpath_menu = '//*[@id="bt_1892603865"]'
            self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_menu))).click()
            
            logging.info("Clicou no menu")
            print("Menu principal clicado.")
        except Exception as e:
            print(f"Ocorreu um erro durante o click no botão de menu: {e}")
            logging.error(f"Ocorreu um erro durante o click no botão de menu: {e}")

    def fechar_navegador(self):
        """
        Encerra a sessão do WebDriver.
        """
        if self.nav:
            print("Fechando o navegador...")
            self.nav.quit()
            self.nav = None

    def botao_e(self):
        try:
            self.saida_iframe()
            time.sleep(1.5)
            xpath = '/html/body/div[2]/table/tbody/tr/td[9]/div/input'
            self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            time.sleep(1.5)
            self.nav.find_element(By.XPATH, xpath).send_keys(Keys.CONTROL,Keys.SHIFT + 'e')
            time.sleep(3)
        except Exception as e:
            print(f"Ocorreu um erro durante o preenchimento da data inicial e final: {e}")
            logging.error(f"Ocorreu um erro durante o preenchimento da data inicial e final: {e}")