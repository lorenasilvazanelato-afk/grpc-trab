import grpc
from concurrent import futures
import grpcCalc_pb2
import grpcCalc_pb2_grpc

class CalculatorServicer(grpcCalc_pb2_grpc.CalculadoraServiceServicer):
    def Somar(self, request, context):
        return grpcCalc_pb2.ResultadoDecimal(resultado=request.a + request.b)

    def Subtrair(self, request, context):
        return grpcCalc_pb2.ResultadoDecimal(resultado=request.a - request.b)

    def Multiplicar(self, request, context):
        return grpcCalc_pb2.ResultadoDecimal(resultado=request.a * request.b)

    def Dividir(self, request, context):
        if request.b == 0:
            return grpcCalc_pb2.ResultadoDecimal(resultado=0)
        return grpcCalc_pb2.ResultadoDecimal(resultado=request.a / request.b)

def iniciar_servidor():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpcCalc_pb2_grpc.add_CalculadoraServiceServicer_to_server(CalculatorServicer(), server)
    server.add_insecure_port('[::]:8080')
    print("Servidor rodando na porta8080")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
