import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

OCULTAR_TELA = False
EMAIL = os.getenv("EMAIL")
SENHA = os.getenv("SENHA")
URL_LOGIN = "https://awsrestart.instructure.com/login/canvas"
URL_ATIVIDADES = "https://awsrestart.instructure.com/courses/4327/grades"
BASE_URL = "https://awsrestart.instructure.com"
