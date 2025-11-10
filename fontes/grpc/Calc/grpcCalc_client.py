import grpc
import grpcCalc_pb2
import grpcCalc_pb2_grpc
import pybreaker
import inquirer

breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=2)

@breaker
def init_app():
    channel = grpc.insecure_channel('localhost:8080')
    stub = grpcCalc_pb2_grpc.CalculadoraServiceStub(channel)

    menu_options = ["Adicionar", "Subtrair", "Multiplicar", "Dividir", "Sair"]

    while True:
        question = [
            inquirer.List("action",
                          message="Escolha a operação:",
                          choices=menu_options)
        ]
        answer = inquirer.prompt(question)
        choice = answer["action"]

        if choice == "Sair":
            print("Encerrando aplicação...")
            break

        try:
            first_value = float(input("Digite o primeiro valor: "))
            second_value = float(input("Digite o segundo valor: "))
        except ValueError:
            print("Entrada inválida! Digite apenas números.")
            continue

        try:
            if choice == "Adicionar":
                result = stub.Somar(grpcCalc_pb2.OperacaoDecimal(a=first_value, b=second_value))
            elif choice == "Subtrair":
                result = stub.Subtrair(grpcCalc_pb2.OperacaoDecimal(a=first_value, b=second_value))
            elif choice == "Multiplicar":
                result = stub.Multiplicar(grpcCalc_pb2.OperacaoDecimal(a=first_value, b=second_value))
            elif choice == "Dividir":
                result = stub.Dividir(grpcCalc_pb2.OperacaoDecimal(a=first_value, b=second_value))
            
            print(f"Resultado: {result.resultado}")

        except pybreaker.CircuitBreakerError:
            print("Servidor temporariamente indisponível. Tente novamente mais tarde.")

if __name__ == '__main__':
    init_app()
