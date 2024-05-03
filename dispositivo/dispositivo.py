from random import random
import threading
import time
import socket
import os

# Mensagens TCP: {Comando: nº do comando, Confirmacao: Bool}
# Mensagens UDP: {Id: int, Tipo: [temp, status, conexao], Dado: [Float, Bool, 0]}

BROKER_IP = str(os.environ.get("broker_ip")) # IP do Broker
BROKER_TCP_PORT = 5026
BROKER_UDP_PORT = 5027

print(BROKER_IP)
class Dispositivo:

    def __init__(self):
        self.temp = 0
        self.ligado = False
        self.conectado = False
        #Socket para o envio de dados
        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tConexao = threading.Thread(target=self.conexao)
        self.tLerComandos = threading.Thread(target=self.receber_comandos)
        self.tParametros = threading.Thread(target=self.definir_parametros)
        self.tEnviar = threading.Thread(target=self.enviar_temperatura)

        self.tLerComandos.start()
        self.tConexao.start()
        self.tParametros.start()

    def conexao(self):
        #Socket para o recebimento de comandos
        self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Solicita uma conexão com o Broker p/ adicionar o dispositivo na lista de dispositivos
        self.conectado = False
        while not self.conectado:
            try:
                self.sockTCP.connect((BROKER_IP, BROKER_TCP_PORT))
                self.conectado = True
            except ConnectionRefusedError:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Tentando conexão")

        
    def receber_comandos(self):
        while True:
            if (self.conectado):
                try:
                    comando = self.sockTCP.recv(1024)  # buffer size é 1024 bytes
                except ConnectionResetError:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"Tentando conexão com o broker")
                    self.sockTCP.close()
                    self.conexao()
                    continue
                
                if not comando:
                    print("Breakou 1")
                    break
                print("Comando recebido:", comando.decode())
                msg = eval(comando.decode())
                cmd = msg.get('Comando')
                if cmd == 0:
                    self.ligado = False
                    self.enviar_status()
                elif cmd == 1:
                    self.ligado = True
                    self.enviar_temperatura()
                elif cmd == 2:
                    self.enviar_temperatura()
                elif cmd == 3:
                    self.enviar_status()
                elif cmd == 4:
                    self.id = msg.get('Confirmacao')

    def enviar_status(self):
        msg = {'Id': self.id, 'Tipo': 'status', 'Dado': self.ligado}
        msg = str(msg)

        self.sockUDP.sendto(msg.encode(), (BROKER_IP, BROKER_UDP_PORT))
        print("Status enviado.")

    def enviar_temperatura(self):
        if self.ligado:
            msg = {'Id': self.id, 'Tipo': 'temp', 'Dado': self.temp}
            msg = str(msg)

            self.sockUDP.sendto(msg.encode(), (BROKER_IP, BROKER_UDP_PORT))
            print("Temperatura enviada.")
        else:
            self.enviar_status()


    def definir_parametros(self):
        while True:
            print("Escolha qual parâmetro deseja alterar:\n"
                  "[0] Ligar\n"
                  "[1] Desligar\n"
                  "[2] Pausar\n"
                  "[3] Alterar temperatura\n"
                  "[4] Finalizar programa\n")
            resp = input("Digite a opção desejada: ").strip()
            while (resp not in ["0", "1", "2", "3", "4"]):
                print("Opção não reconhecida\n")
                resp = input("Digite a opção desejada: ").strip()
            
            if resp == "0":
                if self.ligado:
                    print("O dispositivo já está ligado.")
                else:
                    self.ligado = True
                    print("Alterado o status do dispositivo para ligado.")
                self.enviar_status()
            elif resp == "1":
                if not self.ligado:
                    print("O dispositivo já está desligado.")
                else:
                    self.ligado = False
                    print("Alterado o status do dispositivo para desligado.")
                self.enviar_status()
            elif resp == "2":
                pausa = int(input("Digite o tempo em segundos de pausa: "))
                print(f"O dispositivo não funcionará pelos próximos {pausa} segundos.")
            elif resp == "3":
                temp = float(input("Digite a nova temperatura: "))
                #self.variar_temp(temp)
                self.temp = temp
                self.enviar_temperatura()
            else:
                print("Desligando")
                self.sockTCP.close()
                self.sockUDP.close()
            

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

dispositivo1 = Dispositivo()


'''========================================================================='''

