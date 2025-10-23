# Em: classes/drive.py

import os.path
from dotenv import load_dotenv
import os
from pathlib import Path
from google.oauth2 import service_account # <-- MUDANÇA IMPORTANTE
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

load_dotenv()

# O Escopo continua o mesmo
SCOPES = ['https://www.googleapis.com/auth/drive']

class Drive:
    def __init__(self):
        """
        Construtor da classe.
        Autentica no Google Drive usando um Service Account (via .env).
        Verifica o acesso à pasta de destino usando o ID do .env.
        """
        print("Iniciando serviço do Google Drive (via Service Account)...")
        self.service = self._get_drive_service()
        
        if not self.service:
            print("ERRO: Falha ao autenticar com o Service Account.")
            self.target_folder_id = None
            return

        # --- LÓGICA ATUALIZADA ---
        # 1. Pega o ID diretamente do .env
        self.target_folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
        
        if not self.target_folder_id:
            print("ERRO: Variável 'GOOGLE_DRIVE_FOLDER_ID' não encontrada no arquivo .env.")
            print("Por favor, adicione o ID da pasta do Drive ao .env.")
            return

        # 2. Verifica se o ID é válido e se temos permissão
        if not self._verify_folder_access(self.target_folder_id):
            print(f"ERRO: Não foi possível acessar a pasta com ID: {self.target_folder_id}")
            print("Verifique se o ID está correto e se a pasta foi compartilhada com o e-mail do Service Account.")
            self.target_folder_id = None # Invalida o ID para o resto da execução
        else:
            print(f"Acesso à pasta do Drive (ID: {self.target_folder_id}) verificado com sucesso.")


    def _get_drive_service(self):
        """
        (Este método permanece o mesmo - Autentica via .env)
        """
        try:
            creds_info = {
                "type": os.environ.get("GOOGLE_TYPE"),
                "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
                "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
                "private_key": os.environ.get("GOOGLE_PRIVATE_KEY", "").replace('\\n', '\n'),
                "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "auth_uri": os.environ.get("GOOGLE_AUTH_URI"),
                "token_uri": os.environ.get("GOOGLE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.environ.get("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_X509_CERT_URL"),
                "universe_domain": os.environ.get("GOOGLE_UNIVERSE_DOMAIN")
            }
            if not creds_info["client_email"] or not creds_info["private_key"]:
                print("ERRO: GOOGLE_CLIENT_EMAIL ou GOOGLE_PRIVATE_KEY não encontrados no .env")
                return None
            
            creds = service_account.Credentials.from_service_account_info(
                creds_info, 
                scopes=SCOPES
            )
            print("Autenticação com Service Account bem-sucedida.")
            return build('drive', 'v3', credentials=creds, cache_discovery=False)
        except Exception as error:
            print(f"Um erro ocorreu ao construir o serviço do Drive com Service Account: {error}")
            return None

    def _verify_folder_access(self, folder_id):
        """
        *** NOVO MÉTODO ***
        Verifica se a pasta com o ID fornecido existe e se o
        Service Account tem permissão para acessá-la.
        """
        if not self.service:
            return False
        try:
            folder = self.service.files().get(
                fileId=folder_id, 
                fields='id, name',
                supportsAllDrives=True
            ).execute()
            
            print(f"Pasta encontrada no Drive: '{folder.get('name')}'")
            return True
        except HttpError as error:
            # --- ADICIONE ESTA LINHA PARA DEBUG ---
            print(f"HttpError Detalhado: {error.content}")
            # -------------------------------------
            
            print(f"Falha ao verificar pasta do Drive (ID: {folder_id}): {error}")
            return False
        except Exception as e:
            # Pega outros erros inesperados
            print(f"Erro inesperado ao verificar pasta: {e}")
            return False

    def _get_existing_files_in_drive_folder(self):
        """
        (Este método permanece o mesmo)
        """
        existing_files = set()
        if not self.target_folder_id:
            return existing_files
        
        page_token = None
        try:
            while True:
                query = f"'{self.target_folder_id}' in parents and trashed=false"
                response = self.service.files().list(
                    q=query,
                    corpora="allDrives", 
                    includeItemsFromAllDrives=True, 
                    supportsAllDrives=True, 
                    spaces='drive',
                    fields='nextPageToken, files(name)',
                    pageToken=page_token
                ).execute()
                print(f"DEBUG: A API retornou {len(response.get('files', []))} arquivos nesta página.")
                for file in response.get('files', []):
                    existing_files.add(file.get('name'))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break
            print(f"Encontrados {len(existing_files)} arquivos .xml existentes no Google Drive.")
            return existing_files
        except HttpError as error:
            print(f'Um erro ocorreu ao listar arquivos do Drive: {error}')
            return existing_files

    def upload_files(self, local_folder_path):
        """
        Método público para fazer upload, pulando arquivos que já existem.
        """
        if not self.target_folder_id:
            print("Erro: ID da pasta de destino no Drive não foi definido ou falhou na verificação. Abortando upload.")
            return

        print(f"Verificando arquivos em '{local_folder_path}' para upload no Drive...")
        
        # 1. Busca a lista de arquivos (que pode estar atrasada/cacheada)
        drive_files = self._get_existing_files_in_drive_folder()
        
        local_path = Path(local_folder_path)
        local_xml_files = list(local_path.glob("*.xml"))

        if not local_xml_files:
            print("Nenhum arquivo .xml encontrado na pasta local para upload.")
            return

        total_local_files = len(local_xml_files)
        files_uploaded = 0
        
        for local_file in local_xml_files:
            local_file_name = local_file.name
            
            if local_file_name in drive_files:
                print(f"  -> Ignorando '{local_file_name}': Já existe (cache local ou API).")
            else:
                print(f"  -> Fazendo upload de '{local_file_name}'...")
                try:
                    file_metadata = {'name': local_file_name, 'parents': [self.target_folder_id]}
                    media = MediaFileUpload(local_file, mimetype='text/xml')
                    
                    self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id',
                        supportsAllDrives=True
                    ).execute()
                    
                    files_uploaded += 1
                    
                    drive_files.add(local_file_name)

                except HttpError as error:
                    print(f"    ERRO ao fazer upload de '{local_file_name}': {error}")
        
        # (Relatório final ... permanece o mesmo)
        print("="*30)
        print("Relatório de Upload para o Google Drive:")
        print(f"Total de arquivos .xml na pasta local: {total_local_files}")
        print(f"Arquivos novos enviados para o Drive:  {files_uploaded}")
        print(f"Arquivos ignorados (já existem): {total_local_files - files_uploaded}")
        print("="*30)
        