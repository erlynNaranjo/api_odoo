from xmlrpc import client as xmlrpclib
import datetime

# Configuración para la conexión XML-RPC
url = 'https://erlynnaranjo-prueba-api-prueba-12864339.dev.odoo.com'
db = 'erlynnaranjo-prueba-api-prueba-12864339'
username = 'erlyn@example.com'
password = '006a7426bf551252d6f7af5bb1dc9e5a8d36ea06'

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
def show_available_hours(day_of_week):
    events = get_events_for_day(day_of_week)
    if events:
        print("\nHoras disponibles para el día seleccionado:")
        available_hours = get_available_hours(events)
        for hour in available_hours:
            if hour in working_hours:
                print(hour)
    else:
        print("\nNo hay eventos programados para el día seleccionado.")

if __name__ == "__main__":
    print("Bienvenido al sistema de citas.")
    appointment_types = get_appointment_type_names()
    if appointment_types:
        print("\nLista de nombres de citas del modelo appointment.type:")
        for i, appointment_type in enumerate(appointment_types, start=1):
            print(f"{i}. {appointment_type['name']}")
        selected_index = int(input("\nPor favor, seleccione el número de la cita: "))
        selected_appointment = appointment_types[selected_index - 1]
        day_of_week = int(input("Por favor, ingrese el número del día de la semana (1 para lunes, 2 para martes, ..., 7 para domingo): "))
        show_available_hours(day_of_week)
        
        # Obtener las horas disponibles
        events = get_events_for_day(day_of_week)
        available_hours = get_available_hours(events)
        
        # Solicitar al usuario que elija una hora disponible
        print("\nSeleccione una hora disponible:")
        for i, hour in enumerate(available_hours, start=1):
            if hour in working_hours:
                print(f"{i}. {hour}")
        selected_hour_index = input("\nPor favor, seleccione el número de la hora disponible: ")
        selected_hour = available_hours[int(selected_hour_index) - 1]
        
        # Solicitar el nombre del usuario
        user_name = input("\nIngrese su nombre: ")
        
        # Definir target_date_str
        today = datetime.datetime.now().date()
        days_until_day = (day_of_week - today.weekday() + 7) % 7
        target_date = today + datetime.timedelta(days=days_until_day)
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        # Crear el evento correspondiente a la cita seleccionada
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if uid:
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            new_event = {
                'name': selected_appointment['name'],
                'start': f'{target_date_str} {selected_hour}:00',
                'stop': f'{target_date_str} {selected_hour}:00',
                'appointment_type_id': selected_appointment['id'],
                'create_uid': user_name,  # Asignar el nombre del usuario al campo create_uid
                # Puedes agregar más campos del evento según sea necesario
            }

            event_id = models.execute_kw(db, uid, password, 'calendar.event', 'create', [new_event])
            print(f"\nEvento creado con ID: {event_id}")
        else:
            print("\nError de autenticación.")
