def build_natural_response(intent: dict, row_count: int = 0) -> str:
    filters = intent.get("filters", {})
    presentation = intent.get("presentation", "table")
    loterias = filters.get("loterias", [])

    if row_count == 0:
        return "No encontré resultados para esa consulta."

    intro = {
        "chart": "Listo, preparé la visualización con los datos encontrados.",
        "file": "Listo, preparé el resultado y también te lo dejo disponible para descargar.",
        "text": "Encontré el resultado solicitado.",
        "table": "Aquí tienes el resultado de tu consulta."
    }.get(presentation, "Aquí tienes el resultado de tu consulta.")

    details = []

    if filters.get("anio") is not None:
        details.append(f"año {filters['anio']}")

    if filters.get("mes") is not None:
        details.append(f"mes {filters['mes']}")

    if loterias:
        if len(loterias) == 1:
            details.append(f"lotería {loterias[0]}")
        else:
            details.append("loterías " + ", ".join(loterias))

    if details:
        return f"{intro} Apliqué filtro por {' y '.join(details)}."

    return intro