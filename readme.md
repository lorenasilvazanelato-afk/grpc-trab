# PPD - Laboratório II: Chamada de Procedimento Remoto (gRPC)

Projeto desenvolvido para a disciplina de Programação Paralela e Distribuída (PPD), focado na implementação de sistemas distribuídos cliente-servidor usando Chamada de Procedimento Remoto (RPC) com a biblioteca gRPC em Python.

O repositório contém as implementações de duas atividades principais, conforme especificado no [documento do laboratório (PPD___Lab_RPC-1.pdf)](fontes/PPD___Lab_RPC-1.pdf).

## Alunos

* Kauã Pereira Porto (2313485)
* Lorena Silva Zanelato (2113314)
* Thayna Pereira Muniz (2310482)

## Atividades Implementadas

### Atividade 1: Calculadora gRPC (30%)

Uma calculadora interativa onde o cliente solicita uma operação (Soma, Subtração, Multiplicação, Divisão) e dois valores. O servidor gRPC (`fontes/grpc/Calc/grpcCalc_server.py`) processa a requisição e retorna o resultado.

O cliente (`fontes/grpc/Calc/grpcCalc_client.py`) utiliza a biblioteca `inquirer` para o menu interativo e `pybreaker` para implementar o padrão **Circuit Breaker**, aumentando a resiliência a falhas do servidor.

### Atividade 2: Mineração de Criptomoedas gRPC (70%)

Um protótipo de um sistema de mineração de criptomoedas.

* **Servidor (`fontes/grpc/Mine/grpcMine_server.py`):**
    * Gerencia o estado das transações, gera desafios criptográficos (baseados na contagem de zeros de um hash SHA-1) e valida as soluções submetidas pelos clientes.
    * O acesso ao estado é protegido por `threading.Lock` para segurança em concorrência.
    * Registra clientes e fornece um ID único (`registerClient`).

* **Cliente (`fontes/grpc/Mine/grpcMine_client.py`):**
    * Se registra no servidor para obter um `USER_ID`.
    * Possui um menu interativo (`inquirer`) para consultar o estado do desafio (`getChallenge`, `getTransactionStatus`, etc.) ou iniciar o processo de mineração (`Mine`).
    * A mineração no cliente é realizada localmente usando múltiplas threads (`minerar_desafio`) para encontrar a solução para o desafio proposto pelo servidor.

## Pré-requisitos

* Python 3.x
* Bibliotecas Python listadas em `fontes/grpc/requirements.txt`.

```bash
pip install -r fontes/grpc/requirements.txt