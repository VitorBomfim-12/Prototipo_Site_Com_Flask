from flask import Flask,render_template,url_for,redirect,flash,session
from projeto import app,bcrypt
import dotenv
from datetime import timedelta,datetime
from flask_login import login_required, login_user,logout_user,current_user
from projeto.forms import FormCriarConta, FormLogin, FormContato, Form_Verifica
from projeto.functions import data_,email_verifica,gera_n,hora_,suporte_email,get_db_connection
from dotenv import load_dotenv
import pymysql, pymysql.cursors
dotenv.load_dotenv()

@app.route("/", methods = ["GET","POST"])
def homepage():
    formlogin = FormLogin()
   
    con = get_db_connection()
    if con:
         if formlogin.validate_on_submit():
            try:
                email_digitado  = formlogin.email.data
                cur = con.cursor(pymysql.cursors.DictCursor)
                cur.execute ('select * from users where email = %s limit 1',(email_digitado))
                usuario = cur.fetchone()
        
                if usuario and  bcrypt.check_password_hash(usuario['password_user'], formlogin.senha.data):
                    session["user_attempt"] = usuario['id']
                    cod=gera_n(6)
                    hash_cod = bcrypt.generate_password_hash(cod).decode('utf-8')
                    cur.execute(""" insert into codigosmfa (cod_hash,user_id) VALUES (%s,%s)""",(hash_cod,usuario['id']))
                
                    email_verifica(cod,formlogin.email.data)
                    
                
                    return redirect (url_for ("verificacao"))
                
                elif not usuario:
                    flash("Este email não está cadastrado, crie uma conta!")
                    return redirect(url_for("homepage"))
                    
                
                elif not bcrypt.check_password_hash(usuario['password_user'], formlogin.senha.data):
                    flash("Senha incorreta!")
                    return redirect(url_for("homepage"))
                    
            finally:
                cur.close()
                con.close()
    else: flash("Erro ao conectar ao banco")
            
    return render_template ("homepage.html", form=formlogin)



@app.route("/verifica", methods =["GET","POST"])
def verificacao():
    if 'user_attempt' not in session:
        flash('Faça login para acessar esta página!')
        return redirect(url_for("homepage"))
    
    formverifica=Form_Verifica()
    user = session.get('user_attempt')
    
    con = get_db_connection()
         
    if con:
        if formverifica.validate_on_submit():
            try:    
                with con.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute("SELECT * FROM codigosmfa WHERE user_id = %s",user)
                        tentativa_acess= cur.fetchall()
                        hora_envio_cod = tentativa_acess['hora_cod']
            
               
                hora_atual=datetime.utcnow()
                diferença = hora_atual - hora_envio_cod
                limite = timedelta(minutes=10)

                if bcrypt.check_password_hash(tentativa_acess['cod_hash'] , formverifica.codigo_verificacao.data) and diferença<limite:

                    session.pop('user_attempt')
                    session['user'] = tentativa_acess['user_id']
                    with con.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute("DELETE * FROM codigosmfa WHERE user_id = %s",(user))
                        con.commit()
                    return redirect (url_for("suporte"))
                
                elif diferença > limite: 

                    session.clear()
                    flash("Código expirado")
                    with con.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute("DELETE* FROM codigosmfa WHERE user_id = %s",(user))
                        con.commit()
                    
                    return redirect(url_for("homepage"))
                
                elif formverifica.codigo_verificacao.data!=tentativa_acess.cod_hash:

                    session.clear()
                    flash("Código incorreto!")
                    with con.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute("delete * FROM codigosmfa WHERE user_id = %s",user)
                        con.commit()
                    return redirect(url_for("homepage"))
            finally:
                cur.close()
                con.close
    else:
        flash("Erro ao conectar ao banco!")
        
    return render_template("verifica.html", form = formverifica)
   
      
@app.route("/criarconta", methods =["GET","POST"])
def criarconta():
    
    formcriarconta = FormCriarConta()
    
        

    email_digitado=formcriarconta.email.data
    con = get_db_connection()
        
    if con:
        if formcriarconta.validate_on_submit():    
            try:   
                

                if formcriarconta.confirmacao_senha.data != formcriarconta.senha.data:
                    flash("As senhas devem ser iguais!")
                    return redirect(url_for("criarconta"))
                
                with con.cursor(pymysql.cursors.DictCursor) as cur:
                    cur.execute ("SELECT * FROM users where email = %s",email_digitado)
                    usuario = cur.fetchone()

                if not usuario:
                    senha = bcrypt.generate_password_hash(formcriarconta.senha.data).decode('utf-8')
                    with con.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute("INSERT INTO users (username,password_user,cpf,email,phone_number) VALUES (%s,%s,%s,%s,%s)",
                                    (formcriarconta.username.data,
                                    senha,
                                    formcriarconta.CPF.data,
                                    formcriarconta.email.data,
                                    formcriarconta.telefone.data))
                        con.commit()
                    flash("faça login!")
                    return redirect(url_for("homepage"))
                
                else:
                    flash("Email, CPF, ou telefone já cadastrado! faça login ")
                    return redirect(url_for("homepage"))
            finally:
                con.close()
                
    else: flash("Erro ao conectar ao banco")
        
    return render_template("criarconta.html", form = formcriarconta)

@app.route("/suporte", methods=["GET","POST"])
def suporte():
    if 'user' not in session:
        return redirect(url_for("homepage"))
    
    form_chamado = FormContato()
    con = get_db_connection()
   
    if con:    
        if form_chamado.validate_on_submit():
            try:  
                
            
                    with con.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute("SELECT * FROM users WHERE id = %s",(session['user']))
                        current_user = cur.fetchone()

                    n_chamado = gera_n(10)
                    data=str(data_())
                    hora_atual=str(hora_())

                    with con.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute("INSERT INTO chamados (descricao,serial_number,cliente_id,equipamento_id) VALUES (%s,%s,%s,%s)",(form_chamado.descricao.data,
                        form_chamado.serial_number.data,current_user["id"], form_chamado.equipamento.data,))
                        con.commit()

                    suporte_email(n_chamado,current_user["username"],
                                form_chamado.serial_number.data,
                                form_chamado.descricao.data,data,
                                hora_atual,current_user['email'],
                                current_user['phone_number'])
                    return redirect(url_for("suporte"))
            finally:
                con.close()
                cur.close()
    else:
        flash("Erro ao conectar ao banco!")
                
    return render_template("suporte.html", form = form_chamado)

@app.route("/suporte/chamados")
def chamados():
    lista_chamados = Chamado.query.filter_by(cliente_id=current_user.id).all()
    return render_template("chamados.html",lista_chamados=lista_chamados)

@app.route("/logout")
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("homepage"))

    

   