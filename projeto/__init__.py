from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


app=Flask(__name__)

app.secret_key ="teste__#sahlinse&#$@crdone"
#criação do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chamados.db" 

#criação de chave secreta
app.config ["SECRET_KEY"] ="f3aa3335a2882e2a21e567f9dc4dd300"



database = SQLAlchemy(app)

#inicialização do bcrypt e do login manager no app(site)

bcrypt = Bcrypt(app)

login_manager =LoginManager(app)

login_manager.login_view="homepage"

from projeto import routes