def generate_sql(intent: dict) -> str:
    task = intent.get("task", "aggregate_sales")
    dimensions = intent.get("dimensions", [])
    filters = intent.get("filters", {})
    aggregation = intent.get("aggregation", "sum")
    metric = intent.get("metric", "ventas")
    sort = intent.get("sort", [])
    limit = intent.get("limit")
    presentation = intent.get("presentation", "table")

    if task != "aggregate_sales":
        raise ValueError("Task no soportada")

    anio = filters.get("anio")
    mes = filters.get("mes")
    loterias = filters.get("loterias", [])

    # Ajustes para gráficos
    if presentation == "chart" and anio is not None and len(loterias) == 1:
        dimensions = ["anio", "mes", "loteria"]

    if presentation == "chart" and anio is not None and len(loterias) > 1:
        dimensions = ["anio", "mes", "loteria"]

    where_clauses = []

    if anio is not None:
        where_clauses.append(f"anio = {int(anio)}")

    if mes is not None:
        where_clauses.append(f"mes = {int(mes)}")

    if loterias:
        loteria_conditions = []
        for loteria in loterias:
            safe_loteria = str(loteria).replace("'", "''")
            loteria_conditions.append(
                f"public.unaccent(loteria) ILIKE public.unaccent('%{safe_loteria}%')"
            )
        where_clauses.append("(" + " OR ".join(loteria_conditions) + ")")

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    valid_dimensions = [d for d in dimensions if d in ["anio", "mes", "loteria"]]

    agg_sql = "SUM(ventas) AS total_ventas"

    if valid_dimensions:
        select_sql = ", ".join(valid_dimensions) + ", " + agg_sql
    else:
        select_sql = agg_sql

    sql = f"SELECT {select_sql}\nFROM ventas_loteria"

    if where_sql:
        sql += f"\n{where_sql}"

    if valid_dimensions:
        sql += f"\nGROUP BY {', '.join(valid_dimensions)}"

    order_clauses = []

    # Regla principal: si es gráfico temporal, ordenar por tiempo
    if presentation == "chart":
        if "anio" in valid_dimensions and "mes" in valid_dimensions and "loteria" in valid_dimensions:
            order_clauses = ["anio ASC", "mes ASC", "loteria ASC"]
        elif "anio" in valid_dimensions and "mes" in valid_dimensions:
            order_clauses = ["anio ASC", "mes ASC"]
        elif "anio" in valid_dimensions:
            order_clauses = ["anio ASC"]
        elif "loteria" in valid_dimensions:
            order_clauses = ["total_ventas DESC"]

    # Si no se definió arriba, usar sort del intent
    if not order_clauses and sort:
        for item in sort:
            field = item.get("field")
            direction = str(item.get("direction", "asc")).upper()

            if direction not in ["ASC", "DESC"]:
                direction = "ASC"

            allowed_fields = ["anio", "mes", "loteria", "total_ventas"]
            if field in allowed_fields:
                order_clauses.append(f"{field} {direction}")

    # Fallback
    if not order_clauses:
        if "anio" in valid_dimensions and "mes" in valid_dimensions:
            order_clauses = ["anio ASC", "mes ASC"]
        elif "anio" in valid_dimensions:
            order_clauses = ["anio ASC"]
        elif "loteria" in valid_dimensions:
            order_clauses = ["total_ventas DESC"]
        else:
            order_clauses = ["total_ventas DESC"]

    sql += "\nORDER BY " + ", ".join(order_clauses)

    if limit is not None:
        sql += f"\nLIMIT {int(limit)}"

    sql += ";"

    return sql