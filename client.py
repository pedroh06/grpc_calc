import grpc
import calculator_pb2
import calculator_pb2_grpc


def call(stub, op_name, a, b):
    method = {
        "sum": stub.Sum,
        "sub": stub.Subtract,
        "mul": stub.Multiply,
        "div": stub.Divide,
    }[op_name]

    request = calculator_pb2.OperationRequest(a=a, b=b)
    try:
        response = method(request)
        print(f"  → resultado: {response.result}")
    except grpc.RpcError as e:
        print(f"  → erro [{e.code().name}]: {e.details()}")


def call_stream(stub, values):
    def _gen():
        for v in values:
            yield calculator_pb2.OperationNumber(value=v)
    try:
        response = stub.SumStream(_gen())
        print(f"  → soma stream: {response.result}")
    except grpc.RpcError as e:
        print(f"  → erro [{e.code().name}]: {e.details()}")


def run():
    # --- Modo padrão: canal inseguro (sem TLS) ---
    channel = grpc.insecure_channel('localhost:50051')

    # --- Alternativa segura (SSL/TLS) ---
    # with open('server.crt', 'rb') as c:
    #     creds = grpc.ssl_channel_credentials(c.read())
    # channel = grpc.secure_channel('localhost:50051', creds)

    with channel:
        stub = calculator_pb2_grpc.CalculatorStub(channel)

        print("--- Calculadora gRPC ---")
        print("Comandos:")
        print("  sum|sub|mul|div <a> <b>     ex: sum 7 5")
        print("  stream <n1> <n2> ...        ex: stream 1 2 3 4 5")
        print("  (ENTER vazio para sair)")

        while True:
            entrada = input("> ").strip()
            if not entrada:
                break
            partes = entrada.split()
            try:
                if partes[0] == "stream":
                    valores = [float(x) for x in partes[1:]]
                    if not valores:
                        print("  Informe ao menos um número.")
                        continue
                    call_stream(stub, valores)
                else:
                    op, a, b = partes
                    call(stub, op, float(a), float(b))
            except (ValueError, KeyError, IndexError):
                print("  Formato inválido. Use: sum|sub|mul|div <num> <num>  ou  stream <num> <num> ...")


if __name__ == '__main__':
    run()
