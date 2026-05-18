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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(), server
    )
    server.add_insecure_port('[::]:50051')
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
