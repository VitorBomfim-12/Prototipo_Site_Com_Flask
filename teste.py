from projeto import database,app
from projeto.models import Equipamento,Chamado

with app.app_context():
    equipamentos_tupla = database.session.query(Chamado.equipamento_id).all()

lista_defeitos = [equipamento_id for (equipamento_id,) in equipamentos_tupla]

print(lista_defeitos)