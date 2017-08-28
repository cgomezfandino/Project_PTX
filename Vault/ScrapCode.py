import requests
from bs4 import BeautifulSoup

peticiones = []
names = []
airplanes_names = []
for j in airplanes_ok[0:100]:
    r = requests.get('https://en.wikipedia.org/wiki/' + str(j))
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')
        peticion = soup.find_all('table', {'class': "infobox"})
        peticiones += (peticion)
        names += [j]

        if j == '':
            airplanes_names += ['Nada']
        else:
            airplanes_names += [str(j)]

        print str(j) + ' Downloaded'

Role = []
Manufacturer = []
First_flight = []
Introduction = []
Produced = []
Number_built = []
Name_ = []

for i in peticiones:
    # print type (i)
    rol = None
    if (i.find('th', string='Role') != None):
        rol = i.find('th', string='Role').find_next('td').text

    manu = None
    if (i.find('th', string='Manufacturer') != None):
        manu = i.find('th', string='Manufacturer').find_next('td').text

    first = None
    if (i.find('th', string='First flight') != None):
        first = i.find('th', string='First flight').find_next('td').text

    intro = None
    if (i.find('th', string='Introduction') != None):
        first = i.find('th', string='Introduction').find_next('td').text

    prod = None
    if (i.find('th', string='Produced') != None):
        prod = i.find('th', string='Produced').find_next('td').text

    numb = None
    if (i.find('th', string='Number built') != None):
        numb = i.find('th', string='Number built').find_next('td').text

    name_ = None
    if (i.find('td', string='') != None):
        name_ = i.find('td', string='').find_next('th').text

    Role.append(rol)
    Manufacturer.append(manu)
    First_flight.append(first)
    Introduction.append(intro)
    Produced.append(prod)
    Number_built.append(numb)
    Name_.append(name_)