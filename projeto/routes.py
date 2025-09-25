from flask import Flask,render_template,url_for, request, redirect,flash
from flask_mail import Mail,Message
from projeto import app,database,bcrypt
import os
import dotenv
import random
from datetime import date,datetime
from projeto.models import Chamado
from flask_login import login_required, login_user,logout_user,current_user
from projeto.forms import FormCriarConta, FormLogin, FormContato
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



@app.route("/", methods = ["GET","POST"])
def homepage():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
        usuario = Clientes.query.filter_by(email=formlogin.email.data).first()
        if usuario and  bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
           login_user(usuario)
           return redirect(url_for("suporte")) 
           
    return render_template ("homepage.html", form=formlogin)


@app.route("/criarconta", methods =["GET","POST"])
def criarconta():
    formcriarconta = FormCriarConta()
    if formcriarconta.validate_on_submit():
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
         n_chamado=""
         for i in range (10):
          n_chamado+=str(random.randint(0,9))
         data = date.today()
         data="{}/{}/{}".format(data.day,data.month,data.year)
         data=str(data)
         hora_atual = datetime.now().time()
         hora_atual=str(hora_atual)

         chamado = Chamado(
          numerochamado=n_chamado,
          data=data,
          hora = hora_atual,
          descricao= form_chamado.descricao.data,
          serialnumber= form_chamado.serial_number.data,
          cliente_id=current_user.id
           )
         database.session.add(chamado)
         database.session.commit()
        
         msg = Message(subject=f"Chamado de suporte:{n_chamado}",sender = os.getenv('DEL_EMAIL'), recipients= [os.getenv('REC_MAIL')])
         msg.body = f''' O(a) cliente {current_user.clientname} requisitou um atendimento:\n\n Serial Number: {form_chamado.serial_number.data}  \n\n Descrição do chamado:\n {form_chamado.descricao.data} 
         \n\n Email de retorno: {current_user.email} \n Telefone de contato: {current_user.telefone} \n Data do chamado: {data}, Hora do chamado: {hora_atual}'''
         mail.send(msg)
         return redirect(url_for("suporte"))
    return render_template("suporte.html", form = form_chamado)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))


  