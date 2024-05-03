import socket
from flask import Flask, jsonify, request
import threading
from time import sleep

# Mensagens TCP: {Comando: nº do comando, Confirmacao: Bool}
# Mensagens UDP: {Id: int, Tipo: [temp, status, conexao], Dado: [Float, Bool, 0]}

app = Flask(__name__)

dispositivos = []
conexoes = [None, ]

BROKER_IP = " "

TCP_PORT = 5026         #Porta que o broker vai escutar/enviar mensagens TCP
UDP_PORT = 5027

ULTIMOID = 1

SEMAFORO = True

sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket p/ enviar comandos
sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket p/ receber dados 

def main():
    sockUDP.bind((BROKER_IP, UDP_PORT)) # Conecta o servidor para escutar transmissões UDP
    sockTCP.bind((BROKER_IP, TCP_PORT)) # Conecta o servidor para enviar transmissões TCP
    tDados.start()
    tConexoes.start()
    
def atualizar_ip():
    global BROKER_IP
    try:
        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        BROKER_IP = ip_address
        print("Endereço IP do Broker: " + ip_address)
    except:
        print("Não foi possível conseguir o IP do Broker")

def esperar_conexao():
    while True:
        sockTCP.listen(1)

        conn, addr = sockTCP.accept()
        conectar_novo_dispositivo(addr, conn)

def ler_dados():
    
    while True:
        global SEMAFORO
        data, addr = sockUDP.recvfrom(1024)  # buffer size é 1024 bytes
        msg = eval(data.decode())

        
        if (msg.get('Tipo') == 'status'):
            for dispositivo in dispositivos:
                if (dispositivo.get('id') == msg.get('Id')):
                    dispositivo['ligado'] = msg['Dado']
                    SEMAFORO = True

        elif (msg.get('Tipo') == 'temp'):
            for dispositivo in dispositivos:
                if (dispositivo.get('id') == msg.get('Id')):
                    dispositivo['temperatura'] = msg['Dado']
                    SEMAFORO = True
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
    MAX_TENTATIVAS = 64
    global SEMAFORO
    for i in range(MAX_TENTATIVAS):
        try:
            msg = {'Comando': comando, 'Confirmacao': id if (comando == 4) else False} #Comando que vai ser enviado, 0 p/ Desligar, 1 p/ Ligar, 2 p/ Temperatura atual e 3 p/ Status
            msg = str(msg)
            conexoes[id].sendall(msg.encode())
            print("Enviando comando para o dispositivo")
            break
        except ConnectionResetError:
            print(f"Testando conexão com o dispositivo: Tentativa {i}")
    else:
        print(f"O dispositivo de ID: {id} foi desconectado")
        SEMAFORO = True


@app.route('/dispositivos', methods=['GET'])
def obter_dispositivos():
    global SEMAFORO

    for dispositivo in dispositivos:
        SEMAFORO = False
        enviar_comando(2, dispositivo.get('id')) # Solicita a temperatura atual do dispositivo
    
    while not SEMAFORO:
                print("Esperando resolver comando")


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
    global SEMAFORO
    SEMAFORO = False
    dispositivo_alterado = request.get_json()
    comando = 1 if dispositivo_alterado.get('ligado') else 0 #Comando "1" se for p/ ligar o dispositivo e "0" p/ desligar

    for index, dispositivo in enumerate(dispositivos):

        if dispositivo.get('id') == id:
            dispositivos[index]['ligado'] = dispositivo_alterado.get('ligado')
            enviar_comando(comando, id)
            while not SEMAFORO:
                print("Esperando resolver comando")

            return jsonify(dispositivos[index])

tDados = threading.Thread(target=ler_dados)
tMain = threading.Thread(target=main)
tConexoes = threading.Thread(target=esperar_conexao)

if __name__ == '__main__':
    atualizar_ip()
    tMain.start()
    app.run(port=5025, host=BROKER_IP)