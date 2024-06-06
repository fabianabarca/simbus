from celery import Celery
from celery.schedules import timedelta
from datetime import datetime
import requests
import json
import configparser
from decouple import config


from models import session

# Datos de configuración
config = configparser.ConfigParser()
config.read("simbus.cfg")
url = config["api"]["url"]
token = config["api"]["token"]
period = int(config["scheduler"]["period"])


# Crear "app" de Celery
app = Celery("tasks", broker="redis://localhost")


# Configurar las tareas de Celery

"""
IMPORTANTE

Hacer pruebas locales primero, y solamente después (posiblemente luego de revisión) en el servidor.
"""

@app.task
def post_vehicle():
    """
    Esto posiblemente hay que hacerlo una sola vez, al principio, para registrar el vehículo en el sistema. O si cambia la configuración del vehículo. Pero podría ser cada 24 horas o cada semana, solamente por si acaso.

    O podríamos no usarlo si el vehículo ya está registrado en el sistema (pero esto es riesgoso porque si el vehículo no está registrado, no se podrán enviar los datos de posición, etc.)
    """
    # https://realtime.bucr.digital/api/vehicle
    return "Enviando datos del vehículo"


@app.task
def post_equipment():
    """
    Aplica lo mismo que para los datos del vehículo, porque no requiere actualización constante después de la primera vez.
    """
    #
    return "Enviando datos del equipo"


@app.task
def post_trip():
    """
    En este simulador será creado un viaje en cada sentido cada 5 minutos. Esto es arbitrario, y el objetivo es tener siempre un viaje en curso para poder enviar datos de posición y avance de la ruta y visualizarlo en las pantallas y sitios web. La duración aproximada del viaje es de 25 minutos.
    """
    # https://realtime.bucr.digital/api/trip
    return "Enviando datos del viaje"


@app.task
def post_position():
    """
    Esta es la parte esencial. Debe construirse con los datos de gtfs/shapes.csv para la ruta del viaje. Una forma de hacerlo es la siguiente: asumir una velocidad constante en todo el viaje (calculado a partir de la distancia total del viaje y la duración del viaje) y cada 10 segundos elegir una de las coordenadas de la ruta que sea aproximadamente equivalente a la distancia recorrida en ese tiempo. La columna shape_dist_traveled puede ser útil para esto. Pueden ser saltos de 10 en 10 puntos o algo similar, solamente hay que estar seguros de que llegue al punto final.
    """
    # https://realtime.bucr.digital/api/position
    return "Enviando datos de posición"


@app.task
def post_path():
    """
    Para esto es necesario conocer las ubicaciones de las paradas en gtfs/stops.csv, y así poder saber por cuál parada va el viaje. Es posible que sea necesario crear o una tabla auxiliar o una columna auxiliar en shapes.csv para saber cuál es la parada siguiente y también cuándo es que está parado en una parada. Esto es importante para poder enviar los datos de ocupación del vehículo.

    Desde aquí hay que invocar post_occupancy() cuando el vehículo está en una parada.
    """
    # https://realtime.bucr.digital/api/path
    return "Enviando datos de avance de la ruta"


def post_occupancy():
    """Ejecutada desde post_position() cuando es detectado el vehículo está en una parada"""
    # https://realtime.bucr.digital/api/occupancy/
    return "Enviando datos de ocupación del vehículo"


# ----------
# Configurar aquí las tareas de Celery para el procesamiento de los datos
# ----------

# Configurar el planificador de tareas de Celery
app.conf.beat_schedule = {
    "post-vehicle": {
        "task": "tasks.post_vehicle",
        "schedule": timedelta(hours=24),
    },
    "post-equipment": {
        "task": "tasks.post_equipment",
        "schedule": timedelta(hours=24),
    },
    "post-trip": {
        "task": "tasks.post_trip",
        "schedule": timedelta(minutes=5),
    },
    "post-position": {
        "task": "tasks.post_position",
        "schedule": timedelta(seconds=10),
    },
    "post-path": {
        "task": "tasks.post_path",
        "schedule": timedelta(seconds=10),
    },
}
