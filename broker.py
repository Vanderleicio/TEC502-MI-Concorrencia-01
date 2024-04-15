''' 
1. Objetivos - Gerenciamento de dispositivos sensores e atenuadores
2. URL base - localhost
3. Endpoints -  localhost/dispositivos (GET)
                localhost/dispositivos/id (GET)
                localhost/dispositivos/id (PUT)


4. Recursos - Dispositivo'''
import socket
from flask import Flask, jsonify, request

app = Flask(__name__)

dispositivos = [
    {
        'id': 1,
        'ip': '192.168.15.8',
        'temperatura': 32.5,
        'ligado': True
    },
    {
        'id': 2,
        'ip': '192.168.15.8',
        'temperatura': 45.1,
        'ligado': False
    },
    {
        'id': 3,
        'ip': '192.168.15.8',
        'temperatura': 13.0,
        'ligado': True
    }
]
TCP_IP = "192.168.15.8" #IP do dispositivo
TCP_PORT = 5004         #Porta que o dispositvo está escutando

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_STREAM)

def main():
    print("Programa principal")

def ler_dados():
    print("Dados dos dispositivos")

def enviar_comando(ip, comando):
    sock.connect((ip, TCP_PORT))
    msg = comando #Comando que vai ser enviado, 0 p/ Desligar, 1 p/ Ligar, 2 p/ Reiniciar e 3 p/ Temperatura atual
    sock.sendall(msg.encode())
    print(f"Enviando comando para o dispositivo {ip}")

@app.route('/dispositivos', methods=['GET'])
def obter_dispositivos():
    return jsonify(dispositivos)

@app.route('/dispositivos/<string:ip>', methods=['GET'])
def obter_dispositivo_ip(id):
    for dispositivo in dispositivos:
        if (dispositivo.get('id') == id):
            return jsonify(dispositivo)

@app.route('/dispositivos/<int:id>', methods=['PUT'])
def editar_dispositivo(id):
    dispositivo_alterado = request.get_json()

    comando = "1" if dispositivo_alterado.get('ligado') else "0"

    for index, dispositivo in enumerate(dispositivos):

        if dispositivo.get('id') == id:
            dispositivos[index].update(dispositivo_alterado)
            enviar_comando(dispositivo.get('ip'), comando)

            return jsonify(dispositivos[index])

app.run(port=5000, host='localhost', debug=True)