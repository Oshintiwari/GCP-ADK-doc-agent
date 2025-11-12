from datetime import datetime

def log_step(logs: list[str], message: str) -> None:
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    logs.append(f"[{ts}] {message}")
