# ------------------------------------------------------------
# reportes.py - Arma las líneas de texto de cada informe
# ------------------------------------------------------------
# Reciben los datos ya calculados y devuelven una lista de líneas.
# main.py las muestra y archivos.py las escribe.

import operaciones


# ============================================================
# 1) Utilidades
# ============================================================

def encabezado_reporte(nombre_torneo, tipo, filtro):
    '''Retorna las líneas iniciales de un archivo de reporte.'''
    return [f"Torneo: {nombre_torneo}", f"Reporte: {tipo}", f"Filtro: {filtro}", ""]


def texto_equipo(codigo, equipos):
    '''Retorna "nombre (código)" de un equipo, o "por definir" si todavía no se conoce.'''
    if codigo == "":
        return "por definir"
    return f"{equipos[codigo]['nombre_equipo']} ({codigo})"


def texto_partido(partido, equipos):
    '''Retorna el cruce, la fecha, el marcador y el ganador de un partido, o "pendiente".'''
    cruce = f"Partido {partido['id_partido']} ({partido['fase']}): {texto_equipo(partido['equipo_a'], equipos)} vs {texto_equipo(partido['equipo_b'], equipos)}"
    if partido["jugado"]:
        ganador = texto_equipo(operaciones.determinar_ganador(partido), equipos)
        return f"{cruce} | {partido['fecha']} | {partido['rondas_a']} - {partido['rondas_b']} | Ganador: {ganador}"
    return f"{cruce} | pendiente"


def texto_conjunto(conjunto):
    '''Retorna la cantidad y el listado ordenado de un conjunto.'''
    if len(conjunto) == 0:
        return "0"
    return f"{len(conjunto)} ({', '.join(sorted(conjunto))})"


# ============================================================
# 2) Listados y fichas
# ============================================================

def lineas_equipos_y_jugadores(equipos, jugadores):
    '''Retorna el listado de equipos con sus jugadores.'''
    lineas = ["----- EQUIPOS Y JUGADORES -----"]
    if len(equipos) == 0:
        lineas.append("Todavía no hay equipos registrados.")
    for codigo in equipos:
        lineas.append(texto_equipo(codigo, equipos))
        for jugador in operaciones.jugadores_de_equipo(jugadores, codigo):
            lineas.append(f"   {jugador['codigo_jugador']}: {jugador['nickname']}")
    lineas.append(f"Total: {len(equipos)} equipos y {len(jugadores)} jugadores.")
    return lineas


def lineas_ficha_jugador(jugador, stats_por_jugador, equipos, umbral_clutch):
    '''Retorna la ficha de un jugador encontrado por una búsqueda.'''
    codigo = jugador["codigo_jugador"]
    lineas = [f"----- JUGADOR {codigo}: {jugador['nickname']} -----",
              f"Equipo: {texto_equipo(jugador['codigo_equipo'], equipos)}"]
    if codigo in stats_por_jugador:
        stats = stats_por_jugador[codigo]
        kda = operaciones.calcular_kda(stats["bajas"], stats["muertes"], stats["asistencias"])
        lineas.append(f"Partidos jugados: {stats['partidos']}")
        lineas.append(f"Bajas: {stats['bajas']} | Muertes: {stats['muertes']} | Asistencias: {stats['asistencias']}")
        lineas.append(f"KDA acumulado: {kda:.2f}")
        if operaciones.es_clutch(kda, umbral_clutch):
            lineas.append(f"Condición: JUGADOR CLUTCH (KDA >= {umbral_clutch})")
    else:
        lineas.append("Todavía no jugó ningún partido.")
    return lineas


def lineas_datos_equipo(datos, equipos):
    '''Retorna los jugadores de un equipo con sus estadísticas y los partidos del equipo.'''
    equipo = datos["equipo"]
    lineas = [f"----- EQUIPO {equipo['codigo_equipo']}: {equipo['nombre_equipo']} -----", "Jugadores:"]
    for fila in datos["jugadores"]:
        lineas.append(f"  {fila[0]} {fila[1]}: bajas {fila[2]}, muertes {fila[3]}, asistencias {fila[4]}, KDA {fila[5]:.2f}, partidos {fila[6]}")
    lineas.append("Partidos:")
    if len(datos["partidos"]) == 0:
        lineas.append("  Todavía no aparece en ningún partido.")
    for partido in datos["partidos"]:
        lineas.append("  " + texto_partido(partido, equipos))
    return lineas


# ============================================================
# 3) Informes de la etapa 1
# ============================================================

def lineas_cuadro(partidos, equipos, campeon):
    '''Informe 1: estado completo del cuadro.'''
    lineas = ["----- CUADRO DEL TORNEO -----"]
    if len(partidos) == 0:
        lineas.append("Todavía no se generó el cuadro.")
    for clave in partidos:
        lineas.append(texto_partido(partidos[clave], equipos))
    if campeon != "":
        lineas.append(f"Campeón del torneo: {texto_equipo(campeon, equipos)}")
    return lineas


def lineas_ranking(ranking, clutch):
    '''Informe 2: ranking completo por KDA, marcando a los jugadores clutch.'''
    lineas = ["----- RANKING DE JUGADORES POR KDA -----"]
    if len(ranking) == 0:
        lineas.append("Todavía no hay partidos jugados.")
    posicion = 1
    for registro in ranking:
        marca = ""
        if registro[1] in clutch:
            marca = "  [CLUTCH]"
        lineas.append(f"{posicion}. {registro[2]} ({registro[1]}) - equipo {registro[3]} - KDA: {registro[0]:.2f}{marca}")
        posicion += 1
    return lineas


def lineas_top3(top3):
    '''Informe 3: Top 3 por KDA.'''
    lineas = ["----- TOP 3 DE JUGADORES POR KDA -----"]
    if len(top3) == 0:
        lineas.append("Todavía no hay partidos jugados.")
    posicion = 1
    for registro in top3:
        lineas.append(f"{posicion}. {registro[2]} ({registro[1]}) - KDA: {registro[0]:.2f}")
        posicion += 1
    return lineas


def lineas_mvp(mvp):
    '''Informe 4: MVP del torneo, con empates.'''
    lineas = ["----- MVP DEL TORNEO -----"]
    if len(mvp) == 0:
        lineas.append("Todavía no hay partidos jugados.")
    elif len(mvp) > 1:
        lineas.append(f"Hay {len(mvp)} jugadores empatados con KDA {mvp[0][0]:.2f}:")
    for registro in mvp:
        lineas.append(f"{registro[2]} ({registro[1]}) - equipo {registro[3]} - KDA: {registro[0]:.2f}")
    return lineas


def lineas_mas_letal(mejor_total, letales, equipos):
    '''Informe 5: equipo más letal, con empates.'''
    lineas = ["----- EQUIPO MÁS LETAL -----"]
    if len(letales) == 0:
        lineas.append("Todavía no hay bajas cargadas.")
    for codigo in letales:
        lineas.append(f"{texto_equipo(codigo, equipos)} con {mejor_total} bajas")
    return lineas


def lineas_resumen(datos, equipos, umbral_kda):
    '''Informe 6: resumen general del torneo.'''
    lineas = ["----- RESUMEN GENERAL DEL TORNEO -----",
              f"Partidos jugados: {datos['jugados']} de {datos['total_partidos']}"]
    for fase in datos["partidos_por_fase"]:
        por_fase = datos["partidos_por_fase"][fase]
        lineas.append(f"  {fase}: {por_fase['jugados']} de {por_fase['total']}")
    lineas.append(f"Equipos eliminados: {len(datos['equipos_eliminados'])}")
    for codigo in sorted(datos["equipos_eliminados"]):
        lineas.append(f"  {texto_equipo(codigo, equipos)}")
    lineas.append(f"Promedio de bajas por jugador: {datos['promedio']:.2f}")
    lineas.append(f"Jugadores con KDA mayor a {umbral_kda}: {datos['kda_superior']}")
    lineas.append(f"Jugadores clutch: {len(datos['jugadores_clutch'])}")
    return lineas


def lineas_unicos(datos):
    '''Resumen de únicos: cantidad y listado de cada conjunto.'''
    return ["----- RESUMEN DE ÚNICOS -----",
            f"Jugadores distintos que jugaron: {texto_conjunto(datos['jugadores_con_partidos'])}",
            f"Equipos con al menos una victoria: {texto_conjunto(datos['equipos_con_victoria'])}",
            f"Equipos eliminados: {texto_conjunto(datos['equipos_eliminados'])}",
            f"Jugadores clutch: {texto_conjunto(datos['jugadores_clutch'])}"]


def lineas_rankings(datos):
    '''Retorna el ranking completo y el Top 3 (opción 7 del menú).'''
    return lineas_ranking(datos["ranking"], datos["jugadores_clutch"]) + [""] + lineas_top3(datos["top3"])


def lineas_informes(datos, equipos, umbral_kda):
    '''Retorna MVP, equipo más letal, resumen y únicos (opción 8 del menú).'''
    return (lineas_mvp(datos["mvp"]) + [""]
            + lineas_mas_letal(datos["mejor_total"], datos["letales"], equipos) + [""]
            + lineas_resumen(datos, equipos, umbral_kda) + [""]
            + lineas_unicos(datos))


# ============================================================
# 4) Reportes que se escriben en archivos
# ============================================================

def lineas_reporte_general(nombre_torneo, datos, partidos, equipos, campeon, umbral_kda):
    '''Retorna el contenido completo de reporte_general.txt.'''
    return (encabezado_reporte(nombre_torneo, "General", "ninguno")
            + lineas_cuadro(partidos, equipos, campeon) + [""]
            + lineas_rankings(datos) + [""]
            + lineas_informes(datos, equipos, umbral_kda))


def lineas_reporte_equipo(nombre_torneo, datos, equipos):
    '''Retorna el contenido de reporte_filtrado.txt para el filtro por equipo.'''
    filtro = f"equipo {datos['equipo']['codigo_equipo']}"
    return encabezado_reporte(nombre_torneo, "Filtrado por equipo", filtro) + lineas_datos_equipo(datos, equipos)


def lineas_reporte_fase(nombre_torneo, fase, partidos_fase, equipos):
    '''Retorna el contenido de reporte_filtrado.txt para el filtro por fase.'''
    lineas = encabezado_reporte(nombre_torneo, "Filtrado por fase", f"fase {fase}")
    if len(partidos_fase) == 0:
        lineas.append("No hay partidos en esa fase.")
    for partido in partidos_fase:
        lineas.append(texto_partido(partido, equipos))
    return lineas


def lineas_reporte_fecha(nombre_torneo, fecha, resultados, equipos):
    '''Retorna el contenido de reporte_filtrado.txt para el filtro por fecha.'''
    lineas = encabezado_reporte(nombre_torneo, "Filtrado por fecha", f"fecha {fecha}")
    if len(resultados) == 0:
        lineas.append("No hay partidos jugados en esa fecha.")
    for partido, mejores in resultados:
        lineas.append(texto_partido(partido, equipos))
        if len(mejores) == 0:
            lineas.append("  Mejor KDA: sin estadísticas cargadas")
        for registro in mejores:
            lineas.append(f"  Mejor KDA: {registro[2]} ({registro[1]}) con {registro[0]:.2f}")
    return lineas


def lineas_alertas(nombre_torneo, alertas):
    '''Retorna el contenido de alertas.txt, con las alertas agrupadas por código.'''
    titulos = (("A1", "Jugador con más muertes que rondas"),
               ("A2", "Bajas de un equipo distintas de las muertes del rival"),
               ("A3", "Partido jugado sin sus filas de estadísticas completas"),
               ("A4", "Jugador con bajo rendimiento"),
               ("A5", "Filas descartadas al leer los CSV"))
    lineas = encabezado_reporte(nombre_torneo, "Alertas", "ninguno")
    if len(alertas) == 0:
        lineas.append("No se detectaron alertas.")
    for codigo, titulo in titulos:
        detalles = [alerta[1] for alerta in alertas if alerta[0] == codigo]
        if len(detalles) > 0:
            lineas.append(f"{codigo} - {titulo} ({len(detalles)}):")
            for detalle in detalles:
                lineas.append(f"  {detalle}")
    return lineas
