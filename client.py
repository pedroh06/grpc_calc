import grpc
import calculator_pb2
import calculator_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)

        print("--- Somador (ENTER vazio para sair) ---")
        while True:
            entrada = input("Digite 'a b' (ex: 7 5): ").strip()
            if not entrada:
                break
            try:
                a, b = entrada.split()
                request = calculator_pb2.OperationRequest(a=float(a), b=float(b))
                response = stub.Sum(request)
                print(f"  → resultado: {response.result}")
            except ValueError:
                print("  Formato inválido. Use: <num> <num>")
            except grpc.RpcError as e:
                print(f"  → erro [{e.code().name}]: {e.details()}")


if __name__ == '__main__':
    run()
