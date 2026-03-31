import pandas as pd
import plotly.express as px


def build_chart(df: pd.DataFrame, intent: dict):
    if df is None or df.empty:
        return None

    presentation = intent.get("presentation")
    if presentation != "chart":
        return None

    df = df.copy()
    df.columns = [c.lower() for c in df.columns]

    metric_col = None
    if "total_ventas" in df.columns:
        metric_col = "total_ventas"
    elif "ventas" in df.columns:
        metric_col = "ventas"

    if metric_col is None:
        return None

    # Si solo hay una fila, mejor no graficar
    if len(df) < 2:
        return None

    # Caso 1: lotería vs total
    if "loteria" in df.columns and "anio" not in df.columns and "mes" not in df.columns:
        return px.bar(
            df,
            x="loteria",
            y=metric_col,
            title="Ventas por lotería",
            text_auto=True
        )

    # Caso 2: total por año
    if "anio" in df.columns and "mes" not in df.columns and "loteria" not in df.columns:
        df = df.sort_values(["anio"])
        return px.line(
            df,
            x="anio",
            y=metric_col,
            markers=True,
            title="Ventas por año"
        )

    # Caso 3: evolución mensual general
    if "anio" in df.columns and "mes" in df.columns and "loteria" not in df.columns:
        df = df.sort_values(["anio", "mes"])
        df["periodo"] = df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)
        return px.line(
            df,
            x="periodo",
            y=metric_col,
            markers=True,
            title="Evolución de ventas"
        )

    # Caso 4: evolución mensual por lotería
    if "anio" in df.columns and "mes" in df.columns and "loteria" in df.columns:
        df = df.sort_values(["anio", "mes"])
        df["periodo"] = df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)
        return px.line(
            df,
            x="periodo",
            y=metric_col,
            color="loteria",
            markers=True,
            title="Ventas mensuales por lotería"
        )

    # Caso 5: año y lotería sin mes
    if "anio" in df.columns and "loteria" in df.columns and "mes" not in df.columns:
        df = df.sort_values(["anio"])
        return px.line(
            df,
            x="anio",
            y=metric_col,
            color="loteria",
            markers=True,
            title="Ventas por año y lotería"
        )

    # Fallback
    candidate_x = None
    for col in df.columns:
        if col != metric_col:
            candidate_x = col
            break

    if candidate_x:
        return px.bar(
            df,
            x=candidate_x,
            y=metric_col,
            title="Resultado de ventas"
        )

    return None