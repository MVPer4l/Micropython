from machine import Pin, PWM, I2C, ADC
from time import sleep
import uasyncio as asyncio
import network
from umqtt.simple import MQTTClient

# Dirección I2C del LM75
LM75_ADDR = 0x48
TEMP_ADDR = 0x00

class Conexion:
    def __init__(self, ssid, password, broker_addr, client_name="TONY_VINCE_7u7", topic="esp32/temperature"):
        self.CLIENT_NAME = client_name
        self.BROKER_ADDR = broker_addr
        self.TOPIC = topic
        self.ssid = ssid
        self.password = password
        self.mqttc = MQTTClient(self.CLIENT_NAME, self.BROKER_ADDR, keepalive=60)
        self.wifi_connected = False

    def conectar_wifi(self):
        """
        Conecta el dispositivo a la red Wi-Fi.
        """
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)

        print("Conectando al Wi-Fi...")
        for _ in range(20):  # Esperar 20 intentos (~10 segundos)
            if wlan.isconnected():
                self.wifi_connected = True
                print("Conexión Wi-Fi establecida.")
                print(f"Dirección IP: {wlan.ifconfig()[0]}")
                return
            sleep(0.5)
        
        print("Error: No se pudo conectar al Wi-Fi.")
        self.wifi_connected = False

    def verificarConexion(self):
        """
        Verifica y establece la conexión con el broker MQTT.
        """
        try:
            if not self.wifi_connected:
                print("Wi-Fi no conectado. Conectando...")
                self.conectar_wifi()

            self.mqttc.connect()
            print("Conexión exitosa con el broker MQTT.")
            return True
        except Exception as e:
            print(f"Error al conectar con el broker MQTT: {e}")
            return False

    def publicar(self, topic, mensaje):
        """
        Publica un mensaje al topic configurado.
        :param topic: El topic donde se publicará el mensaje.
        :param mensaje: Mensaje a publicar.
        """
        try:
            self.mqttc.publish(topic, mensaje)
            print(f"Mensaje publicado en {topic}: {mensaje}")
        except Exception as e:
            print(f"Error al publicar el mensaje: {e}")

    def suscribirse(self, topic, relevador):
        """
        Suscribirse a un topic para recibir mensajes.
        :param topic: El topic al que suscribirse.
        :param relevador: Objeto de la clase relevador.
        """
        try:
            # Usar functools.partial para pasar el relevador al callback
            self.mqttc.set_callback(self.mensaje_recibido)
            self.mqttc.subscribe(topic)
            print(f"Suscrito al topic: {topic}")
        except Exception as e:
            print(f"Error al suscribirse al topic {topic}: {e}")

    def mensaje_recibido(self, topic, msg, relevador):
        """
        Callback ejecutado al recibir un mensaje en el topic suscrito.
        :param topic: Nombre del topic.
        :param msg: Mensaje recibido.
        :param relevador: Objeto de la clase relevador para ejecutar acciones.
        """
        try:
            mensaje = msg.decode().lower()  # Convertir a minúsculas
            print(f"Mensaje recibido en {topic}: {mensaje}")
            
            if mensaje == "on":
                relevador.encender()  # Encender el relevador
                print("Acción: Encender relevador.")
            elif mensaje == "off":
                relevador.apagar()  # Apagar el relevador
                print("Acción: Apagar relevador.")
            else:
                print(f"Comando desconocido: {mensaje}")
        except Exception as e:
            print(f"Error procesando el mensaje: {e}")

    def desconectar(self):
        """
        Desconecta el cliente MQTT.
        """
        try:
            self.mqttc.disconnect()
            print("Cliente MQTT desconectado.")
        except Exception as e:
            print(f"Error al desconectar el cliente MQTT: {e}")

class temperatureSensor:
    def __init__(self, scl_pin=22, sda_pin=21, address=LM75_ADDR):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.address = address

    def get_temperature(self):
        temp_reg = self.i2c.readfrom_mem(LM75_ADDR, TEMP_ADDR, 2)
        temp = (temp_reg[0] << 8 | temp_reg[1]) >> 7
        if temp > 1023:  # Manejar negativos
            temp -= 2048
        return temp * 0.5

async def publicar_temperatura(conexion, sensor):
    """
    Tarea asíncrona para publicar la temperatura periódicamente.
    """
    while True:
        temperatura = sensor.get_temperature()
        conexion.publicar("esp32/temperatura", f"TONY ENVIO TEMPERATURA -> {temperatura:.2f}")
        await asyncio.sleep(2)

async def escuchar_mensajes(conexion):
    """
    Tarea asíncrona para escuchar mensajes en el topic suscrito.
    """
    while True:
        try:
            conexion.mqttc.check_msg()
        except Exception as e:
            print(f"Error al procesar mensajes MQTT: {e}")
        await asyncio.sleep(1)
        
class relevador:
    def __init__(self):
        self.rele = Pin(18, Pin.OUT)
        self.rele.value(0)
    #
    def encender(self):
        self.rele.value(1)
    #
    def apagar(self):
        self.rele.value(0)
    #
#
async def main():
    # Configuración
    ssid = "LINI IP"
    password = "SyMP.IP.2024"
    broker_addr = "192.168.1.102"

    # Inicializa el sensor de temperatura y la conexión
    sensor_temp = temperatureSensor()
    rele = relevador()
    conexion = Conexion(ssid, password, broker_addr)

    # Verifica la conexión
    if not conexion.verificarConexion():
        print("No se pudo conectar al broker. Revisa la configuración.")
        return

    # Suscribirse al topic `esp32/led`
    conexion.suscribirse("esp32/led", rele)

    # Ejecuta las tareas asíncronas
    await asyncio.gather(
        publicar_temperatura(conexion, sensor_temp),
        escuchar_mensajes(conexion)
    )

# Ejecutar el programa principal
asyncio.run(main())
