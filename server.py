from __future__ import annotations
from typing import Any

import psutil
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Process Monitor",
    instructions="Servidor MCP para monitoramento de processos locais",
)


def _bytes_para_mb(valor: int) -> float:
    return round(valor / (1024 * 1024), 2)


def _serializar_processo(proc: psutil.Process) -> dict[str, Any]:
    with proc.oneshot():
        memoria = proc.memory_info()
        return {
            "pid": proc.pid,
            "nome": proc.name(),
            "status": proc.status(),
            "usuario": proc.username(),
            "cpu_percent": proc.cpu_percent(interval=0.05),
            "memoria_rss_mb": _bytes_para_mb(memoria.rss),
            "memoria_vms_mb": _bytes_para_mb(memoria.vms),
        }


@mcp.tool()
def listar_processos(limite: int = 15) -> list[dict[str, Any]]:
    """Lista processos ativos ordenados por uso de memória (RSS)."""
    processos: list[dict[str, Any]] = []

    for proc in psutil.process_iter():
        try:
            processos.append(_serializar_processo(proc))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processos.sort(key=lambda item: item["memoria_rss_mb"], reverse=True)
    return processos[: max(1, min(limite, 100))]


@mcp.tool()
def detalhes_processo(pid: int) -> dict[str, Any]:
    """Retorna detalhes de um PID específico."""
    try:
        proc = psutil.Process(pid)
        with proc.oneshot():
            return {
                **_serializar_processo(proc),
                "cmdline": proc.cmdline(),
                "threads": proc.num_threads(),
                "aberto_em": proc.create_time(),
            }
    except psutil.NoSuchProcess:
        return {"erro": f"Processo PID={pid} não encontrado"}
    except psutil.AccessDenied:
        return {"erro": f"Acesso negado ao processo PID={pid}"}


@mcp.tool()
def encerrar_processo(pid: int, forcar: bool = False) -> str:
    """Encerra um processo. Use forcar=True para kill imediato."""
    try:
        processo_atual = psutil.Process()
        if pid == processo_atual.pid:
            return "Operacao bloqueada: o servidor não pode encerrar a si próprio."

        alvo = psutil.Process(pid)
        if forcar:
            alvo.kill()
        else:
            alvo.terminate()

        alvo.wait(timeout=3)
        return f"Processo PID={pid} encerrado com sucesso."
    except psutil.NoSuchProcess:
        return f"Processo PID={pid} não existe."
    except psutil.AccessDenied:
        return f"Sem permissão para encerrar PID={pid}."
    except psutil.TimeoutExpired:
        return f"Timeout ao encerrar PID={pid}. Tente novamente com forcar=True."


if __name__ == "__main__":
    mcp.run()