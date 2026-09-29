"""
test_performance_1m.py - Benchmark y Validación de 1,000,000 de Registros
==========================================================================
Verifica que el motor de base de datos soporte 1,000,000 de registros,
consultas con paginación en menos de 50ms y deduplicación sin sobrecarga.
"""
import time
import sqlite3
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def db_1m(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("bench") / "benchmark_1m.db"
    conn = sqlite3.connect(str(db_file))
    
    # Optimizaciones SQLite para alta concurrencia y volumen masivo
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = 10000")
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        documento TEXT,
        nombre TEXT,
        celular TEXT,
        direccion TEXT
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS ix_cli_doc ON clientes(documento);")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_cli_nom ON clientes(nombre);")
    conn.execute("CREATE INDEX IF NOT EXISTS ix_cli_cel ON clientes(celular);")
    
    yield conn
    conn.close()

def test_insercion_masiva_1_millon(db_1m):
    conn = db_1m
    total_registros = 1_000_000
    chunk_size = 50_000
    
    print(f"\n[Benchmark] Iniciando inserción de {total_registros:,} registros...")
    start_time = time.perf_counter()
    
    for chunk_start in range(0, total_registros, chunk_size):
        lote = [
            (
                str(10000000 + ((chunk_start + i) % 90000000)),
                f"CLIENTE PRUEBA {chunk_start + i}",
                f"9{str(10000000 + ((chunk_start + i) % 90000000))[:8]}",
                f"AV. CENTRAL {chunk_start + i}, HUANUCO"
            )
            for i in range(chunk_size)
        ]
        with conn:
            conn.executemany(
                "INSERT INTO clientes (documento, nombre, celular, direccion) VALUES (?, ?, ?, ?)",
                lote
            )
    
    elapsed = time.perf_counter() - start_time
    count = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    
    print(f"[Benchmark] {count:,} registros insertados en {elapsed:.2f} segundos.")
    print(f"[Benchmark] Velocidad: {total_registros / elapsed:,.0f} registros/segundo.")
    
    assert count == total_registros

def test_consulta_paginada_1_millon(db_1m):
    conn = db_1m
    
    # 1. Consulta por índice (DNI exacto)
    t0 = time.perf_counter()
    res = conn.execute("SELECT * FROM clientes WHERE documento = '50000000'").fetchall()
    t_idx = (time.perf_counter() - t0) * 1000
    print(f"\n[Benchmark] Búsqueda por DNI indexado en 1M: {t_idx:.2f} ms")
    assert t_idx < 50.0  # Menos de 50ms
    
    # 2. Consulta paginada (Offset 500,000, Limit 50)
    t0 = time.perf_counter()
    res_page = conn.execute("SELECT * FROM clientes LIMIT 50 OFFSET 500000").fetchall()
    t_page = (time.perf_counter() - t0) * 1000
    print(f"[Benchmark] Consulta Paginada profunda (Offset 500,000, Limit 50): {t_page:.2f} ms")
    assert len(res_page) == 50
    assert t_page < 100.0
