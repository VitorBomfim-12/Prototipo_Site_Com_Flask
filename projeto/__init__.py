from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import os,dotenv
from dotenv import load_dotenv
app = Flask(__name__)
    
dotenv.load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')
#criação do banco de dados



#configuração das sessões
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_USE_SIGNER"] = True 
 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('DEL_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

#criação de chave secreta
app.config ["SECRET_KEY"] ="f3aa3335a2882e2a21e567f9dc4dd300"



#inicialização do bcrypt e do login manager no app(site)

bcrypt = Bcrypt(app)

Session(app)

login_manager =LoginManager(app)

mail = Mail(app)

login_manager.login_view="homepage"

from projeto import routes