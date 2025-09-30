from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.secret_key ="teste__#sahlinse&#$@crdone"
#criação do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chamados.db" 

#configuração das sessões
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_USE_SIGNER"] = True  
#criação de chave secreta
app.config ["SECRET_KEY"] ="f3aa3335a2882e2a21e567f9dc4dd300"

database = SQLAlchemy(app)

#inicialização do bcrypt e do login manager no app(site)

bcrypt = Bcrypt(app)

Session(app)

login_manager =LoginManager(app)

login_manager.login_view="homepage"

from projeto import routes