#LIBRERIAS
#internas
from machine import Pin, SoftI2C, ADC
import time
import network
from umqtt.simple import MQTTClient
import ujson
import utime
import urequests
#externas
from lib_lcd1602_2004_with_i2c import LCD
from dht import DHT11
from bmp085 import BMP180
from lib_luz import sensor_luz



#FUNCIONES
#funcion para interrupcion
def interrup(Pin):
    global last_interrupt_time,run_program,button, lcd, red, yellow, green
    lista=[]
    current_time= time.ticks_ms()
    if time.ticks_diff(current_time, last_interrupt_time)>1000:
        run_program=not run_program
    last_interrupt_time=current_time
    if run_program==False:
        print("interrupcion")
        lcd.clear()
        time.sleep(0.5)
        lcd.puts("MANTENIMIENTO",1,3)
        green.off()
        red.on()
        fecha,hora=def_fecha_hora()
        data = {"Estacion":"E8_CAP_08", "Fecha":str(fecha), "Hora":str(hora), "Temp":0, "Hum":0, "VelViento":0, "UV":0, "IntSolar":0, "PresAtm":0, "Altitud":0, "Interrup":1}
        lista.append(data)
        send_mqtt(lista)
        lcd.puts("MANTENIMIENTO",1,3)
        while Pin.value()==0:
            pass
        print("fin interrupcion")
        red.off()
        green.on()
        lcd.clear()
        time.sleep(0.5)
            
    
#funcion de configuracion
def setup():
    global net_name, passwordwifi, run_program, button,last_interrupt_time, green, yellow,red,act_sensor,wifi
    global dht, lcd, bmp, sensores_luz, url
    global port,user,passwordmqtt,mqtt_id,keepalive,ssl,ssl_params,server
    #Datos para conexion wifi
    net_name="RED"
    passwordwifi="PASSWORD"
    wifi=network.WLAN(network.STA_IF)
    
    #variables
    run_program=True #variable de condicion para que el programa entre en pausa o no
    last_interrupt_time=0
    
    #configuracion de entras y salidas digitales
    button = Pin(9, Pin.IN, Pin.PULL_DOWN)
    button.irq(trigger=Pin.IRQ_FALLING, handler=interrup)
    green=Pin(6,Pin.OUT)
    green.on()
    yellow=Pin(7,Pin.OUT)
    yellow.off()
    red=Pin(8,Pin.OUT)
    red.off()
    act_sensor=Pin(5,Pin.OUT) #enciende los sensores
    act_sensor.on()
    
    #configuracion del modulo i2c
    scl_pin = 12
    sda_pin = 11
    i2c = SoftI2C(scl_pin,sda_pin,freq=100000)
    print("modulo i2c configurado")
    
    #configuracion de la pantalla lcd
    lcd = LCD(i2c)
    print('Pantalla LCD configurada')
    
    #configuracion del sensor bmp180
    bmp = BMP180(i2c)
    bmp.oversample = 2
    bmp.sealevel = 101325
    print("Sensor bmp180 configurado")
    
    #configuracion del sensor dht11
    dht = DHT11 (Pin(3))
    while True:
        try:
            dht.measure()
            break
        except:
            pass
    print("sensor dht11 configurado")
    
    #configuracion del sensor UVM30A
    sensores_luz=sensor_luz(1,2)
    
    #API para tiempo
    url = 'http://worldtimeapi.org/api/timezone/America/Guatemala'
    
    #DATOS MQTT
    port=0
    user=b'USER'
    passwordmqtt=b'PASSWORD'
    mqtt_id=b''
    keepalive = 7200
    ssl = True
    ssl_params = {'server_hostname':'36e9b7c4f0d8445489a9802addb355e3.s1.eu.hivemq.cloud'}
    server = b'36e9b7c4f0d8445489a9802addb355e3.s1.eu.hivemq.cloud'
    
    
    
#funcion de conexion wifi
def wifi_connect(condition):
    global net_name, passwordwifi,wifi

    if condition:
        wifi.active(True) #encender wifi
        time.sleep(0.5)
        while True:
            try:
                wifi.connect(net_name,passwordwifi)
                break
            except:
                wifi.active(False)
                time.sleep(1)
                wifi.active(True)
        #verificar conexion
        time.sleep(0.5)
        while not wifi.isconnected():
            #print("intentando reconectar")
            pass
       # print(f"Conexion establecida con {net_name}")
        #print(wifi.ifconfig())
    else:
        wifi.active(False) #apagar wifi
        #print(wifi.isconnected())
        #print("Wifi apagado")

#enviar datos al mqtt
def send_mqtt(datos):
    global port,user,passwordmqtt,mqtt_id,keepalive,ssl,ssl_params,server, yellow,lcd
    lcd.clear()
    time.sleep(0.5)
    lcd.puts("Enviando datos")
    yellow.on()
    wifi_connect(True)
    time.sleep(0.5)
    # Crea un cliente MQTT
    client = MQTTClient(mqtt_id,server,port,user,passwordmqtt,keepalive,ssl,ssl_params)
    client.connect()
    
    # Publica los datos en el tópico "sensores"

    for i in datos:
        json_data = ujson.dumps(i)
        client.publish("Reto_UMES/E8_CAP_08/sensores.json",json_data)
        time.sleep(5)
        
    # Desconecta del broker MQTT
    print("Datos enviados correctamente")
    client.disconnect()
    yellow.off()
    wifi_connect(False)
    lcd.clear()
    time.sleep(0.5)

def def_fecha_hora():
    global url
    contador=0
    wifi_connect(True)
    while True:
        try:
            response = urequests.get("http://worldtimeapi.org/api/timezone/America/Guatemala",timeout=0.5)
            break
        except:
            print("intento ",contador)
            contador+=1
            pass 

    if response.status_code == 200:
        data = response.json()  # Obtener los datos de respuesta como JSON
        fecha = data['datetime'][:10]  # Extraer la fecha y hora
        fecha=fecha[5:7]+"/"+fecha[8:10]+"/"+fecha[:4]
        hora = data['datetime'][11:19]  # Extraer la fecha y hora
    else:
        fecha="00/00/0000"
        hora="00:00:00"
    
    response.close()  # Cerrar la conexión
    wifi_connect(False)
    return fecha, hora


#funcion del programa pricipal
def loop():
    global lcd, bmp, dht, sensores_luz,lcd
    while True:
        lecturas=[]
        contador=0
        while contador<3:
            #LECTURAS
            fecha,hora=def_fecha_hora()
            temp= dht.temperature()
            hum= dht.humidity()
            uv= sensores_luz.info_sensorUV()
            ldr= sensores_luz.info_sensorLDR()
            presion= bmp.pressure
            altitud= bmp.altitude
            viento=0
            data = {"Estacion":"E8_CAP_08", "Fecha":str(fecha), "Hora":str(hora), "Temp":temp, "Hum":hum, "VelViento":viento, "UV":uv, "IntSolar":ldr, "PresAtm":presion, "Altitud":altitud, "Interrup":0}
            lecturas.append(data)
            contador+=1
            print(f"Dato #{contador} leido")
            n=0
            time.sleep(5)
             while n<20:
                time.sleep(0.5)
                lcd.puts("TEMPERATURA: "+str(temp)+"C",0,0)
                lcd.puts("HUMEDAD: "+str(hum)+"%",2,0)
                time.sleep(5)
                lcd.clear()
                
                time.sleep(0.5)
                lcd.puts("PRESION: "+str(presion)+"hP",0,0)
                lcd.puts("ALTITUD: "+str(altitud)+"m",2,0)
                time.sleep(5)
                lcd.clear()
                
                time.sleep(0.5)
                lcd.puts("UV: "+str(uv),0,0)
                lcd.puts("LUZ: "+str(ldr)+" lum",2,0)
                time.sleep(5)
                lcd.clear()
                n+=1

        #print(lecturas)
        send_mqtt(lecturas)
   
#PROGRAMA PRINCIPAL
if __name__=="__main__":
    setup()
    loop()
