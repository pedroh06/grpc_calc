# Projeto gRPC — Calculator (Somador)

## Estrutura
```
grpc_calc/
├── calculator.proto   # contrato (interface)
├── server.py          # servidor gRPC (Sum)
├── client.py          # cliente interativo
└── README.md
```

## Como executar

### 1) Instalar dependências
```bash
pip install grpcio grpcio-tools
```

### 2) Gerar stubs a partir do .proto
Dentro da pasta do projeto:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. calculator.proto
```
Isso cria `calculator_pb2.py` e `calculator_pb2_grpc.py`. **Não edite esses arquivos** — eles são regenerados sempre que o `.proto` muda.

### 3) Rodar
Terminal 1:
```bash
python server.py
```
Terminal 2:
```bash
python client.py
```

## Saída esperada (cliente)
```
--- Somador (ENTER vazio para sair) ---
Digite 'a b' (ex: 7 5): 7 5
  → resultado: 12.0
Digite 'a b' (ex: 7 5): 10 2.5
  → resultado: 12.5
```

## Pontos para a apresentação
- **Contrato antes do código.** O `.proto` é a fonte da verdade. Cliente e servidor poderiam estar em linguagens diferentes (Go, Java) e ainda assim conversariam — desde que ambos gerem stubs do mesmo `.proto`.
- **`double` em vez de `int32`.** Permite somar números fracionários sem mudar o contrato. Custo: mais bytes na rede.
- **Por que HTTP/2:** multiplexação (várias chamadas numa única conexão TCP) e suporte nativo a streaming.
- **Limitação atual:** comunicação `insecure` (sem TLS). Em produção, usar `grpc.secure_channel` com credenciais SSL.
