from datetime import date, datetime
data = date.today()
data="{}/{}/{}".format(data.day,data.month,data.year)
hora_atual = datetime.now().time()

print(hora_atual)
print(type(data))
