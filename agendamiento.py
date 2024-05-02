from xmlrpc import client as xmlrpclib
import datetime

url = 'https://erlynnaranjo-prueba-api-prueba-12864339.dev.odoo.com'
db = 'erlynnaranjo-prueba-api-prueba-12864339'
username = 'erlyn@example.com'
password = '006a7426bf551252d6f7af5bb1dc9e5a8d36ea06'

# Autenticación
common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

# Verificación de la autenticación
if uid:
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Obtener la fecha actual
    today = datetime.datetime.now().date()

    # Calcular la fecha dentro de tres días
    three_days_later = today + datetime.timedelta(days=3)

    # Convertir las fechas en formato de cadena
    today_str = today.strftime('%Y-%m-%d')
    three_days_later_str = three_days_later.strftime('%Y-%m-%d')

    # Definir el dominio para buscar eventos entre la fecha actual y tres días después
    domain = [('start', '>=', today_str + ' 00:00:00'), ('start', '<=', three_days_later_str + ' 23:59:59')]

    # Buscar eventos dentro del rango de fechas
    reserv = models.execute_kw(db, uid, password, 'calendar.event', 'search_read', [domain], {'fields': ['name', 'user_name']})

    if reserv:
        print("Personas con eventos en el calendario:")
        for event in reserv:
            print("Nombre: %s" % (event.get('user_name')))
    else:
        print("No se encontraron eventos en el calendario.")
else:
    print("No se pudo autenticar.")
