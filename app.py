import time
import logging
from dotenv import load_dotenv
import os
from classes.innovaro import Innovaro
from classes.download_xmls import Download_XML
from classes.drive_xml import Drive

load_dotenv()

if __name__ == "__main__":
    
    # Configura o logging
    logging.basicConfig(level=logging.INFO)

    # 1. Cria uma instância da classe
    # O __init__ será chamado, o navegador abrirá e o login será feito.
    try:
        bot = Innovaro(usuario=os.environ.get('USUARIO'), senha=os.environ.get('SENHA'))

        # 2. Usa os métodos da classe
        
        # Clica no menu principal
        bot.menu_innovaro()
        time.sleep(2)

        # Clica em um item de menu (exemplo)
        bot.listar_menu_click("Fiscal e Regulamentação")
        time.sleep(2)
        
        # Clica em um sub-item (exemplo)
        bot.listar_menu_click("Consultas")
        time.sleep(2)

        bot.listar_menu_click("Auxiliares Fiscais")
        time.sleep(2)

        bot.listar_menu_click("Manifestação (C)")
        time.sleep(2)

        bot.listar_menu_click("99003 Download de XML Manifestados (C)")
        time.sleep(2)

        # ... aqui você faria suas ações dentro do iframe ...
        print("Executando ações dentro do iframe...")
        bot.carregamento()

        download_xmls = Download_XML(bot.nav)

        download_xmls.preencher_variaveis_manifesto()

        time.sleep(1)

        bot.botao_e()

        bot.carregamento()

        time.sleep(1)
        
        pasta_local_dos_xmls = download_xmls.download_xml_manifestados()
        bot.carregamento()
        
        # --- 2. NOVA ETAPA: UPLOAD PARA O DRIVE ---
        if pasta_local_dos_xmls:
            print("\n--- Iniciando integração com Google Drive ---")
            drive_uploader = Drive()
            drive_uploader.upload_files(local_folder_path=pasta_local_dos_xmls)
            print("--- Integração com Google Drive finalizada ---")
        else:
            print("Nenhuma pasta local de XMLs foi processada. Pulando upload para o Drive.")
        
    except Exception as e:
        print(f"Um erro principal ocorreu na automação: {e}")
    
    finally:
        # 3. Fecha o navegador
        # É importante fazer isso no 'finally' para garantir
        # que o navegador feche mesmo se ocorrer um erro.
        if 'bot' in locals() and bot.nav:
            bot.fechar_navegador()