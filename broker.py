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

app = Flask(__name__)

dispositivos = []

TCP_IP = "192.168.15.5" #IP do broker
TCP_PORT = 5001         #Porta que o broker vai escutar/enviar mensagens TCP

UDP_IP = "192.168.15.5"
UDP_PORT = 15009

ULTIMOID = 0

sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket p/ enviar comandos
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket p/ receber dados 

def main():
    sockUDP.bind((UDP_IP , UDP_PORT)) # Conecta o servidor para escutar transmissões UDP
    tDados.start()

def ler_dados():

    while True:
        data, addr = sockUDP.recvfrom(1024)  # buffer size é 1024 bytes
        msg = eval(data.decode())

        if (msg.get('Tipo') == 'conexao'):
            conectar_novo_dispositivo(addr)

        elif (msg.get('Tipo') == 'status'):
            for dispositivo in dispositivos:
                if (dispositivo.get('ip') == addr[0]) and (dispositivo.get('porta') == addr[1]):
                    dispositivo['status'] = msg['Dado']

        elif (msg.get('Tipo') == 'temp'):
            for dispositivo in dispositivos:
                if (dispositivo.get('ip') == addr[0]) and (dispositivo.get('porta') == addr[1]):
                    dispositivo['temperatura'] = msg['Dado']
        else:
            print("Tipo não reconhecido")

        print("Mensagem recebida:", data.decode())
        print(addr)

def conectar_novo_dispositivo(endereco):
    novoDisp = {'id': ULTIMOID,
                'ip': endereco[0],
                'porta': endereco[1],
                'temperatura': 0,
                'ligado': False}
    
    dispositivos.append(novoDisp)
    print("Novo dispositivo conectado")
    enviar_comando((novoDisp.get('ip'), novoDisp.get('porta')), 2)


def enviar_comando(addr, comando):
    sockTCP.connect((addr[0] , addr[1])) # Conecta o servidor para enviar transmissões TCP

    msg = {'Comando': comando, 'Confirmacao': False} #Comando que vai ser enviado, 0 p/ Desligar, 1 p/ Ligar, 2 p/ Temperatura atual e 3 p/ Status
    msg = str(msg)
    sockTCP.sendall(msg.encode())
    print(f"Enviando comando para o dispositivo")

@app.route('/dispositivos', methods=['GET'])
def obter_dispositivos():
    return jsonify(dispositivos)

@app.route('/dispositivos/temp/<int:id>', methods=['GET'])
def obter_dispositivo_temp(id):
    for dispositivo in dispositivos:
        if (dispositivo.get('id') == id):
            comando = "2" # Comando "2" p/ solicitar a temperatura atual do dispositivo
            enviar_comando(dispositivo.get('ip'), comando)


            return jsonify(dispositivo.get('temperatura'))

@app.route('/dispositivos/status/<int:id>', methods=['GET'])
def obter_dispositivo_status(id):
    for dispositivo in dispositivos:
        if (dispositivo.get('id') == id):
            comando = "3" #Comando "3" p/ solicitar o status atual do dispositivo
            enviar_comando(dispositivo.get('ip'), comando)

            return jsonify(dispositivo.get('ligado'))

@app.route('/dispositivos/<int:id>', methods=['PUT'])

def editar_dispositivo(id):
    dispositivo_alterado = request.get_json()

    comando = "1" if dispositivo_alterado.get('ligado') else "0" #Comando "1" se for p/ ligar o dispositivo e "0" p/ desligar

    for index, dispositivo in enumerate(dispositivos):

        if dispositivo.get('id') == id:
            dispositivos[index].update(dispositivo_alterado)
            enviar_comando(dispositivo.get('ip'), comando)

            return jsonify(dispositivos[index])

tDados = threading.Thread(target=ler_dados)

if __name__ == '__main__':
    main()
    app.run(port=5000, host='localhost', debug=False)