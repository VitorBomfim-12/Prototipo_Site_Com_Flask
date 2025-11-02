
from projeto import database,app
from projeto.models import Chamado,Clientes,Equipamento

with app.app_context():
    # Apaga todas as tabelas existentes no banco de dados
    print("Apagando o banco de dados...")
    database.drop_all()
    print("Banco de dados apagado com sucesso.")

    # Cria todas as tabelas novamente, com base nos modelos definidos em models.py
    print("Criando o novo banco de dados...")
    database.create_all()
    print("Banco de dados e tabelas criados com sucesso!")

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
