
from projeto import database,app
from projeto.models import Chamado,Clientes

with app.app_context():
  database.create_all()