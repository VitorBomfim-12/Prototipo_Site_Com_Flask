from flask import Flask,render_template,url_for,redirect,flash,session
from flask_mail import Mail,Message
from projeto import app,database,bcrypt,Session
import os
import dotenv
import random
from datetime import date,datetime,timedelta
from flask_login import login_required, login_user,logout_user,current_user
from projeto.forms import FormCriarConta, FormLogin, FormContato, Form_Verifica
from projeto.models import Clientes, Chamado
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

    
dotenv.load_dotenv()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('DEL_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)



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
  
@app.route("/", methods = ["GET","POST"])
def homepage():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
        usuario = Clientes.query.filter_by(email=formlogin.email.data).first()
        if usuario and  bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
            cod=gera_n(6)
            email_verifica(cod,formlogin.email.data)
            session["codigo"] = cod
            session["user"] = usuario
            session["hora_lancamento"] = datetime.now()
            return redirect (url_for ("verificacao"))
        else:
            flash("Email ou senha incorretos!")
            
           
    return render_template ("homepage.html", form=formlogin)


@app.route("/verifica", methods =["GET","POST"])
def verificacao():

    formverifica=Form_Verifica()
    codigo = session.get("codigo")
    hora_do_envio=session.get("hora_lancamento")

    hora_atual=datetime.now()
    diferença = hora_atual-hora_do_envio
    limite = timedelta(minutes=5)
    
    if formverifica.validate_on_submit():
     
     if formverifica.codigo_verificacao.data==codigo and diferença < limite:
        user = session.get("user")
        login_user(user)
        return redirect (url_for("suporte"))
     elif diferença > limite: 
        session.clear()
        flash("Código expirado")
        return redirect(url_for("homepage"))
     elif formverifica.codigo_verificacao.data!=codigo:
        session.clear()
        flash("Código incorreto!")
        return redirect(url_for("homepage"))
          
     

    return render_template("verifica.html", form = formverifica)
   
      
@app.route("/criarconta", methods =["GET","POST"])
def criarconta():
    
    formcriarconta = FormCriarConta()
    if formcriarconta.validate_on_submit():
        if formcriarconta.confirmacao_senha.data != formcriarconta.senha.data:
             flash("As senhas devem ser iguais!")
             return redirect(url_for("criarconta"))
        try:
         senha = bcrypt.generate_password_hash(formcriarconta.senha.data)
         cliente=Clientes(clientname = formcriarconta.username.data,
                         email = formcriarconta.email.data,
                         senha = senha,
                         CPF = formcriarconta.CPF.data,
                         telefone = formcriarconta.telefone.data)
         

         database.session.add(cliente)
         database.session.commit()
         login_user(cliente,remember=True)
         return redirect(url_for("suporte"))
        
        except IntegrityError:
            database.session.rollback()
            flash("Email, CPF, ou telefone já cadastrado! faça login ")
            return redirect(url_for("homepage"))
        
    return render_template("criarconta.html", form = formcriarconta)

@app.route("/suporte", methods=["GET","POST"])
@login_required
def suporte():
    form_chamado = FormContato()
    if form_chamado.validate_on_submit():
         
         n_chamado = gera_n(10)
         data=str(data_())
         hora_atual=str(hora_())

         chamado = Chamado(
          numerochamado=n_chamado,
          data=data,
          hora = hora_atual,
          descricao= form_chamado.descricao.data,
          serialnumber= form_chamado.serial_number.data,
          equipamento_id= form_chamado.equipamento.data
          ,cliente_id=current_user.id )
         
         database.session.add(chamado)
         database.session.commit()
   
         suporte_email(n_chamado,current_user.clientname,
                       form_chamado.serial_number.data,
                       form_chamado.descricao.data,data,
                       hora_atual,current_user.email,
                       current_user.telefone
                       )
         return redirect(url_for("suporte"))
    return render_template("suporte.html", form = form_chamado)

@app.route("/suporte/chamados")
@login_required
def chamados():
    lista_chamados = Chamado.query.filter_by(cliente_id=current_user.id).all()
    print(lista_chamados)
    return render_template("chamados.html",lista_chamados=lista_chamados)

@app.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("homepage"))

    

   