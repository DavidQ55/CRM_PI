from database.db import get_conn

def get_dashboard_metrics(start_date=None, end_date=None):
    conn = get_conn()

    if start_date and end_date:
        if start_date > end_date:
            return {
                "error": "La fecha inicial no puede ser mayor a la final"
            }

    query = """
        SELECT DISTINCT c.id, c.segment
        FROM clients c
        LEFT JOIN purchases p ON c.id = p.client_id
    """

    params = []

    if start_date and end_date:
        query += " WHERE date(p.date) BETWEEN date(?) AND date(?)"
        params.extend([start_date, end_date])

    rows = conn.execute(query, params).fetchall()

    total = len(rows)

    segments = {
        "General": 0,
        "Frecuente": 0,
        "VIP": 0
    }

    for row in rows:
        if row["segment"] in segments:
            segments[row["segment"]] += 1

    top_query = """
        SELECT c.name, COUNT(p.id) as total
        FROM clients c
        LEFT JOIN purchases p ON c.id = p.client_id
    """

    if start_date and end_date:
        top_query += """
            WHERE date(p.date)
            BETWEEN date(?) AND date(?)
        """

    top_query += """
        GROUP BY c.id
        ORDER BY total DESC
        LIMIT 5
    """

    top_clients = conn.execute(top_query, params).fetchall()

    return {
        "total_clients": total,
        "segments": segments,
        "top_clients": [dict(x) for x in top_clients]
    }