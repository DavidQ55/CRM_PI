from database.db import get_conn

conn = get_conn()

try:
    conn.execute("ALTER TABLE clients ADD COLUMN notes TEXT")
    print("Columna notes agregada")
except Exception as e:
    print("Probablemente ya existe:", e)

conn.commit()
conn.close()