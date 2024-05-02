from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from xmlrpc import client as xmlrpclib
import datetime

# Definición de estados de la conversación
SELECTING_FEATURE, TYPING = range(2)

# Configuración para la conexión XML-RPC
url = 'https://erlynnaranjo-prueba-api-prueba-12864339.dev.odoo.com'
db = 'erlynnaranjo-prueba-api-prueba-12864339'
username = 'erlyn@example.com'
password = '006a7426bf551252d6f7af5bb1dc9e5a8d36ea06'

BOT_TOKEN = 'TOKEN'

# Horario laboral
working_hours = [
    "09:00 - 09:30",
    "10:00 - 10:30",
    "11:00 - 11:30",
    "14:00 - 14:30",
    "15:00 - 15:30",
    "16:00 - 16:30"
]

# Función para obtener los nombres de las citas del modelo appointment.type
def get_appointment_type_names():
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if uid:
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        appointment_types = models.execute_kw(db, uid, password, 'appointment.type', 'search_read', [[]], {'fields': ['id', 'name']})
        return appointment_types
    else:
        return []

# Función para obtener los eventos programados para un día específico
def get_events_for_day(day_of_week):
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if uid:
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        today = datetime.datetime.now().date()
        days_until_day = (day_of_week - today.weekday() + 7) % 7
        target_date = today + datetime.timedelta(days=days_until_day)
        target_date_str = target_date.strftime('%Y-%m-%d')
        domain = [('start', '>=', target_date_str + ' 09:00:00'), ('start', '<=', target_date_str + ' 16:30:00')]
        events = models.execute_kw(db, uid, password, 'calendar.event', 'search_read', [domain], {'fields': ['start', 'stop', 'appointment_type_id']})
        return events
    else:
        return []

# Función para generar las horas disponibles a partir de los eventos programados
def get_available_hours(events):
    busy_hours = set()
    for event in events:
        start_hour = event['start'].split()[1][:5]
        end_hour = event['stop'].split()[1][:5]
        current_hour = start_hour
        while current_hour < end_hour:
            busy_hours.add(current_hour)
            current_hour = (datetime.datetime.strptime(current_hour, '%H:%M') + datetime.timedelta(hours=1)).strftime('%H:%M')
    all_hours = [f"{hour}:00" for hour in range(9, 17)]  # Horario laboral de 9:00 a 16:30
    available_hours = sorted(set(all_hours) - busy_hours)
    return available_hours

# Mostrar las horas disponibles para el día seleccionado
def show_available_hours(update: Update, context: CallbackContext):
    day_of_week = int(update.message.text)
    events = get_events_for_day(day_of_week)
    if events:
        available_hours = get_available_hours(events)
        available_hours_str = "\n".join(hour for hour in available_hours if hour in working_hours)
        update.message.reply_text(f"\nHoras disponibles para el día seleccionado:\n{available_hours_str}")
    else:
        update.message.reply_text("\nNo hay eventos programados para el día seleccionado.")

# Función para iniciar la conversación
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Hola! Por favor selecciona una opción:",
        reply_markup=...,  # Aquí debes proporcionar el teclado de opciones
    )
    return SELECTING_FEATURE

# Función para seleccionar una característica
def select_feature(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Seleccionaste la característica: {}".format(query.data)
    )
    return TYPING

# Función para manejar la entrada de texto
def save_input(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    # Aquí puedes procesar el texto ingresado
    update.message.reply_text("Texto guardado correctamente!")
    return ConversationHandler.END

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_FEATURE: [CallbackQueryHandler(select_feature)],
            TYPING: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_input)],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, show_available_hours))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

