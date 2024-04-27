import tkinter as tk
from tkinter import ttk
import requests

def on_item_select(event):
    item = treeview.selection()
    if item:
        item_values = treeview.item(item, "values")
        selected_item_label.config(text=f"Item selecionado: {item_values[0]}")

def atualizar_lista():
    dados_da_solicitacao = requests.get("http://localhost:5000/dispositivos").json()

    # Limpa a lista existente
    for item in treeview.get_children():
        treeview.delete(item)

    # Adiciona os dados da solicitação à Treeview
    for dados in dados_da_solicitacao:
        treeview.insert("", tk.END, values=(dados["id"], f"{dados['temperatura']} °C", "Ligado" if dados["ligado"] else "Desligado"))

# Inicializa a janela principal
root = tk.Tk()
root.title("Interface Gráfica")

# Cria a Treeview com colunas
treeview = ttk.Treeview(root, columns=("Id", "Temperatura", "Status"), show="headings")
treeview.heading("#0", text="Índice")
treeview.heading("Id", text="Id")
treeview.heading("Temperatura", text="Temperatura")
treeview.heading("Status", text="Status")

# Configura o alinhamento do texto das colunas para centralizar
for coluna in treeview["columns"]:
    treeview.column(coluna, anchor="center")

treeview.bind("<<TreeviewSelect>>", on_item_select)
treeview.pack(padx=10, pady=10)

atualizar_lista()
# Etiqueta para mostrar qual item está selecionado
selected_item_label = ttk.Label(root, text="Item selecionado: ")
selected_item_label.pack()

# Cria o frame para os botões
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Botões adicionais
button1 = ttk.Button(button_frame, text="Ligar")
button1.pack(side=tk.LEFT, padx=5)
button2 = ttk.Button(button_frame, text="Pausar")
button2.pack(side=tk.LEFT, padx=5)
button3 = ttk.Button(button_frame, text="Continuar")
button3.pack(side=tk.LEFT, padx=5)

# Centraliza os botões horizontalmente no frame
button_frame.pack_configure(anchor=tk.CENTER)

# Inicia o loop de eventos
root.mainloop()
