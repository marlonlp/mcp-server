# MCP Process Monitor

Servidor MCP (Model Context Protocol) para monitoramento de processos locais com Python.

Este projeto expõe ferramentas para:
- listar processos ativos ordenados por uso de memória;
- consultar detalhes de um PID específico;
- encerrar processos locais (com opção de término forçado).

## Funcionalidades

O servidor implementa 3 ferramentas MCP:

1. `listar_processos(limite: int = 15) -> list[dict]`
   - Retorna processos ativos ordenados por `memoria_rss_mb` (descendente).
   - O `limite` é normalizado entre `1` e `100`.

2. `detalhes_processo(pid: int) -> dict`
   - Retorna dados detalhados do processo:
     - PID, nome, status, usuário, uso de CPU e memória;
     - linha de comando (`cmdline`);
     - quantidade de threads;
     - timestamp de criação.

3. `encerrar_processo(pid: int, forcar: bool = False) -> str`
   - Encerra o processo por `terminate()` ou `kill()` quando `forcar=True`.
   - Possui proteção para impedir que o servidor encerre a si próprio.

## Estrutura do projeto

```text
.
├── server.py
└── README.md
```

## Pré-requisitos

- Python 3.10+
- Ambiente Linux/macOS/Windows com acesso aos processos locais

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows (PowerShell)

pip install --upgrade pip
pip install mcp psutil
```

## Execução

```bash
python server.py
```

O servidor inicia em modo MCP e disponibiliza as ferramentas via transporte padrão do SDK (`stdio`).

## Exemplo de uso em cliente MCP (local)

Use o interpretador da sua venv para registrar o servidor no cliente MCP:

```json
{
  "mcpServers": {
    "process-monitor": {
      "command": "/caminho/para/projeto/.venv/bin/python",
      "args": ["/caminho/para/projeto/server.py"]
    }
  }
}
```

## Segurança e permissões

- As ações refletem permissões do usuário que executa o servidor.
- `encerrar_processo` pode interromper serviços críticos se usado sem cuidado.
- Alguns PIDs podem retornar `AccessDenied` dependendo do sistema.

## Próximas melhorias (opcional)

- adicionar métricas de uso de disco/rede por processo;
- incluir filtros por usuário/nome de processo;
- adicionar testes automatizados para as ferramentas MCP.
