
from projeto import database,app
from projeto.models import Equipamento

lista_equipamentos= ('trator',
              'colheitadeira',
              'arado','semeadeiras',
              'fertilizadores',
              'geradores',
              'pulverizadores',
              'empilhadeiras',
              'retroescavadeira',
              'equipamentos_eletronicos',
              'forrageiras')

with app.app_context():
    for equip in lista_equipamentos:
       equip_ad = Equipamento(tipo = equip)
       database.session.add(equip_ad)
       
    database.session.commit()


