from flask import Flask,render_template,url_for,redirect,flash,session
from projeto import app,bcrypt,session
import socket,dotenv
from datetime import timedelta,datetime
from flask_login import login_required, login_user,logout_user,current_user
from projeto.forms import FormCriarConta, FormLogin, FormContato, Form_Verifica
from projeto.models import Clientes, Chamado, Equipamento,CodigosMFA
from sqlalchemy.exc import IntegrityError
from projeto.functions import data_,email_verifica,gera_n,hora_,suporte_email,get_db_connection,create_cur
from dotenv import load_dotenv
import pymysql, pymysql.cursors
    
dotenv.load_dotenv()

@app.route("/", methods = ["GET","POST"])
def homepage():
    formlogin = FormLogin()
    if formlogin.validate_on_submit():
            
    
            email_digitado  = formlogin.email.data
            con = get_db_connection()
            if con:
                try:
                    cur = con.cursor(pymysql.cursors.DictCursor)
                    cur.execute ('select * from users where email = %s limit 1'(email_digitado))
                    usuario = cur.fetchone()
            
                    if usuario and  bcrypt.check_password_hash(usuario['password_user'], formlogin.senha.data):
                        session["user_attempt"] = usuario['id']
                        cod=gera_n(6)
                        hash_cod = bcrypt.generate_password_hash(cod).decode('utf-8')
                        cur.execute(""" insert into codigosmfa (cod_hash,user_id)""",(cod,usuario['id']))
                    
                        email_verifica(cod,formlogin.email.data)
                        
                    
                        return redirect (url_for ("verificacao"))
                    
                    elif not usuario:
                        flash("Este email não está cadastrado, crie uma conta!")
                        
                    
                    elif not bcrypt.check_password_hash(usuario.senha, formlogin.senha.data):
                        flash("Senha incorreta!")
                        
                finally:
                    cur.close()
                    con.close()
            else: flash("Erro ao conectar ao banco")
            
    return render_template ("homepage.html", form=formlogin)

      
@app.route("/criarconta", methods =["GET","POST"])
def criarconta():
    
    formcriarconta = FormCriarConta()
    if formcriarconta.validate_on_submit():
        

        email_digitado=formcriarconta.email.data
        con = get_db_connection()
        
        if con:
            try:   
                cur = con.cursor(pymysql.cursors.DictCursor)
                cur.execute ("SELECT * FROM users where email = %s",email_digitado)
                usuario = cur.fetchone()

                if formcriarconta.confirmacao_senha.data != formcriarconta.senha.data:
                    flash("As senhas devem ser iguais!")
                    return redirect(url_for("criarconta"))
                if not usuario:
                    senha = bcrypt.generate_password_hash(formcriarconta.senha.data).decode('utf-8')
                    
                    cur.execute("INSERT INTO users (username,password_user,cpf,email,phone_number) VALUES (%s,%s,%s,%s,%s)",
                                formcriarconta.username.data,
                                senha,
                                formcriarconta.email.data,
                                formcriarconta.CPF.data,
                                formcriarconta.telefone.data)
                    con.commit()
                    flash("faça login!")
                    return redirect(url_for("homepage"))
                
                else:
                    con.rollback()
                    flash("Email, CPF, ou telefone já cadastrado! faça login ")
                    return redirect(url_for("homepage"))
            finally:
                con.close()
                cur.close()
        else: flash("Erro ao conectar ao banco")
        
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
                       current_user.telefone)
         return redirect(url_for("suporte"))
    return render_template("suporte.html", form = form_chamado)

@app.route("/suporte/chamados")
@login_required
def chamados():
    lista_chamados = Chamado.query.filter_by(cliente_id=current_user.id).all()
    return render_template("chamados.html",lista_chamados=lista_chamados)

@app.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("homepage"))

    

   