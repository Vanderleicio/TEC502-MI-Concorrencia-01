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

TCP_PORT = 5026 # Porta que o broker vai escutar/enviar mensagens TCP
UDP_PORT = 5027 # Porta que o broker vai escutar/enviar mensagens UDP

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

        while True:
            confirmacao = conn.recv(1024)
            if not confirmacao:
                break
            print('Mensagem recebida do cliente:', confirmacao.decode())
            confirmacao = eval(confirmacao)
            if (confirmacao.get('Confirmacao') == None):
                print(confirmacao.get('Confirmacao'))
                ja_conectado = False
            else:
                ja_conectado = confirmacao.get('Confirmacao')
            
            conectar_novo_dispositivo(addr, conn, ja_conectado)
            break

def ler_dados():
    
    while True:
        data, addr = sockUDP.recvfrom(1024)  # buffer size é 1024 bytes
        msg = eval(data.decode())

        
        if (msg.get('Tipo') == 'status'):
            for dispositivo in dispositivos:
                if (dispositivo.get('id') == msg.get('Id')):
                    dispositivo['ligado'] = msg['Dado']

        elif (msg.get('Tipo') == 'temp'):
            for dispositivo in dispositivos:
                if (dispositivo.get('id') == msg.get('Id')):
                    dispositivo['temperatura'] = msg['Dado']
                    dispositivo['ligado'] = True
        else:
            print("Tipo não reconhecido")

        print("Mensagem recebida:", data.decode())
        print(addr)

def conectar_novo_dispositivo(endereco, conn, conexao_antiga):
    global ULTIMOID

    if conexao_antiga: #False se a conexão for nova, ID do dispositivo se for antiga
        # O "novo" dispositivo já estava cadastrado
            disp_antigo = {'id': conexao_antiga,
                'ip': endereco[0],
                'porta': endereco[1],
                'temperatura': 0,
                'ligado': False}
            conexoes[conexao_antiga] = conn
            dispositivos.append(disp_antigo)
    else:
        
        # É realmente um dispositivo novo
        novoDisp = {'id': ULTIMOID,
                    'ip': endereco[0],
                    'porta': endereco[1],
                    'temperatura': 0,
                    'ligado': False}
        
        dispositivos.append(novoDisp)
        if novoDisp.get('id') < len(conexoes):
            conexoes[novoDisp.get('id')] = conn
        else:
            conexoes.insert(novoDisp.get('id'), conn)

        print("Novo dispositivo conectado")
        ULTIMOID += 1

        enviar_comando(4, novoDisp.get('id'))


def enviar_comando(comando, id):

    MAX_TENTATIVAS = 64
    for i in range(MAX_TENTATIVAS):
        try:
            msg = {'Comando': comando, 'Confirmacao': id if (comando == 4) else False} #Comando que vai ser enviado, 0 p/ Desligar, 1 p/ Ligar, 2 p/ Temperatura atual, 3 p/ Status e 4 p/ Conexão
            msg = str(msg)
            conexoes[id].sendall(msg.encode())
            print(f"Enviando comando para o dispositivo")
            conexoes[id].settimeout(0.1) # Espera uma resposta de confirmação por 1 segundo
            confirmacao = conexoes[id].recv(1024)
            break
        except ConnectionResetError:
            print(f"Testando conexão com o dispositivo: Tentativa {i}")
        except socket.timeout:
            print("Não houve confirmação do dispositivo a tempo")
    else:
        print(f"O dispositivo de ID: {id} foi desconectado")
        for index, dispositivo in enumerate(dispositivos):
            if dispositivo.get('id') == id:
                del dispositivos[index]
                conexoes[id] = None


@app.route('/dispositivos', methods=['GET'])
def obter_dispositivos():

    for dispositivo in dispositivos:
        enviar_comando(2, dispositivo.get('id')) # Solicita a temperatura atual do dispositivo
    


    return jsonify(dispositivos)


@app.route('/dispositivos/<int:id>', methods=['PUT'])
def editar_dispositivo(id):
    dispositivo_alterado = request.get_json()
    comando = 1 if dispositivo_alterado.get('ligado') else 0 #Comando "1" se for p/ ligar o dispositivo e "0" p/ desligar

    for index, dispositivo in enumerate(dispositivos):

        if dispositivo.get('id') == id:
            enviar_comando(comando, id)

            return jsonify(dispositivos[index])

tDados = threading.Thread(target=ler_dados)
tMain = threading.Thread(target=main)
tConexoes = threading.Thread(target=esperar_conexao)

if __name__ == '__main__':
    atualizar_ip()
    tMain.start()
    app.run(port=5025, host=BROKER_IP)