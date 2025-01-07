from machine import Pin, Timer, PWM
from time import sleep

# Configuración de LEDs
led_rojo1 = Pin(23, Pin.OUT)
led_rojo2 = Pin(21, Pin.OUT)
led_rojo3 = Pin(18, Pin.OUT)

led_verde1 = Pin(22, Pin.OUT)
led_verde2 = Pin(19, Pin.OUT)
led_verde3 = Pin(5, Pin.OUT)

leds_rojos = [led_rojo1, led_rojo2, led_rojo3]
leds_verdes = [led_verde1, led_verde2, led_verde3]

estado_leds = False

# Temporizador para alternar LEDs
timer_leds = Timer(0)


# Configuración del buzzer
buzzer = PWM(Pin(32))
buzzer.duty(512)


# Función para alternar LEDs
def alternar_leds(timer):
    global estado_leds
    if estado_leds:
        for led in leds_verdes:
            led.on()
        for led in leds_rojos:
            led.off()
    else:
        for led in leds_rojos:
            led.on()
        for led in leds_verdes:
            led.off()
    estado_leds = not estado_leds
    
timer_leds.init(period=500, mode=Timer.PERIODIC, callback=alternar_leds)

# Frecuencias de las 12 notas musicales
notas = {
    "C4": 261.63, "C4#": 277.18, "D4": 293.66, "D4#": 311.13,
    "E4": 329.63, "F4": 349.23, "F4#": 369.99, "G4": 392.00,
    "G4#": 415.30, "A4": 440.00, "A4#": 466.16, "B4": 493.88,
    "C5": 523.26, "D5":587.33, "E5":659.25,"F5":698.45
}


#reproducir nota
def reproducir_nota(nota, duracion=0.5):
    frecuencia = notas.get(nota)
    if frecuencia:
        buzzer.duty(512)
        buzzer.freq(int(frecuencia))
        sleep(duracion)
        sleep(0.01)
        buzzer.duty(0)
        
    elif nota=='stop':
        buzzer.freq()
    else:
        print(f"Nota '{nota}' no reconocida")
        
        
def merriCrismass():
    print("primer compas")
    reproducir_nota("G4", 0.5)
    reproducir_nota("C5", 0.5)
    reproducir_nota("C5", 0.25)
    reproducir_nota("D5", 0.25)
    
    print("2 compas")
    reproducir_nota("C5", 0.25)
    reproducir_nota("B4", 0.25)
    reproducir_nota("A4", 0.5)
    reproducir_nota("A4", 0.5)
    
    print("3 compas")
    reproducir_nota("A4", 0.5)
    reproducir_nota("D5", 0.25)
    reproducir_nota("D5", 0.5)
    reproducir_nota("E5", 0.25)
    
    print("4 compas")
    reproducir_nota("D5", 0.25)
    reproducir_nota("C5", 0.25)
    reproducir_nota("B4", 0.5)
    reproducir_nota("G4", 0.5)
    reproducir_nota("G4", 0.5)
    
    print("5 compas")
    reproducir_nota("E5", 0.5)
    reproducir_nota("E5", 0.25)
    reproducir_nota("F5", 0.25)
    reproducir_nota("E5", 0.25)
    reproducir_nota("D5", 0.25)
    reproducir_nota("C5", 0.5)
    reproducir_nota("A4", 0.5)
    
    print("p6 compas")
    reproducir_nota("G4", 0.25)
    reproducir_nota("G4", 0.25)
    reproducir_nota("A4", 0.5)
    reproducir_nota("D5", 0.5)
    reproducir_nota("B4", 0.5)
    reproducir_nota("C5", 0.5)
    




#REPRODUCIR ESCALA C4-C5
try:
    while True:
        print("Reproduciendo meri crisma <3")
        merriCrismass()
        #for nota in ["C", "D", "E", "F", "G", "A", "B","C8"]:
            #reproducir_nota(nota, 0.5)
        sleep(1)
except KeyboardInterrupt:
    print("Detenido por el usuario")
    timer_leds.deinit()
    buzzer.deinit()