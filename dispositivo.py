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

        #self.t0.start()
        self.t2.start()

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
            print("Escolha qual parâmetro deseja alterar:\n"
                  "[0] Ligar\n"
                  "[1] Desligar\n"
                  "[2] Pausar\n"
                  "[3] Alterar temperatura\n")
            resp = input("Digite a opção desejada: ").strip()
            while (resp not in ["0", "1", "2", "3"]):
                print("Opção não reconhecida\n")
                resp = input("Digite a opção desejada: ").strip()
            
            if resp == "0":
                if self.ligado:
                    print("O dispositivo já está ligado.")
                else:
                    self.ligado = True
                    print("Alterado o status do dispositivo para ligado.")
            elif resp == "1":
                if not self.ligado:
                    print("O dispositivo já está desligado.")
                else:
                    self.ligado = False
                    print("Alterado o status do dispositivo para desligado.")
            elif resp == "2":
                pausa = int(input("Digite o tempo em segundos de pausa: "))
                print(f"O dispositivo não funcionará pelos próximos {pausa} segundos.")
            else:
                temp = float(input("Digite a nova temperatura: "))
                self.variar_temp(temp)
            

    def variar_temp(self, novaTemp):
        while self.temp != novaTemp:
            if novaTemp > self.temp:
                if (self.temp + 0.5) >= novaTemp:
                    self.temp = novaTemp
                else:
                    self.temp += 0.5
            else:
                if (self.temp - 0.5) <= novaTemp:
                    self.temp = novaTemp
                else:
                    self.temp -= 0.5
            print(self.temp)
            time.sleep(1) 
    
    def checar_comando(self):
        print("Recebi comandos?")
        time.sleep(1)

    def enviar_dados(self):
        print("Enviado")

teste = Dispositivo()


'''========================================================================='''

