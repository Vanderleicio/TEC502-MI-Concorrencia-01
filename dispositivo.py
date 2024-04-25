from random import random
import threading
import time
import socket

# Mensagens TCP: {Comando: nº do comando, Confirmacao: Bool}
# Mensagens UDP: {Tipo: [temp, status, conexao], Dado: [Float, Bool, 0]}

UDP_IP = "192.168.15.5" # IP do Broker
UDP_PORT = 15009

TCP_IP = "192.168.15.5" # IP do dispositivo
TCP_PORT = 5001

class Dispositivo:

    def __init__(self):
        self.temp = 0
        self.ligado = False

        #Socket para o recebimento de comandos
        self.sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #Socket para o envio de dados
        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tConexao = threading.Thread(target=self.conexao)
        self.tLerComandos = threading.Thread(target=self.receber_comandos)
        self.tParametros = threading.Thread(target=self.definir_parametros)
        self.tEnviar = threading.Thread(target=self.enviar_temperatura)

        self.tConexao.start()
        self.tEnviar.start()
        self.tParametros.start()

    def conexao(self):
        msg = "{'Tipo': 'conexao', 'Dado': 0}"

        self.sockUDP.sendto(msg.encode(), (UDP_IP, UDP_PORT))
        print("Pedido de conexão enviado")


        self.sockTCP.bind((TCP_IP, TCP_PORT))

        self.sockTCP.listen(1)

        print("Aguardando por conexões...")

        self.conn, self.addr = self.sockTCP.accept()
        print("Conexão recebida de:", self.addr)
        self.tLerComandos.start()
        
    def receber_comandos(self):
        while True:
            comando = self.conn.recv(1024)  # buffer size é 1024 bytes
            if not comando:
                break
            print("Comando recebido:", comando.decode())
            msg = eval(comando.decode())
            cmd = msg.get('Comando')
            if cmd == "0":
                self.ligado = False
            elif cmd == "1":
                self.ligado = True
            elif cmd == "2":
                self.enviar_temperatura()
            elif cmd == "3":
                self.enviar_status()
        self.tConexao.start()

    def enviar_status(self):
        msg = {'Tipo': 'status', 'Dado': self.ligado}
        msg = str(msg)

        self.sockUDP.sendto(msg.encode(), (UDP_IP, UDP_PORT))
        print("Status enviado.")

    def enviar_temperatura(self):
        if self.ligado:
            msg = {'Tipo': 'temp', 'Dado': self.temp}
            msg = str(msg)

            self.sockUDP.sendto(msg.encode(), (UDP_IP, UDP_PORT))
            print("Temperatura enviada.")


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
            elif resp == "1":
                if not self.ligado:
                    print("O dispositivo já está desligado.")
                else:
                    self.ligado = False
                    print("Alterado o status do dispositivo para desligado.")
            elif resp == "2":
                pausa = int(input("Digite o tempo em segundos de pausa: "))
                print(f"O dispositivo não funcionará pelos próximos {pausa} segundos.")
            elif resp == "3":
                temp = float(input("Digite a nova temperatura: "))
                self.variar_temp(temp)
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

dispositivo = Dispositivo()


'''========================================================================='''

