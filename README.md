# TEC502-MI-Concorrencia-01

### Sumário 
------------
+ [Como Executar](#como-executar)
+ [Introdução](#introdução)
+ [Tabela de Comandos](#tabela-de-comandos)
+ [Testes](#testes)
+ [Conclusões](#conclusões)
+ [Referências](#referências)

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

## Introdução

A tecnologia tem consistentemente desempenhado um papel fundamental no cotidiano da sociedade, seja para atividades laborais ou mesmo de lazer, ela constantemente está presente facilitando-as. A Internet das Coisas (do inglês _Internet of Things, IoT_), termo cunhado por Kevin Ashton. se mostra cada vez mais como um possível futuro de integração entre os inúmeros dispositivos que nos cercam. Diante desse contexto, foi proposto o desenvolvimento de uma solução capaz de integrar e facilitar a comunicação entre dispositivos e aplicações que precisam das informações geradas por esses dispositivos, o serviço deve implementar um serviço _broker_ que permita haver troca de mensagem entre os dispositivos e a aplicação, e através dele a aplicação deve ser capaz de comunicar com os diversos dispositivos conectados, recebendo e enviando informações.

A solução proposta é majoritariamente dividida em três partes: a aplicação, uma interface gráfica que permite monitorar os dispositivos conectados e comandá-los; o broker, um serviço intermediário capaz de enviar os dados e comandos entre os dispositivos e a aplicação; e o dispositivo, que gera os dados que serão enviados para a aplicação e que tem uma interface não gráfica capaz de simular o comportamento de um sensor real. Já este relatório é dividido em 3 partes além desta Introdução, sendo elas: a discussão detalhada acerca do desenvolvimento do produto, os resultados e como executá-lo.

## Discussão sobre produto

Como já dito acima, a arquitetura da solução é dividida em 3 partes principais, a aplicação, o broker e o dispositivo. A Figura 1 ilustra de maneira geral a organização do serviço, bem como quais são as mensagens trocadas entre suas partes, o que essas mensagens carregam e os protocolos de comunicação utilizados por cada uma delas. Inicialmente serão explicadas as características das comunicações empregadas na solução, para que então os componentes sejam explicados mais detalhadamente.

![DiagramaGeral](https://github.com/Vanderleicio/TEC502-MI-Concorrencia-01/blob/main/imagesREADME/RedesPBL1.jpg)
- **Figura 1:** *Comunicações entre os componentes da solução. [Autor]*

### Comunicação

#### Ordem das mensagens
Como explicado na seção "Como executar", para haver o funcionamento esperado, inicialmente o Broker é executado para que um endereço IP possa ser designado para ele, e para que todas as outras partes possam se comunicar com ele através desse endereço. De uma forma geral, após o Broker ser inicializado, ele espera conexões TCP e UDP vindas dos dispositivos, ou uma requisição HTTP da Aplicação e a comunicaçao para a troca de informações acontece da seguinte forma:

1 - A aplicação requisita ao Broker dados atualizados dos dispositivos conectados;

2 - O Broker solicita a todos os dispositivos que atualizem suas informações;

3 - Os dispositivos enviam sua temperatura atual se ele estiver ligado, ou seu status se desligado;

4 - O Broker atualiza sua lista de dispositivos com as informações retornadas;

5 - O Broker envia a lista de dispositivos como resposta para a requisição HTTP feita pela Aplicação.

Esse processo é o mais recorrente, já que é através dele que a interface gráfica da aplicação se mantem atualizada em relação aos dados dos dispositivos. Porém, todas as outros processos de comunicação entre os componentes do sistema acontece de maneira semelhante, por exemplo, para ligar um dispositivo a Aplicação faz uma requisição ao Broker informando o ID do dispositivo que será alterado, o Broker por sua vez envia um comando ao dispositivo correspondente solicitando que ele altere seu status para ligado, e o dispositivo envia sua status para o Broker, que o atualiza na lista de dispositivos. Esses processos serão detalhados posteriormente.

#### Protocolos utilizados

Para que houvesse uma comunicação correta e satisfatória entre os componentes foi necessária a implementação de protocolos em nível de aplicação e o uso de protocolos de transporte já estabelecidos, sendo eles o _Transmission Control Protocol_(TCP), _User Datagram Protocol_(UDP) e requisições _Hypertext Transfer Protocol_(HTTP). A Figura 2 mostra os protocolos de comunicação a nível de transporte utilizados, quais são as mensagens que são utilizadas com esses protocolos e a formatação utilizada para cada uma dessas mensagens, a fim de que os diferentes componentes possam entender o que se está querendo comunicar de maneira satisfatória. Vale ressaltar que em todas as comunicações a mensagem é transformada em formato JSON antes de ser enviada.

![Protocolos](https://github.com/Vanderleicio/TEC502-MI-Concorrencia-01/blob/main/imagesREADME/ProtocolosUsados.png)
- **Figura 2:** *Protocolos utilizados na solução. [Autor]*

Pela Figura 2 é possível perceber que entre o Broker e os Dispositivos são utilizados os protocolos TCP e UDP. Enquanto o primeiro é utilizado para o envio e a confirmação de comandos, já que ele é uma abordagem confiável de envio de mensagens, o segundo é usado para o envio de dados, e embora ele não garanta a confiabilidade do envio, ele permite que os dados sejam enviados de maneira mais dinâmica, sem que seja necessária a confirmação e permitindo que o envio de dados seja mais frequente em um curto espaço de tempo.

No que diz respeito ao protocolo em nível de aplicação, ele acontece da seguinte forma: Após o Broker ser iniciado ele aguarda que o dispositivo faça uma conexão via TCP e outra via UDP nas portas 5026 e 5027, respectivamente, então o Broker armazena as informações acerca da conexão do dispositivo, e envia uma mensagem de conexão com o ID associado a ele na lista de dispositivos, daí em diante, em todos os envios UDP do dispositivo, ele sinaliza qual é o seu ID para que o Broker saiba de qual dispositivo se trata. Para o envio de comandos gerais, o Broker manda uma mensagem via TCP para o dispositivo e aguarda que ele confirme o recebimento do comando, durante todo tempo o Broker fica aguardando receber mensagens UDP na sua porta 5027, enquanto o dispositivo fica esperando mensagens TCP, assim, sempre que uma mensagem é recebida, eles resolvem o que a mensagem está solicitando, enquanto continuam com as outras tarefas.

### Funcionamento dos componentes

Com toda a comunicação entre os componentes devidamente explicada, agora será clarificado o desenvolvimento dos componentes que formam esse sistema e concomitantemente a forma como cada uma dessas partes executa os protocolos supracitados, processa suas informações e retorna o que é necessário para o correto funcionamento da solução. 
