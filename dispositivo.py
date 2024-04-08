from random import random
import threading
import time
import socket

# Endereço IP e porta do destino
UDP_IP = "192.0.0.0" #Colocar o IP do destino
UDP_PORT = 5005
class Dispositivo:

    def __init__(self):
        self.temp = 0
        self.ligado = False
        self.variar = False

        self.t1 = threading.Thread(target=self.definir_parametros)
        self.t2 = threading.Thread(target=self.variar_temp)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.t1.start()
        self.t2.start()
        self.t2.join()

        

    def definir_parametros(self):
        self.temp = float(input("Digite a temperatura que voce quer definir: "))
        self.ligado = input("Definir status 0 p/ Desligado, 1 p/ Ligado: ") == "1"
        self.variar = self.ligado and (input("Variar temperatura? 0 p/ Não, 1 p/ Sim: ") == "1")
        
        MESSAGE = f"{self.temp}"
        
        self.sock.sendto(MESSAGE.encode(), ("192.168.15.4", 5005))
        self.sock.close()
        #if self.variar:
            #self.variar_temp()

    def variar_temp(self):
        cont = 0
        while self.variar:
            r = random()
            cont += 1
            print(cont)
            if (r > 0.99):
                if (r > 0.995):
                    self.temp += 0.1
                else:
                    self.temp -= 0.1
            
            if (cont > 1000):
                self.t1.start()
    
    def checar_comando(self):
        print("Recebi comandos?")
        time.sleep(1)

    def enviar_dados(self):
        print("Enviado")

teste = Dispositivo()