import grpc
import grpc_mine_pb2
import grpc_mine_pb2_grpc
import inquirer
import hashlib
import threading
import time
import random
import sys

HOST = 'localhost:8080'
USER_ID = 0

def hash_sha1(val):
    return hashlib.sha1(val.encode()).hexdigest()

def minerar_desafio(valor):
    achado = None
    inicio = time.time()

    def tarefa():
        nonlocal achado
        while achado is None:
            candidato = str(random.getrandbits(64))
            if hash_sha1(candidato).count('0') >= valor:
                achado = candidato
                break

    threads = [threading.Thread(target=tarefa) for _ in range(4)]
    for t in threads: t.start()

    while achado is None:
        tempo = time.time() - inicio
        sys.stdout.write(f"\rMinerando: {tempo:.2f}s")
        sys.stdout.flush()
        time.sleep(0.2)

    for t in threads: t.join()
    print(f"\nMinerado em {time.time() - inicio:.2f}s")
    return achado

def ler_int(mensagem):
    """Solicita input do usuário até que seja um número inteiro válido."""
    while True:
        entrada = input(mensagem).strip()
        if not entrada:
            print("Entrada não pode ser vazia. Tente novamente.")
            continue
        if not entrada.isdigit():
            print("Entrada inválida. Digite apenas números.")
            continue
        return int(entrada)

def iniciar_cliente():
    global USER_ID
    canal = grpc.insecure_channel(HOST)
    stub = grpc_mine_pb2_grpc.MineStub(canal)

    # Registra o cliente no servidor
    USER_ID = stub.registerClient(grpc_mine_pb2.Empty()).result
    print(f"ID registrado: {USER_ID}")

    opcoes = [
        "getTransactionId", "getChallenge", "getTransactionStatus",
        "submitChallenge", "getWinner", "getSolution", "Sair"
    ]

    while True:
        escolha = inquirer.prompt([inquirer.List("acao", message="Escolha ação:", choices=opcoes)])["acao"]

        if escolha == "Sair":
            print("Encerrando...")
            break

        try:
            if escolha == "getTransactionId":
                res = stub.getTransactionId(grpc_mine_pb2.Empty())
                print(f"TransactionID atual: {res.result}")

            elif escolha == "getChallenge":
                tid = ler_int("Digite transactionID: ")
                res = stub.getChallenge(grpc_mine_pb2.TxnId(transactionId=tid))
                print(f"Challenge: {res.result}")

            elif escolha == "getTransactionStatus":
                tid = ler_int("Digite transactionID: ")
                res = stub.getTransactionStatus(grpc_mine_pb2.TxnId(transactionId=tid))
                print("Status:", {0:"Resolvido",1:"Pendente",-1:"Inválido"}.get(res.result,"Desconhecido"))

            elif escolha == "getWinner":
                tid = ler_int("Digite transactionID: ")
                res = stub.getWinner(grpc_mine_pb2.TxnId(transactionId=tid))
                print(f"Vencedor: {res.result if res.result != 0 else 'Ainda não há'}")

            elif escolha == "getSolution":
                tid = ler_int("Digite transactionID: ")
                res = stub.getSolution(grpc_mine_pb2.TxnId(transactionId=tid))
                print(f"Status: { {0:'Resolvido',1:'Pendente',-1:'Inválido'}.get(res.status,'Desconhecido') }, "
                      f"Solução: {res.solution}, Challenge: {res.challenge}")

            elif escolha == "submitChallenge":
                tid = stub.getTransactionId(grpc_mine_pb2.Empty()).result
                print(f"TransactionID atual: {tid}")

                desafio = stub.getChallenge(grpc_mine_pb2.TxnId(transactionId=tid)).result
                print(f"Challenge recebido: {desafio}")

                solucao = minerar_desafio(desafio)
                print(f"Solução encontrada: {solucao}")

                res = stub.submitChallenge(grpc_mine_pb2.TaskRequest(
                    transactionId=tid, clientId=USER_ID, solution=solucao))
                print("Resultado:", {1:"Válida",0:"Inválida",2:"Já resolvida",-1:"ID inválido"}.get(res.result,"Desconhecido"))

        except grpc.RpcError as e:
            print(f"Erro RPC: {e.code()} - {e.details()}")

        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    iniciar_cliente()
