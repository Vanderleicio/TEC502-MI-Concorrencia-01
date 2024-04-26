''' 
1. Objetivos - Gerenciamento de dispositivos sensores e atenuadores
2. URL base - localhost
3. Endpoints -  localhost/dispositivos (GET)
                localhost/dispositivos/id (GET)
                localhost/dispositivos/id (PUT)


4. Recursos - Dispositivo'''

# Mensagens TCP: {Comando: nº do comando, Confirmacao: Bool}
# Mensagens UDP: {Tipo: [temp, status, conexao], Dado: [Float, Bool, 0]}
import socket
from flask import Flask, jsonify, request
import threading
from time import sleep

app = Flask(__name__)

dispositivos = []
conexoes = [None, ]

BROKER_IP = "192.168.15.5"

TCP_PORT = 5001         #Porta que o broker vai escutar/enviar mensagens TCP
UDP_PORT = 15009

ULTIMOID = 1

sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket p/ enviar comandos
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket p/ receber dados 

def main():
    sockUDP.bind((BROKER_IP, UDP_PORT)) # Conecta o servidor para escutar transmissões UDP
    sockTCP.bind((BROKER_IP, TCP_PORT)) # Conecta o servidor para enviar transmissões TCP
    tDados.start()
    esperar_conexao()
    

def esperar_conexao():
    sockTCP.listen(1)

    conn, addr = sockTCP.accept()
    conectar_novo_dispositivo(addr, conn)

def ler_dados():
    
    while True:
        data, addr = sockUDP.recvfrom(1024)  # buffer size é 1024 bytes
        msg = eval(data.decode())

        
        if (msg.get('Tipo') == 'status'):
            for dispositivo in dispositivos:
                if (dispositivo.get('ip') == addr[0]):
                    dispositivo['ligado'] = msg['Dado']

        elif (msg.get('Tipo') == 'temp'):
            for dispositivo in dispositivos:
                if (dispositivo.get('ip') == addr[0]):
                    dispositivo['temperatura'] = msg['Dado']
        else:
            print("Tipo não reconhecido")

        print("Mensagem recebida:", data.decode())
        print(addr)

def conectar_novo_dispositivo(endereco, conn):
    global ULTIMOID

    novoDisp = {'id': ULTIMOID,
                'ip': endereco[0],
                'temperatura': 0,
                'ligado': False}
    
    dispositivos.append(novoDisp)
    conexoes.insert(novoDisp.get('id'), conn)
    print("Novo dispositivo conectado")
    ULTIMOID += 1

    enviar_comando(4, novoDisp.get('id'))


def enviar_comando(comando, id):
    msg = {'Comando': comando, 'Confirmacao': id if (comando == 4) else False} #Comando que vai ser enviado, 0 p/ Desligar, 1 p/ Ligar, 2 p/ Temperatura atual e 3 p/ Status
    msg = str(msg)
    conexoes[id].sendall(msg.encode())
    print(f"Enviando comando para o dispositivo")

@app.route('/dispositivos', methods=['GET'])
def obter_dispositivos():
    return jsonify(dispositivos)

@app.route('/dispositivos/temp/<int:id>', methods=['GET'])
def obter_dispositivo_temp(id):
    for dispositivo in dispositivos:
        if (dispositivo.get('id') == id):
            comando = 2 # Comando "2" p/ solicitar a temperatura atual do dispositivo
            enviar_comando(comando, id)

            sleep(0.1)#VER COMO CONSERTAR ISSO!

            print(dispositivo.get('temperatura'))
            return jsonify(dispositivo.get('temperatura'))

@app.route('/dispositivos/status/<int:id>', methods=['GET'])
def obter_dispositivo_status(id):
    for dispositivo in dispositivos:
        if (dispositivo.get('id') == id):
            comando = 3 #Comando "3" p/ solicitar o status atual do dispositivo
            enviar_comando(comando, id)

            sleep(0.1) #VER COMO CONSERTAR ISSO!

            return jsonify(dispositivo.get('ligado'))

@app.route('/dispositivos/<int:id>', methods=['PUT'])

def editar_dispositivo(id):
    dispositivo_alterado = request.get_json()

    comando = 1 if dispositivo_alterado.get('ligado') else 0 #Comando "1" se for p/ ligar o dispositivo e "0" p/ desligar

    for index, dispositivo in enumerate(dispositivos):

        if dispositivo.get('id') == id:
            dispositivos[index]['ligado'] = dispositivo_alterado.get('ligado')
            enviar_comando(comando, id)

            return jsonify(dispositivos[index])

tDados = threading.Thread(target=ler_dados)
tMain = threading.Thread(target=main)

if __name__ == '__main__':
    tMain.start()
    app.run(port=5000, host='localhost', debug=False)