import socket

def enviar_mensagem(host, porta, mensagem):
    # Cria um socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Conecta ao servidor
        s.connect((host, porta))
        # Envia a mensagem
        s.sendall(mensagem.encode())
        print("Mensagem enviada:", mensagem)

# Configurações do servidor
HOST = 'localhost'  # Host do servidor
PORTA = 12345        # Porta que o servidor está ouvindo

# Mensagem a ser enviada
mensagem = "Olá, servidor!"

# Envia a mensagem para o servidor
enviar_mensagem(HOST, PORTA, mensagem)
