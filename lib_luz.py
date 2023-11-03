import machine

class sensor_luz:
    
    def __init__(self,PinUv,PinLdr):
        self.uv=machine.ADC(machine.Pin(PinUv))
        self.ldr=machine.ADC(machine.Pin(PinLdr))
        self.index=0
                
    def info_sensorUV(self):
        while True:
            try:
                self.LecturaUv=self.uv.read()
                voltaje=(self.LecturaUv*3.3/4095)*1000
                break
            except:
                pass
        try:
            if 0<voltaje<50:
                self.index=0
            elif 50<voltaje<227:
                self.index=1
            elif 227<voltaje<318:
                self.index=2
            elif 318<voltaje<408:
                self.index=3
            elif 408<voltaje<503:
                self.index=4
            elif 503<voltaje<606:
                self.index=5
            elif 606<voltaje<696:
                self.index=6
            elif 696<voltaje<795:
                self.index=7
            elif 795<voltaje<881:
                self.index=8
            elif 881<voltaje<976:
                 self.index=9
            elif 976<voltaje<1079:
                  self.index=10
            elif voltaje>1079:
                 self.index=11             
        except:
            self.index=0
        return self.index
            
    def info_sensorLDR(self):
        LecturaLdr=self.ldr.read()
        if int(self.index)>3:
            while True:
                try:
                    k=0.19
                    valor=4095-LecturaLdr
                    self.lum=k*valor
                    break
                except:
                    pass
        else:
            self.lum=0
                
        return self.lum
   
