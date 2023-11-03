import json
import paho.mqtt.client as paho
from paho import mqtt
import pymysql
import re

def send_sql(dict):
    conexion=pymysql.connect(host="localhost",user="root",password="",database="datos_estaciones")
    cursor=conexion.cursor()
    sql="""INSERT INTO datos_generales (estacion, fecha, hora, temperatura, humedad, velocidad_viento, intensidad_solar, presion_atmosferica)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql,(
        dict["Estacion"],
        dict["Fecha"],
        dict["Hora"],
        dict["Temp"],
        dict["Hum"],
        dict["VelViento"],
        dict["IntSolar"],
        dict["PresAtm"]
    ))
    print("Datos enviados!")
    conexion.commit()
    conexion.close()



def add_json(dict):
    dict=str(dict)
    dict=dict.replace("'",'"')
    with open("datageneral.json","a") as file:  
        file.write(dict+"\n")
    file.close()



def on_message(client,used_data,msg):
    print(msg.topic + " " + str(msg.qos))
    
    print("dato recibido correctamente")
    data=msg.payload.decode()
    #print(type(data))
    data=str(data)
    x=re.search("^{",data)
    print(data)
    if x:
        print("Dato correcto!")
        data=json.loads(msg.payload.decode())
        print(type(data))

        data["Estacion"]=str(msg.topic)
        
        try:
            if "hora" in data:
                data["Hora"]=data["hora"]
        except:
            data["Hora"]="-"

        try:
            if "fecha" in data:
                data["Fecha"]=data["fecha"]
        except:
            data["Fecha"]="-"
        
        try:
            if "temp" in data:
                data["Temp"]=data["temp"]
        except:
            data["Temp"]="-"

        try:
            if "hum" in data:
                data["Hum"]=data["hum"]
        except:
            data["Hum"]="-"

        try:
            if "Velviento" in data:
                data["VelViento"]=data["Velviento"]
        except:
            if "velviento" in data:
                data["VelViento"]=data["velviento"]

        try:
            if "intsolar" in data:
                data["IntSolar"]=data["intsolar"]
        except:
            data["IntSolar"]='-'
        
        try:
            if "presatm" in data:
                data["PresAtm"]=data["presatm"]
        except:
            data["PresAtm"]='-'
        add_json(data)
        #send_sql(data)
    else:
        print("Dato denegado")
        print(data)
        
    print(data)

    #add_json(data)
    #send_sql(data)

client=paho.Client(client_id="",userdata=None,protocol=paho.MQTTv5)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("Grupo#8_TARS","Jirafaelectronica1!")
client.connect("36e9b7c4f0d8445489a9802addb355e3.s1.eu.hivemq.cloud",8883)

client.on_message=on_message
client.subscribe("Reto_UMES/#", qos=2)
client.subscribe("Reto_Umes/#", qos=2)

client.loop_forever()