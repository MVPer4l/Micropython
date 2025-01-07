from machine import I2C, Pin
import time

# Configurar el bus I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Dirección I2C del LM75 (generalmente 0x48)
LM75_ADDR = 0x48
TEMP_ADDR = 0x00

def get_temperature():
    temp_reg = i2c.readfrom_mem(LM75_ADDR, TEMP_ADDR, 2)  # i2c.readfrom_mem(addr, memaddr, nbytes, *, addrsize=8)
    #Tenemos 2 bytes en temp_reg, es necesario juntarlos
    #temp_reg[0] Bits mas significativos, es necesario desplazarlos para dejar espacion a temp_reg[1]
    #Desplazamos con << a la izquierda y unimos con un Or temp_reg[1]
    temp = (temp_reg[0] << 8 | temp_reg[1]) >> 7  # Convertir a temperatura
    if temp > 1023:  # Manejar negativos
        temp -= 2048
    return temp * 0.5  # Convertir a grados Celsius

while True:
    temp = get_temperature()
    print(f"Temperatura: {temp:.2f} °C")
    time.sleep(1)