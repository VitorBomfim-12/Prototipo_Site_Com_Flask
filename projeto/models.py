from projeto import database, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
    return Clientes.query.get(int(id_usuario))

#usermixin permite que uma classe gerecie os perfis

class Clientes(database.Model,UserMixin):
    
    id = database.Column (database.Integer,primary_key=True,nullable=False,unique=True)
    CPF= database.Column(database.String,unique=True, nullable=False)
    email= database.Column(database.String,unique=True,nullable=False)
    senha =  database.Column(database.String,nullable=False)
    clientname= database.Column(database.String, nullable=False)
    telefone= database.Column(database.String,unique=True,nullable=False) 
    chamados= database.relationship("Chamado", backref="cliente", lazy=True) 
    
class Chamado(database.Model):
    
    id = database.Column(database.Integer, primary_key=True)
    numerochamado= database.Column(database.Integer, nullable=False, unique=True)
    data= database.Column(database.String,nullable=False, )
    hora= database.Column(database.String,nullable=False, )
    descricao= database.Column(database.String, nullable=False)
    serialnumber= database.Column(database.String, nullable=False)
    cliente_id = database.Column(database.Integer, database.ForeignKey('clientes.id'),nullable=False)
  
