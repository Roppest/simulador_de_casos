import random
import os
try :
	from bs4 import BeautifulSoup as soup
except ImportError:
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'beautifulsoup4'])
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'lxml'])
finally:
	from bs4 import BeautifulSoup as soup
	import bs4

try :
	import pandas as pd
except ImportError:
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
finally:
	import pandas as pd
import numpy as np
import geopy.distance as distance

'''
Este simulador crea vectores de datos que representan características de personas,
y sismos para poder calcular su IR (Indice de Riesgo).

Sismo o V1 = {Mag, Slat, Slong}
Persona o V2 = {dfis, dsen, U, Plat, Plong}
'''
def calcular_p(mag):
    if mag < 4.0:
        return 1
    elif 4.0 <= mag and mag < 5.0:
        return 2
    elif 5.0 <= mag and mag < 6.0:
        return 4
    elif 6.0 <= mag and mag < 6.5:
        return 5
    elif 6.5 <= mag and mag < 7.0:
        return 6
    elif 7.0 <= mag and mag < 7.5:
        return 7
    elif 7.5 <= mag and mag < 8.0:
        return 8
    elif 8.0 >= mag:
        return 10
    else:
        return 0

def calcular_v(v1,v2):
    distancia = round(distance.distance((v1[1],v1[2]),(v2[3],v2[4])).km)
    dist_val = 0
    if distancia < 80:
        dist_val = 2.5
    elif 80 <= distancia and distancia < 140:
        dist_val = 2
    elif 140 <= distancia and distancia < 200:
        dist_val = 1.5
    elif 200 <= distancia and distancia < 300:
        dist_val = 1
    elif 300 <= distancia and distancia < 400:
        dist_val = 0.5

    return dist_val + v2[0] + v2[1] + v2[2]

def calcular_ir(p,v):
    return (p+v)/2

def asignar_color(ir):
    if ir <= 5:
        return 'verde'
    elif 5.1 < ir and ir <= 6.9:
        return 'amarillo'
    elif ir >= 7:
        return 'rojo'

url_datos_sismicos = '../scraper/data/sismos/'
magnitud_maxima = 8 #cualquier magnitud mayor seria catastrofica
data = os.listdir(url_datos_sismicos)
locs_personas = [
    [19.70078, -101.18443],
 	[18.9261, -99.23075],
 	[16.84942, -99.90891],
 	[19.03793, -98.20346],
    [19.70078, -101.18443],
    [16.75973, -93.11308],
    [19.24997, -103.72714],
    [19.43411, -99.20024],
    [17.06542, -96.72365],
    [17.64344, -101.55212]
    ]
'''
#Morelia
#Cuernavaca
#Acapulco
#Puebla
#Morelia
#Tuxtla
#Colima
#CDMX
#Oaxaca
#Zihuatanejo
'''
valores_dfis = [0.5,1.0,1.5,2.0,2.5]
valores_ubi = [0.5,1.0,1.5,2.0,2.5]
valores_dsen = [0.5,1.5,2.5]

with open(url_datos_sismicos+data[0],'r') as f:
    existing_file = f.read()
    f.close()

content = soup(existing_file,features='xml')
#todas las descripciones [s.find('title').text[5:-4] for s in content.find_all('item')]
#todas las ciudades [s.find('title').text[31:-4] for s in content.find_all('item')]
#sacamos todas las geolocalizaciones de los sismos
locs = [(float(s.find('geo:lat').text),float(s.find('geo:long').text)) for s in content.find_all('item')]
#filtramos para evitar repeticiones
locs = set(locs)
locs = [l for l in locs]
locs = locs[:10]
#generamos magnitudes aleatorias
magnitudes = [round(random.uniform(4.0,8.0),1) for m in range(10)]
#combinamos ambas listas para generar lista de vectores V1
v1 = [[b,a[0],a[1]] for a,b in list(zip( locs, magnitudes))]
#Asignamos valores aleatorios para el vector de usuario
v2 = [[random.choice(valores_dfis),random.choice(valores_dsen),random.choice(valores_ubi),a[0],a[1]] for a in locs_personas]
#Realizamos producto cartesiano de ambas listas y acoplamos en DataFrame para visualizar mejor
print(v1[0])
print(v2[0])
v1andv2 = [a + b for a in v1 for b in v2]
df = pd.DataFrame(v1andv2, columns=['Mag','Slat','Slong','dfis','dsen','U','Plat','Plong'])

#calculo de P y agregado al DataFrame
df['P']=[calcular_p(m[0]) for m in v1andv2]

#calculo de V y agregado al DataFrame
df['V']=[calcular_v(v[:3],v[3:]) for v in v1andv2]

df['IR'] = (df['P']+df['V'])/2

#calculo del color de semaforo
df['Sem'] = [asignar_color(s) for s in list(df['IR'])]

print(df)
print('Generando .csv')
df.to_csv(r'./casos_simulados.csv',index = False, header=True)
