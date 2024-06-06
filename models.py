from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import configparser


# Datos de configuración
config = configparser.ConfigParser()
config.read("simbus.cfg")
system = config["db"]["system"]
name = config["db"]["name"]

# Crear la clase base de la tabla
Base = declarative_base()

# Definir los modelos

# Posiblemente hay que hacer una traducción de los modelos del ORM de Django
# a SQLAlchemy aquí. Evaluar si es necesario copiar cada modelo aquí, o si
# es posible usar una sola tabla para guardar los estados de los viajes.

# Ejemplo no relacionado:

class TestData(Base):
    __tablename__ = "test_data"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    pm10 = Column(Float)
    pm25 = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    country = Column(String)


# Crear la conexión a la base de datos SQLite3
engine = create_engine(f"{system}:///{name}")
Session = sessionmaker(bind=engine)
session = Session()

# Crear la(s) tabla(s) en la base de datos
Base.metadata.create_all(engine)
