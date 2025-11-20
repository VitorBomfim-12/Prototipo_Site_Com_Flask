from flask import Flask,session
from flask_session import Session
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




bcrypt = Bcrypt(app)
Session(app)
mail = Mail(app)

from projeto import routes