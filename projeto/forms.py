from flask_wtf import FlaskForm #biblioteca que permite a criação de formulários de login
from wtforms import StringField, PasswordField,SubmitField,RadioField #importação dos campos dos formulários
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError #importação de funções que validam as informações inseridas 
#pelo usuário
from projeto.models import Clientes

#criação de formulários
class FormLogin(FlaskForm):
    email = StringField("E-mail",validators=[DataRequired(),Email()])
    senha= PasswordField("Senha", validators=[DataRequired()])
    botao_confirmacao= SubmitField("Fazer login")
#validação dos dados inseridos pelo usuário

class FormCriarConta(FlaskForm): 
    username=StringField("Nome",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired(), Email()])
    senha=PasswordField("Senha",validators=[DataRequired(),Length(min=8,max=20)])
    confirmacao_senha=PasswordField("Confirmação de senha", validators=[DataRequired(),EqualTo("senha"), Length(min=8,max=20)])
    CPF=StringField("CPF", validators=[DataRequired(),Length(min=11,max=11)])
    telefone=StringField("Telefone",validators=[DataRequired(),Length(min=8,max=13)])
    botao_confirmacao=SubmitField("Criar conta")
 
 #investigar repetição de email

    def validadate_telefone(self,telefone):
        usuario = Clientes.query.filter_by(telefone=telefone.data).first()
        if usuario: raise ValidationError("Telefone cadastrado!")
 
    def validate_email(self,email):
        usuario= Clientes.query.filter_by(email=email.data).first()
        if usuario: raise ValidationError("Email já cadastrado, faça login")
    
    def validate_cpf(self,CPF):
        usuario=Clientes.query.filter_by(CPF=CPF.data).first()
        if usuario: raise ValidationError("CPF já cadastrado, faça login")
    #função que define se um usuário ja existe, usando CPF,telefone ou email como parâmetro

class FormContato(FlaskForm):
    descricao=StringField("Descrição do chamado",validators=[DataRequired()])
    serial_number=StringField("Serial Number do produto:",validators=[DataRequired()])
    
    equipamento = RadioField('Escolha o equipamento:',
               choices=[('1',"Trator"),('2','Colheitadeira'),
              ('3','Arados'),('3','Semeadeiras'),
              ('4','Fertilizadores'),
              ('5','Geradores'),
              ('6','Pulverizadores'),
              ('7','Empilhadeiras')
              ('8','Retroescavadeira'),
              ('9','Equipamentos eletrônicos'),
              ('10','Forrageiras'),], validators=[DataRequired()])

    botao_confirmacao=SubmitField("Enviar chamado")
    
class Form_Verifica(FlaskForm):
    codigo_verificacao= StringField("Código",validators=[DataRequired(),Length(max=6)])
    botao_confirmacao = SubmitField("Login")

