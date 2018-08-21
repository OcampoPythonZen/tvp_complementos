import datetime

class trato_de_fechas():

    def __init__(self,formato,fecha_inicial,fecha_final):
        self.formato='%Y-%m-%d'
        self.fecha_inicial=datetime.datetime.strptime(fecha_inicial,formato)
        self.fecha_final=datetime.datetime.strptime(fecha_final,formato)

    def __str__(self):
        return 'El formato de la fecha es: ' + self.formato \
                 + ', el año de la fecha inicial es: ' + str(self.fecha_inicial.year) \
                 + ', el año de la fecha final es: ' + str(self.fecha_final.year)

    def __sub__(self):
        return 'Tu edad es de: ' + str(self.fecha_final.year-self.fecha_inicial.year) + ' años'


obj=trato_de_fechas('%Y-%m-%d','1988-11-9','2018-8-15')
print(obj)
print(obj.__sub__())






