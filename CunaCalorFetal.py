from machine import Pin, PWM, I2C
from time import sleep

# Dirección I2C del LM75
LM75_ADDR = 0x48
TEMP_ADDR = 0x00


class relevador:
    def __init__(self):
        self.rele = Pin(18, Pin.OUT)
        self.rele.value(1)
    #
    def encender(self):
        self.rele.value(1)
    #
    def apagar(self):
        self.rele.value(0)
    #
#

class temperatureSensor:
    def __init__(self,scl_pin=22, sda_pin=21, address=LM75_ADDR):
        self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.addres=address
    #
    def get_temperature(self):
        temp_reg = self.i2c.readfrom_mem(LM75_ADDR, TEMP_ADDR, 2) 
        temp = (temp_reg[0] << 8 | temp_reg[1]) >> 7 
        if temp > 1023:  # Manejar negativos
            temp -= 2048
        return temp * 0.5
    #
#
class ventiladorPWM:
    def __init__(self, pinPWM=14, frequency=25000, init_duty=10):
        self.frequency = frequency
        self.venti = PWM(Pin(pinPWM), freq=self.frequency)
        self.set_duty(init_duty)
    #
    def set_duty(self, duty_percent):
        if 0 <= duty_percent <= 100:
            duty = int(duty_percent * 1023 / 100)  # Escala el porcentaje al rango 0-1023
            self.venti.duty(duty)
        else:
            raise ValueError("El duty cycle debe estar entre 0 y 100")
        #
    #
    def acelerar(self):
        self.set_duty(100)
    #
    
    def desacelerar(self):
        self.set_duty(10)
    #
    
    def apagar_venti(self):
        self.set_duty(0)
        
        
class FSM:
    def __init__(self, ventilador, relevador):
        self.state = "NORMAL"  # Estado inicial
        self.ventilador = ventilador
        self.relevador = relevador
        self.threshold_high = 30  # Umbral superior
        self.threshold_low = 26                       # Umbral inferior

    def update(self, temperature):
        """
        Actualiza el estado de la máquina basado en la temperatura actual.
        :param temperature: Temperatura en °C leída del sensor.
        """
        if self.state == "NORMAL":
            if temperature > self.threshold_high:
                self.state = "COOLING"
                self.ventilador.acelerar()
                self.relevador.apagar()
                print("Estado: COOLING. Ventilador acelerado. Relevador apagado.")
        
        elif self.state == "COOLING":
            if temperature < self.threshold_low:
                self.state = "WAITING"
                print("Estado: WAITING. Manteniendo configuración actual.")
        
        elif self.state == "WAITING":
            if temperature < self.threshold_low:
                self.state = "NORMAL"
                self.ventilador.apagar_venti()
                self.relevador.encender()
                print("Estado: NORMAL. Ventilador apagado. Relevador encendido.")

def main():
    """
    Método principal que inicializa los dispositivos y ejecuta la FSM.
    """
    # Inicializa los dispositivos
    relevador_device = relevador()
    ventilador_device = ventiladorPWM(pinPWM=14, frequency=25000, init_duty=10)
    sensor_temp = temperatureSensor(scl_pin=22, sda_pin=21, address=LM75_ADDR)

    # Inicializa la FSM
    fsm = FSM(ventilador_device, relevador_device)

    # Bucle principal
    print("Sistema iniciado. Esperando lecturas de temperatura.")
    while True:
        try:
            # Lee la temperatura del sensor
            temperatura = sensor_temp.get_temperature()
            print(f"Temperatura actual: {temperatura:.2f} °C")

            # Actualiza el estado de la FSM
            fsm.update(temperatura)

            # Pausa entre lecturas (ajustable según necesidad)
            sleep(2)

        except Exception as e:
            print(f"Error: {e}")
            sleep(5)  # Espera más tiempo antes de intentar de nuevo en caso de error

# Punto de entrada del programa
if __name__ == "__main__":
    main()