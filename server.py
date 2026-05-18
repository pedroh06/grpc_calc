import grpc
from concurrent import futures
import time

import calculator_pb2
import calculator_pb2_grpc


class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):

    def Sum(self, request, context):
        result = request.a + request.b
        print(f"[Sum]      {request.a} + {request.b} = {result}")
        return calculator_pb2.OperationResponse(result=result)

    def Subtract(self, request, context):
        result = request.a - request.b
        print(f"[Subtract] {request.a} - {request.b} = {result}")
        return calculator_pb2.OperationResponse(result=result)

    def Multiply(self, request, context):
        result = request.a * request.b
        print(f"[Multiply] {request.a} * {request.b} = {result}")
        return calculator_pb2.OperationResponse(result=result)

    def Divide(self, request, context):
        if request.b == 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                          "Divisão por zero não é permitida.")
        result = request.a / request.b
        print(f"[Divide]   {request.a} / {request.b} = {result}")
        return calculator_pb2.OperationResponse(result=result)

    def SumStream(self, request_iterator, context):
        total = 0.0
        count = 0
        for n in request_iterator:
            total += n.value
            count += 1
        print(f"[SumStream] soma de {count} valores = {total}")
        return calculator_pb2.OperationResponse(result=total)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(), server
    )

    # --- Modo padrão: canal inseguro (sem TLS) ---
    server.add_insecure_port('[::]:50051')

    # --- Alternativa segura (SSL/TLS) ---
    # Gere os certificados com:
    #   openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt \
    #     -days 365 -nodes -subj "/CN=localhost"
    # e descomente:
    #
    # with open('server.key', 'rb') as k, open('server.crt', 'rb') as c:
    #     creds = grpc.ssl_server_credentials([(k.read(), c.read())])
    # server.add_secure_port('[::]:50051', creds)

    server.start()
    print("Servidor gRPC iniciado na porta 50051. (Ctrl+C para encerrar)")

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        print("\nServidor interrompido.")


if __name__ == '__main__':
    serve()
