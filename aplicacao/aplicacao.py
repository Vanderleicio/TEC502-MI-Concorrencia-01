import tkinter as tk
from tkinter import ttk
import requests
import threading
from time import sleep
import os

dispositivos = []
#IP_BROKER = os.environ.get("broker_ip")
IP_BROKER = "192.168.15.7"
print(IP_BROKER)
URL_PADRAO = "http://" + str(IP_BROKER) + ":5025"
CONECTADO = False

def on_item_select(event):
    item = treeview.selection()
    if item:
        item_values = treeview.item(item, "values")
        selected_item_label.config(text=f"Item selecionado: {item_values[0]}")
        button1.config(text=f"{'Desligar' if (item_values[2] == 'Ligado') else 'Ligar'}")

def ligar_dispositivo():
    item = treeview.selection()
    if item:
        item_values = treeview.item(item, "values")
        treeview.item(item, values=(item_values[0], item_values[1], "Desligando..." if (item_values[2] == 'Ligado') else "Ligando..."))
        idDisp = item_values[0]
        status = item_values[2] == 'Ligado'
        route = URL_PADRAO + '/dispositivos/' + idDisp
        corpo = {'id': idDisp, 'ip': '', 'temperatura': '', 'ligado': not status}
        resposta = requests.put(route, json=corpo)

def update_status(texto, cor):
    status_label.config(text=texto, fg=cor)

def atualizar_lista():
    global dispositivos, CONECTADO
    while True:
        CONECTADO = False

        while not CONECTADO:
            try:
                dados_da_solicitacao = requests.get(URL_PADRAO + "/dispositivos").json()
                CONECTADO = True
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Conectado com o Broker")
                update_status("Conectado", "green")
            except:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Tentando conexão")
                update_status("Desconectado", "red")
        
        print(dispositivos)
        if (dispositivos != dados_da_solicitacao):
            # Limpa a lista existente
            for item in treeview.get_children():
                treeview.delete(item)

            # Adiciona os dados da solicitação à Treeview
            
            for dados in dados_da_solicitacao:

                treeview.insert("", tk.END, values=(dados["id"], f"{dados['temperatura']} °C", "Ligado" if dados["ligado"] else "Desligado"))
            
            dispositivos = dados_da_solicitacao
        sleep(0.5)

def inicializacao():
    # Define os títulos das colunas
    treeview.heading("#0", text="Índice")
    treeview.heading("Id", text="Id")
    treeview.heading("Temperatura", text="Temperatura")
    treeview.heading("Status", text="Status")

    # Configura o alinhamento do texto das colunas para centralizar
    for coluna in treeview["columns"]:
        treeview.column(coluna, anchor="center")

    treeview.bind("<<TreeviewSelect>>", on_item_select)

    # Organiza os elementos da tela

    treeview.pack(padx=10, pady=10)

    status_label.pack(pady=20)

    selected_item_label.pack()

    button_frame.pack(pady=10)

    button1.pack(side=tk.LEFT, padx=5)

    button_frame.pack_configure(anchor=tk.CENTER)


def loop_atualizacoes():
    while True:
        button1.config(state="normal" if CONECTADO else "disabled")


root = tk.Tk()
root.title("Controle dos sensores")

# Cria os elementos da tela
treeview = ttk.Treeview(root, columns=("Id", "Temperatura", "Status"), show="headings")
status_label = tk.Label(root, text="Desconectado", fg="red", font=("Helvetica", 16))
selected_item_label = ttk.Label(root, text="Item selecionado: ")
button_frame = ttk.Frame(root)
button1 = ttk.Button(button_frame, text="Ligar/Desligar", command=ligar_dispositivo)

inicializacao()

# Thread para atualização constante da lista de sensores
tAtualizacao = threading.Thread(target=atualizar_lista)
tAtualizacao.start()

# Thread para atualizações de elementos dinâmicos da tela
tLoop = threading.Thread(target=loop_atualizacoes)
tLoop.start()

root.mainloop()