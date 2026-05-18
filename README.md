# Projeto gRPC — Calculator

## Estrutura
```
grpc_calc/
├── calculator.proto   # contrato (interface)
├── server.py          # servidor gRPC (Sum, Subtract, Multiply, Divide, SumStream)
├── client.py          # cliente interativo
└── README.md
```

## Como executar

### 1) Instalar dependências
```bash
pip install grpcio grpcio-tools
```

### 2) Gerar stubs a partir do .proto
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
--- Calculadora gRPC ---
Comandos:
  sum|sub|mul|div <a> <b>     ex: sum 7 5
  stream <n1> <n2> ...        ex: stream 1 2 3 4 5
  (ENTER vazio para sair)
> sum 7 5
  → resultado: 12.0
> sub 20 8
  → resultado: 12.0
> mul 6 9
  → resultado: 54.0
> div 100 4
  → resultado: 25.0
> div 10 0
  → erro [INVALID_ARGUMENT]: Divisão por zero não é permitida.
> stream 1 2 3 4 5
  → soma stream: 15.0
```

## Pontos para a apresentação
- **Contrato antes do código.** O `.proto` é a fonte da verdade. Cliente e servidor poderiam estar em linguagens diferentes (Go, Java) e ainda assim conversariam — desde que ambos gerem stubs do mesmo `.proto`.
- **`double` em vez de `int32`.** Permite divisão com resultado fracionário sem mudar o contrato. Custo: mais bytes na rede.
- **Tratamento de erro via `context.abort`.** Em REST você devolveria HTTP 400; em gRPC o equivalente é abortar com `StatusCode.INVALID_ARGUMENT`. O cliente captura via `grpc.RpcError`.
- **Por que HTTP/2:** multiplexação (várias chamadas numa única conexão TCP) e suporte nativo a streaming.
- **Limitação atual:** comunicação `insecure` (sem TLS). Em produção, usar `grpc.secure_channel` com credenciais SSL.

---

## 9. Extensões e Discussões

### 9.1 Novos métodos
Adicionar uma operação ao serviço gRPC envolve três passos:
1. **Atualizar o `.proto`** — declarar o novo `rpc` dentro de `service Calculator`.
2. **Regenerar os stubs** com `grpc_tools.protoc` (comando do passo 2 acima).
3. **Implementar o método** no `CalculatorServicer` em [server.py](server.py) e, se quiser expor no CLI, mapear no dispatch do [client.py](client.py).

Neste projeto, partindo apenas de `Sum`, restauramos `Subtract`, `Multiply` e `Divide`. `Divide` ilustra **erro de domínio em gRPC**: em vez de devolver `NaN`, o servidor aborta com `context.abort(grpc.StatusCode.INVALID_ARGUMENT, "...")` quando `b == 0`, e o cliente captura via `grpc.RpcError`.

### 9.2 Streaming
gRPC suporta 4 modos de RPC, todos sobre HTTP/2:

| Modo | Request | Response | Exemplo |
|---|---|---|---|
| Unary | 1 | 1 | `Sum(a, b)` |
| Server-streaming | 1 | N | acompanhar evolução de um cálculo longo |
| Client-streaming | N | 1 | **`SumStream`** — somar N valores |
| Bidirectional | N | N | chat, pipelines de processamento |

Implementamos **`SumStream`** (client-streaming): o cliente envia um fluxo de `OperationNumber` e o servidor responde **uma única vez** com a soma total. No `.proto`:
```proto
rpc SumStream(stream OperationNumber) returns (OperationResponse);
```

No servidor, o método recebe um **iterador**:
```python
def SumStream(self, request_iterator, context):
    total = 0.0
    for n in request_iterator:
        total += n.value
    return calculator_pb2.OperationResponse(result=total)
```

No cliente, basta entregar um **gerador** ao stub. Teste com `stream 1 2 3 4 5` no CLI.

**Vantagem prática:** uma única conexão e uma única chamada para somar 1.000 valores, em vez de 1.000 RPCs unárias — economia de overhead de rede e melhor throughput.

### 9.3 Segurança (SSL/TLS)
O projeto roda em **`insecure_channel` / `add_insecure_port`** — sem criptografia, adequado apenas para desenvolvimento local. Para produção, gRPC usa TLS nativamente sobre HTTP/2.

**Gerar certificado auto-assinado para teste local:**
```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt \
  -days 365 -nodes -subj "/CN=localhost"
```

**Servidor com TLS** (snippet já presente comentado em [server.py](server.py)):
```python
with open('server.key', 'rb') as k, open('server.crt', 'rb') as c:
    creds = grpc.ssl_server_credentials([(k.read(), c.read())])
server.add_secure_port('[::]:50051', creds)
```

**Cliente com TLS** (snippet já presente comentado em [client.py](client.py)):
```python
with open('server.crt', 'rb') as c:
    creds = grpc.ssl_channel_credentials(c.read())
channel = grpc.secure_channel('localhost:50051', creds)
```

**Tópicos para aprofundar:**
- **mTLS (mutual TLS):** o cliente também apresenta certificado — comum em comunicação interna entre microserviços.
- **CA confiável:** em produção, use certificados emitidos por uma CA (Let's Encrypt, CA interna) em vez de auto-assinados.
- **Rotação e gestão:** ferramentas como cert-manager (Kubernetes) e service meshes (Istio, Linkerd) automatizam emissão, renovação e mTLS entre serviços.

### 9.4 gRPC vs REST

| Aspecto | gRPC | REST/JSON |
|---|---|---|
| Transporte | HTTP/2 (multiplexação, header compression) | HTTP/1.1 (geralmente) |
| Payload | Protobuf binário (compacto, rápido) | JSON texto (legível, verboso) |
| Contrato | `.proto` forte e versionado | OpenAPI/Swagger (opcional) |
| Tipagem | Estática, stubs gerados | Dinâmica, validação manual |
| Streaming | Nativo (4 modos) | SSE / WebSocket à parte |
| Browser | Precisa de `grpc-web` | Nativo |
| Debug humano | Difícil (binário, precisa de `grpcurl`) | Fácil (curl, navegador) |
| Multi-linguagem | Excelente (codegen oficial) | Boa via bibliotecas |
| Cache HTTP | Limitado | Excelente (verbos + status codes) |

**Quando usar gRPC:** comunicação interna entre microserviços, sistemas com requisitos de baixa latência/alto throughput, pipelines de streaming, ambientes poliglotas onde o contrato forte evita bugs de integração.

**Quando usar REST:** APIs públicas/voltadas para browser, integração com terceiros, cenários onde cache HTTP e debug via curl importam, equipes sem disciplina para manter um `.proto` versionado.

**Híbrido também é válido:** muitas empresas expõem REST/GraphQL na borda (para o browser/clientes externos) e gRPC internamente entre serviços.
