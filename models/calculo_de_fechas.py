from datetime import date,timedelta,time,datetime


formato_fecha="%Y-%m-%d"
fecha_nacimiento=datetime.strptime("1986-11-9",formato_fecha)
fecha_actual=datetime.strptime("2018-8-13",formato_fecha)
fecha_hector=datetime .strptime("1986-11-21",formato_fecha)

print((fecha_actual-fecha_hector))

