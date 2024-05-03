# TEC502-MI-Concorrencia-01
 
## Como executar a solução:
Certifique-se de ter o [Python](https://www.python.org) 3.11 instalado na sua máquina, ou faça o download. É crucial também ter o Docker instalado, porque é através dele que as imagens de 2 dos 3 componentes do sistema serão obtidas.

### Obtendo as imagens:
Execute os seguintes comandos para baixar as imagens:
```
docker pull vanderleicio/dispositivo:latest
```
```
docker pull vanderleicio/broker:latest
```

### Executandos as imagens obtidas:
Após a obtenção das imagens será necessário executá-las. A primeira imagem a ser executada deve ser o broker, porque ela fornece o IP que será passado para a imagem seguinte:
```
docker run -it -p 5025:5025 vanderleicio/dispositivo
```
Copie o número do IP do Broker e passe como variável de execução da imagem dos Dispositivos (no lugar de {broker_ip}):
```
docker run -it -e broker_ip={broker_ip} vanderleicio/dispositivo
```

### Executando a aplicação:
Baixe o arquivo [aplicacao.py]([https://gist.github.com/usuario/linkParaInfoSobreContribuicoes](https://github.com/Vanderleicio/TEC502-MI-Concorrencia-01/blob/main/aplicacao/aplicacao.py)) e o execute com o comando:
```
python aplicacao/aplicacao.py
```
Pronto, a solução já está executando e funcionando.
