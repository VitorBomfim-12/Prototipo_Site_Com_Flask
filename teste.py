from datetime import date, datetime
data = date.today()
data="{}/{}/{}".format(data.day,data.month,data.year)
hora_atual = datetime.now().time()
hora_atual=str(hora_atual)
print(hora_atual)
print((type(hora_atual)))