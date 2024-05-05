from random import random
import threading
import time
import socket
import os

# Mensagens TCP: {Comando: nº do comando, Confirmacao: Bool}
# Mensagens UDP: {Id: int, Tipo: [temp, status, conexao], Dado: [Float, Bool, 0]}

#BROKER_IP = str(os.environ.get("broker_ip")) # IP do Broker
BROKER_IP = '192.168.15.7'
BROKER_TCP_PORT = 5026
BROKER_UDP_PORT = 5027

print(BROKER_IP)
class Dispositivo:

    def __init__(self):
        self.temp = 0
        self.ligado = False
        self.conectado = False
        self.id = None
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
        # Faz a conexão e reconexão com o Broker

        # Socket para o recebimento de comandos
        self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.conectado = False
        while not self.conectado:
            try:
                # Solicita uma conexão com o Broker p/ adicionar o dispositivo na lista de dispositivos
                self.sockTCP.connect((BROKER_IP, BROKER_TCP_PORT))
                self.conectado = True

                # Protocolo de iniciação, se None o dispositivo nunca esteve cadastrado no broker
                msg = {'Comando': 4, 'Confirmacao': self.id} 
                msg = str(msg)
                self.sockTCP.sendall(msg.encode())

            except ConnectionRefusedError:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Tentando conexão com o Broker")
            except OSError:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("A conexão com o broker foi desligada")
            
        
    def receber_comandos(self):
        while True:
            if (self.conectado):

                try:
                    comando = self.sockTCP.recv(1024)  # buffer size é 1024 bytes
                except ConnectionResetError:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"Conexão com o broker foi desligada")
                    self.sockTCP.close()
                    self.conexao()
                    continue
                except ConnectionAbortedError:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Falha na rede, tentando reconexão com o Broker")
                    self.sockTCP.close()
                    self.conexao()
                    continue

                if not comando:
                    continue

                print("Comando recebido:", comando.decode())
                
                
                msg = eval(comando.decode())
                cmd = msg.get('Comando')

                conf = {'Comando': cmd, 'Confirmacao': True}
                self.sockTCP.sendall(str(conf).encode())

                if cmd == 0:
                    self.ligado = False
                    self.enviar_status()
                elif cmd == 1:
                    self.ligado = True
                    self.enviar_status()
                    self.enviar_temperatura()
                elif cmd == 2:
                    self.enviar_temperatura()
                elif cmd == 3:
                    self.enviar_status()
                elif cmd == 4:
                    self.enviar_status()
                    self.enviar_temperatura()
                    self.id = msg.get('Confirmacao')

    def enviar_status(self):
        msg = {'Id': self.id, 'Tipo': 'status', 'Dado': self.ligado}
        msg = str(msg)
        try:
            self.sockUDP.sendto(msg.encode(), (BROKER_IP, BROKER_UDP_PORT))
            print("Status enviado.")
        except OSError:
            print("A conexão com o broker foi desligada")
            self.sockTCP.close()
            self.conexao()

    def enviar_temperatura(self):
        if self.ligado:
            # Se estiver ligaod envia a temperatura registrada.
            try:
                msg = {'Id': self.id, 'Tipo': 'temp', 'Dado': self.temp}
                msg = str(msg)

                self.sockUDP.sendto(msg.encode(), (BROKER_IP, BROKER_UDP_PORT))
                print("Temperatura enviada.")
            except OSError:
                print("A conexão com o broker foi desligada")
                self.sockTCP.close()
                self.conexao()
        else:
            # Se estiver desligado envia o status, e não a temperatura atual
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
                self.temp = temp
                self.enviar_temperatura()
            else:
                print("Desligando")
                self.sockTCP.close()
                self.sockUDP.close()

dispositivo1 = Dispositivo()


'''========================================================================='''

