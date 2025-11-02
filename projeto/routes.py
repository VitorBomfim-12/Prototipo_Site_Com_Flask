from flask import Flask,render_template,url_for,redirect,flash,session
from projeto import app,database,bcrypt,session
import socket,dotenv,os
from datetime import timedelta,datetime, timezone
from flask_login import login_required, login_user,logout_user,current_user
from projeto.forms import FormCriarConta, FormLogin, FormContato, Form_Verifica
from projeto.models import Clientes, Chamado, Equipamento,CodigosMFA
from sqlalchemy.exc import IntegrityError
from projeto.functions import data_,email_verifica,gera_n,hora_,suporte_email
from dotenv import load_dotenv
    
dotenv.load_dotenv()

@app.route("/", methods = ["GET","POST"])
def homepage():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
        try:
            usuario = Clientes.query.filter_by(email=formlogin.email.data).first()
            if usuario and  bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
                session["user_attempt"] = usuario.id 
                cod=gera_n(6)
                hash_cod = bcrypt.generate_password_hash(cod).decode('utf-8')
                mfa_gerado = CodigosMFA(cod_hash = hash_cod,
                                        user_id=usuario.id)
                
                database.session.add(mfa_gerado)
                database.session.commit()
                email_verifica(cod,formlogin.email.data)
                
                return redirect (url_for ("verificacao"))
            
            elif not usuario:
                flash("Este email não está cadastrado, crie uma conta!")

            elif not bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
                flash("Senha incorreta!")
        except socket.gaierror:
            flash(f"Parece que você esta sem internet!\n Erro: socketgaierror")
                
           
    return render_template ("homepage.html", form=formlogin)


@app.route("/verifica", methods =["GET","POST"])
def verificacao():

    formverifica=Form_Verifica()

    user = session.get('user_attempt')
    tentativa_acess = CodigosMFA.query.filter_by(user_id=user)

    hora_envio_cod = tentativa_acess.hora_cod
    hora_atual=datetime.now()
    diferença = hora_atual - hora_envio_cod
    limite = timedelta(minutes=5)
    
    if formverifica.validate_on_submit():
   
     if bcrypt.check_password_hash(tentativa_acess.cod_hash , formverifica.codigo_verificacao.data):
        login_user(user)
        session.pop('user_attempt')
        return redirect (url_for("suporte"))
     
     elif diferença > limite: 
        session.clear()
        flash("Código expirado")
        return redirect(url_for("homepage"))
     elif formverifica.codigo_verificacao.data!=tentativa_acess.cod_hash:
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
         senha = bcrypt.generate_password_hash(formcriarconta.senha.data).decode('utf-8')
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

    

   