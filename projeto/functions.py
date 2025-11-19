from projeto import mail
from flask_mail import Message
from projeto.models import Chamado
from datetime import date,datetime
import random,os,dotenv
import pymysql

dotenv.load_dotenv()
def gera_n(lim):
     while True:
         n_chamado=""
         for i in range (lim):
             n_chamado+=str(random.randint(0,9))

         teste_chamado_exis= Chamado.query.filter_by(numerochamado=n_chamado).first()
         if not teste_chamado_exis:
             return str(n_chamado)
         
def email_verifica(n_cham,email):
    
    msg_ve = Message(subject=f" Código de verificação ", sender = os.getenv('DEL_EMAIL'), recipients=[email])
    msg_ve.body = f''' Seu código de verificação é {str(n_cham)}\n\n @Jhon Deere, todos os direitos reservados'''
    mail.send(msg_ve)
   

def suporte_email(n_cham,nome,serial,descricao,data,hora,email, telefone):
    msg = Message(subject=f"Chamado de suporte Nº{n_cham}", sender = os.getenv('DEL_EMAIL'), recipients=[os.getenv('REC_EMAIL')])
    msg.body = f''' O(a) cliente {nome} requisitou um antendimento \n Serial number: {serial}
    \n Descrição: {descricao}\n Data e hora {data} , {hora} \n\n Email de retorno: {email} \n Telefone :{telefone}'''
    mail.send(msg)

def data_():
    data = date.today()
    data="{}/{}/{}".format(data.day,data.month,data.year)
    return data
        
def hora_():
     hora_atual = datetime.now().time()
     hora_atual=hora_atual.strftime("%H:%M")
     return hora_atual
  

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=os.getenv("DB_password"),
        database='helpdesk',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def create_cur():
       con = get_db_connection()
       cur = con.cursor(pymysql.cursors.DictCursor)
       return cur
