import json, hashlib
from pathlib import Path

_CACHE = Path(".cache/embeddings.json")
_CACHE.parent.mkdir(parents=True, exist_ok=True)
_store = {}
if _CACHE.exists():
    try: _store = json.loads(_CACHE.read_text())
    except: _store = {}

def _key(text, model):  # deterministic key
    return hashlib.sha256((model + "||" + text).encode()).hexdigest()

def get_cached(text, model):
    return _store.get(_key(text, model))

def put_cached(text, model, vec):
    _store[_key(text, model)] = vec

def flush():
    _CACHE.write_text(json.dumps(_store))
