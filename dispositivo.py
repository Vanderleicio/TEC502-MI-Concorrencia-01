from random import random
import threading
import time
import socket


UDP_IP = "192.168.15.3" # Colocar o IP do destino
UDP_PORT = 5005

TCP_IP = "192.168.15.8" # Colocar o IP da fonte
TCP_PORT = 5004

class Dispositivo:

    def __init__(self):
        self.temp = 0
        self.ligado = False
        self.variar = False

        #Socket para o recebimento de comandos
        self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #Socket para o envio de dados
        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.t0 = threading.Thread(target=self.conexao)
        self.t1 = threading.Thread(target=self.receber_comandos)
        self.t2 = threading.Thread(target=self.definir_parametros)
        self.t3 = threading.Thread(target=self.enviar_temperatura)

        self.t0.start()
        self.t2.start()

        '''
        self.t1 = threading.Thread(target=self.definir_parametros)
        self.t2 = threading.Thread(target=self.variar_temp)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.t1.start()
        self.t2.start()
        self.t2.join()'''

    def conexao(self):
        self.sockTCP.bind((TCP_IP, TCP_PORT))

        self.sockTCP.listen(1)

        print("Aguardando por conexões...")

        self.conn, self.addr = self.sockTCP.accept()
        print("Conexão recebida de:", self.addr)
        self.t1.start()
        
    def receber_comandos(self):
        while True:
            comando = self.conn.recv(1024)  # buffer size é 1024 bytes
            if not comando:
                break
            print("Comando recebido:", comando.decode())
            if comando.decode() == "1":
                print("Foi")
                self.t3.start()



    def enviar_temperatura(self):
        msg = f"{self.temp}"

        self.sockUDP.sendto(msg.encode(), (UDP_IP, UDP_PORT))
        print("Temperatura enviada.")


    def definir_parametros(self):
        while True:
            self.temp = input("Digite a temperatura que voce quer definir: ")
            self.ligado = input("Definir status 0 p/ Desligado, 1 p/ Ligado: ") == "1"
            self.variar = self.ligado and (input("Variar temperatura? 0 p/ Não, 1 p/ Sim: ") == "1")

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


'''========================================================================='''

