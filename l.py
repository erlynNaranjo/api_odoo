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

    # Campos que deseamos leer
    fields = ['name', 'start', 'stop', 'location', 'create_uid']

    # Buscar eventos dentro del rango de fechas
    reserv = models.execute_kw(db, uid, password, 'calendar.event', 'search_read', [domain], {'fields': fields})

    if reserv:
        print("Eventos en el calendario:")
        for event in reserv:
            print("Nombre: %s" % (event['name']))
            print("Fecha y hora de inicio: %s" % (event['start']))
            print("Fecha y hora de fin: %s" % (event['stop']))
            print("Ubicación: %s" % (event['location']))
            print("ID del usuario que creó el evento: %s" % (event['create_uid']))
            print("---------------------------------------")
    else:
        print("No se encontraron eventos en el calendario.")
else:
    print("No se pudo autenticar.")




import datetime
from telebot import TeleBot

# Replace with your actual bot token
BOT_TOKEN = "'6717368965:AAGZD7z21p0OPFyQxi2pvDRSJtWMQNdUWC8'"

# Define your working hours
working_hours = {
    "monday": ["09:00 - 09:30", "10:00 - 10:30", "11:00 - 11:30", "14:00 - 14:30", "15:00 - 15:30", "16:00 - 16:30"],
    "tuesday": ["09:00 - 09:30", "10:00 - 10:30", "11:00 - 11:30", "14:00 - 14:30", "15:00 - 15:30", "16:00 - 16:30"],
    # ... define working hours for other weekdays ...
    "sunday": []  # No working hours on Sunday
}


def is_working_hour(hour):
    """Checks if the given hour is within working hours"""
    return any(start <= hour <= end for start, end in working_hours.get(datetime.datetime.now().strftime("%A").lower(), []))


def get_available_hours(events):
    """Calculates available hours based on events and working hours"""
    busy_hours = set()
    for event in events:
        start_hour, end_hour = event["start"].split()[1][:5], event["stop"].split()[1][:5]
        current_hour = start_hour
        while current_hour < end_hour:
            busy_hours.add(current_hour)
            current_hour = (datetime.datetime.strptime(current_hour, "%H:%M") + datetime.timedelta(hours=1)).strftime("%H:%M")
    all_hours = [f"{hour}:00" for hour in range(9, 17)]
    available_hours = sorted(set(all_hours) - busy_hours)
    return [hour for hour in available_hours if is_working_hour(hour)]


def handle_message(message):
    """Handles user messages and sends available hours"""
    day_of_week = message.text.lower()
    if day_of_week not in working_hours:
        bot.send_message(message.chat.id, "Invalid day of the week. Please enter a valid weekday (Monday-Sunday).")
        return

    events = []  # Simulate fetching events (replace with actual logic)
    available_hours = get_available_hours(events)

    if available_hours:
        available_hours_str = "\n".join(available_hours)
        bot.send_message(message.chat.id, f"Available hours for {day_of_week}:\n{available_hours_str}")
    else:
        bot.send_message(message.chat.id, f"No available hours for {day_of_week}.")


bot = TeleBot(BOT_TOKEN)
bot.message_handler(func=lambda message: True)(handle_message)

# Starts the bot
bot.infinity_polling()

