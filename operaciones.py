# ------------------------------------------------------------
# operaciones.py - Lógica del torneo
# ------------------------------------------------------------
# Sorteo, carga de partidos, progresión, KDA, acumuladores, rankings,
# búsquedas y alertas. Ninguna función usa input() ni print():
# reciben los datos por parámetro y devuelven resultados.

import random

import validaciones


# ============================================================
# 1) Inscripción de equipos y jugadores
# ============================================================

def nicknames_registrados(jugadores):
    '''Retorna el conjunto de nicknames ya inscriptos.'''
    return {jugadores[codigo]["nickname"] for codigo in jugadores}


def nombres_registrados(equipos):
    '''Retorna el conjunto de nombres de equipo ya inscriptos.'''
    return {equipos[codigo]["nombre_equipo"] for codigo in equipos}


def armar_equipo(nombre, nicknames, equipos, jugadores, config):
    '''Valida en memoria un alta y retorna (equipo, jugadores_nuevos), o lanza ValueError.'''
    validaciones.validar_cantidad_jugadores(nicknames, config)
    nombre_normalizado = validaciones.validar_no_repetido(
        validaciones.validar_nombre(nombre), nombres_registrados(equipos), "un equipo")

    codigo_equipo = "E" + str(len(equipos) + 1)
    registrados = nicknames_registrados(jugadores)
    jugadores_nuevos = []
    siguiente = len(jugadores) + 1
    for nickname in nicknames:
        normalizado = validaciones.validar_no_repetido(
            validaciones.validar_nombre(nickname), registrados, "un jugador")
        registrados.add(normalizado)
        jugadores_nuevos.append({"codigo_jugador": "J" + str(siguiente).zfill(2),
                                 "nickname": normalizado,
                                 "codigo_equipo": codigo_equipo})
        siguiente += 1

    equipo = {"codigo_equipo": codigo_equipo, "nombre_equipo": nombre_normalizado}
    return equipo, jugadores_nuevos


def jugadores_de_equipo(jugadores, codigo_equipo):
    '''Retorna la lista de registros de los jugadores de un equipo.'''
    return [jugadores[codigo] for codigo in jugadores if jugadores[codigo]["codigo_equipo"] == codigo_equipo]


# ============================================================
# 2) Cuadro: sorteo, carga de resultados y progresión
# ============================================================

def sortear_equipos(equipos):
    '''Retorna los códigos de equipo en orden aleatorio.'''
    codigos = list(equipos)
    random.shuffle(codigos)
    return codigos


def crear_partido(id_partido, fase, equipo_a, equipo_b):
    '''Retorna el registro de un partido todavía no jugado.'''
    return {"id_partido": id_partido, "fase": fase, "fecha": "", "equipo_a": equipo_a,
            "equipo_b": equipo_b, "rondas_a": -1, "rondas_b": -1, "jugado": False}


def generar_partidos(codigos, config):
    '''Retorna los 7 partidos: cuartos con los equipos sorteados; semifinales y final sin equipos.'''
    partidos = {}
    id_partido = 1
    for i in range(0, len(codigos), 2):
        fase = validaciones.fase_de_partido(id_partido, config["fases"])
        partidos[id_partido] = crear_partido(id_partido, fase, codigos[i], codigos[i + 1])
        id_partido += 1
    for destino in sorted(config["cuadro"]):
        fase = validaciones.fase_de_partido(destino, config["fases"])
        partidos[destino] = crear_partido(destino, fase, "", "")
    return partidos


def determinar_ganador(partido):
    '''Retorna el código del equipo ganador de un partido jugado.'''
    if partido["rondas_a"] > partido["rondas_b"]:
        return partido["equipo_a"]
    return partido["equipo_b"]


def determinar_perdedor(partido):
    '''Retorna el código del equipo perdedor de un partido jugado.'''
    if partido["rondas_a"] > partido["rondas_b"]:
        return partido["equipo_b"]
    return partido["equipo_a"]


def aplicar_resultado(id_partido, fecha, rondas_a, rondas_b, partidos, cuadro):
    '''Retorna una copia de partidos con el resultado cargado y el ganador en el partido siguiente.'''
    nuevos = {clave: dict(partidos[clave]) for clave in partidos}
    partido = nuevos[id_partido]
    partido["fecha"] = fecha
    partido["rondas_a"] = rondas_a
    partido["rondas_b"] = rondas_b
    partido["jugado"] = True

    ganador = determinar_ganador(partido)
    for destino in cuadro:
        if cuadro[destino][0] == id_partido:
            nuevos[destino]["equipo_a"] = ganador
        elif cuadro[destino][1] == id_partido:
            nuevos[destino]["equipo_b"] = ganador
    return nuevos


def preparar_carga_partido(id_partido, fecha, rondas_a, rondas_b, filas, torneo):
    '''Valida en memoria una carga completa y retorna los partidos actualizados, o lanza ValueError.'''
    config = torneo["config"]
    partidos = torneo["partidos"]
    validaciones.validar_partido_cargable(id_partido, partidos)
    validaciones.validar_marcador(rondas_a, rondas_b, config["rondas_para_ganar"])
    validaciones.validar_fecha(fecha)
    validaciones.validar_orden_fechas(fecha, id_partido, partidos, config["cuadro"])
    nuevos = aplicar_resultado(id_partido, fecha, rondas_a, rondas_b, partidos, config["cuadro"])
    validaciones.validar_planilla(filas, nuevos[id_partido], torneo["jugadores"], torneo["estadisticas"], config)
    return nuevos


def partidos_cargables(partidos):
    '''Retorna los partidos que ya tienen sus dos equipos y todavía no se jugaron.'''
    return [partidos[clave] for clave in partidos
            if not partidos[clave]["jugado"] and partidos[clave]["equipo_a"] != "" and partidos[clave]["equipo_b"] != ""]


def hay_partidos_jugados(partidos):
    '''Indica si al menos un partido tiene su resultado cargado.'''
    return True in [partidos[clave]["jugado"] for clave in partidos]


def obtener_campeon(partidos, cuadro):
    '''Retorna el código del campeón, o "" si la final todavía no se jugó.'''
    id_final = max(cuadro)
    if id_final in partidos and partidos[id_final]["jugado"]:
        return determinar_ganador(partidos[id_final])
    return ""


# ============================================================
# 3) Control de estado del menú
# ============================================================

def motivo_no_disponible(opcion, torneo):
    '''Retorna por qué una opción no está habilitada, o "" si se puede usar.'''
    config = torneo["config"]
    partidos = torneo["partidos"]
    cantidad = len(torneo["equipos"])
    motivo = ""

    if opcion in ("1", "3", "5") and torneo["usuario_actual"]["rol"] != "organizador":
        motivo = "solo para el organizador"
    elif opcion == "1":
        if len(partidos) > 0:
            motivo = "inscripción cerrada"
        elif cantidad >= config["cantidad_equipos"]:
            motivo = "cupo completo"
    elif opcion == "3":
        if len(partidos) > 0:
            motivo = "el cuadro ya fue generado"
        elif cantidad < config["cantidad_equipos"]:
            motivo = f"hay {cantidad} de {config['cantidad_equipos']} equipos"
    elif opcion == "5":
        if len(partidos) == 0:
            motivo = "el cuadro no fue generado"
        elif obtener_campeon(partidos, config["cuadro"]) != "":
            motivo = "el torneo finalizó"
    elif opcion == "7" or opcion == "8":
        if not hay_partidos_jugados(partidos):
            motivo = "no hay partidos jugados"
    elif opcion == "9":
        if len(partidos) == 0:
            motivo = "el cuadro no fue generado"
    return motivo


# ============================================================
# 4) Búsquedas
# ============================================================

def buscar_jugador_recursivo(lista_jugadores, nickname, i=0):
    '''Retorna el registro del jugador con ese nickname, o None si no está. Recursiva.'''
    if i == len(lista_jugadores):
        return None
    elif lista_jugadores[i]["nickname"] == nickname:
        return lista_jugadores[i]
    else:
        return buscar_jugador_recursivo(lista_jugadores, nickname, i + 1)


def buscar_por_codigo(coleccion, codigo):
    '''Retorna el registro con ese código en un diccionario, o None si no está.'''
    if codigo in coleccion:
        return coleccion[codigo]
    return None


# ============================================================
# 5) KDA y acumuladores
# ============================================================

def calcular_kda(bajas, muertes, asistencias):
    '''Retorna (bajas + asistencias) / muertes, o bajas + asistencias si no hubo muertes.'''
    if muertes > 0:
        return (bajas + asistencias) / muertes
    return bajas + asistencias


def es_clutch(kda, umbral_clutch):
    '''Indica si un KDA alcanza el umbral de jugador clutch.'''
    return kda >= umbral_clutch


def acumular_stats_por_jugador(estadisticas):
    '''Retorna {codigo_jugador: {bajas, muertes, asistencias, partidos}} con las sumas del historial.'''
    stats_por_jugador = {}
    for fila in estadisticas:
        codigo = fila["codigo_jugador"]
        if codigo not in stats_por_jugador:
            stats_por_jugador[codigo] = {"bajas": 0, "muertes": 0, "asistencias": 0, "partidos": 0}
        stats_por_jugador[codigo]["bajas"] += fila["bajas"]
        stats_por_jugador[codigo]["muertes"] += fila["muertes"]
        stats_por_jugador[codigo]["asistencias"] += fila["asistencias"]
        stats_por_jugador[codigo]["partidos"] += 1
    return stats_por_jugador


def bajas_por_equipo(estadisticas, jugadores):
    '''Retorna {codigo_equipo: total de bajas} a partir del historial.'''
    totales = {}
    for fila in estadisticas:
        codigo_equipo = jugadores[fila["codigo_jugador"]]["codigo_equipo"]
        if codigo_equipo not in totales:
            totales[codigo_equipo] = 0
        totales[codigo_equipo] += fila["bajas"]
    return totales


def partidos_por_fase(partidos, fases):
    '''Retorna {fase: {jugados, total}} con la cantidad de partidos de cada fase.'''
    resumen = {fase: {"jugados": 0, "total": 0} for fase in fases}
    for clave in partidos:
        resumen[partidos[clave]["fase"]]["total"] += 1
        if partidos[clave]["jugado"]:
            resumen[partidos[clave]["fase"]]["jugados"] += 1
    return resumen


# ============================================================
# 6) Ranking, MVP, equipo más letal e indicadores
# ============================================================

def construir_ranking(jugadores, stats_por_jugador):
    '''Retorna una lista de tuplas (kda, codigo_jugador, nickname, codigo_equipo), de mayor a menor KDA.'''
    ranking = [(calcular_kda(stats_por_jugador[codigo]["bajas"], stats_por_jugador[codigo]["muertes"],
                             stats_por_jugador[codigo]["asistencias"]),
                codigo, jugadores[codigo]["nickname"], jugadores[codigo]["codigo_equipo"])
               for codigo in jugadores if codigo in stats_por_jugador]
    ranking.sort(key=lambda registro: registro[0], reverse=True)
    return ranking


def obtener_top3(ranking):
    '''Retorna los tres primeros del ranking (o los que haya).'''
    return ranking[:3]


def obtener_mvp(ranking):
    '''Retorna los jugadores con el KDA máximo. Si hay empate retorna todos.'''
    if len(ranking) == 0:
        return []
    return [registro for registro in ranking if registro[0] == ranking[0][0]]


def equipos_mas_letales(totales):
    '''Retorna (mejor total, lista de equipos con ese total) a partir de bajas_por_equipo.'''
    if len(totales) == 0:
        return 0, []
    mejor_total = max(totales.values())
    return mejor_total, [codigo for codigo in totales if totales[codigo] == mejor_total]


def promedio_bajas(stats_por_jugador):
    '''Retorna el promedio de bajas por jugador, contando solo a los que jugaron.'''
    if len(stats_por_jugador) == 0:
        return 0
    total = 0
    for codigo in stats_por_jugador:
        total += stats_por_jugador[codigo]["bajas"]
    return total / len(stats_por_jugador)


def contar_kda_superior(ranking, umbral):
    '''Retorna cuántos jugadores tienen un KDA mayor al umbral.'''
    return len([registro for registro in ranking if registro[0] > umbral])


def contar_partidos_jugados(partidos):
    '''Retorna cuántos partidos tienen su resultado cargado.'''
    return len([clave for clave in partidos if partidos[clave]["jugado"]])


def jugadores_con_partidos(estadisticas):
    '''Retorna el conjunto de códigos con al menos una fila en el historial.'''
    return {fila["codigo_jugador"] for fila in estadisticas}


def equipos_eliminados(partidos):
    '''Retorna el conjunto de perdedores de los partidos jugados.'''
    return {determinar_perdedor(partidos[clave]) for clave in partidos if partidos[clave]["jugado"]}


def equipos_con_victoria(partidos):
    '''Retorna el conjunto de ganadores de los partidos jugados.'''
    return {determinar_ganador(partidos[clave]) for clave in partidos if partidos[clave]["jugado"]}


def jugadores_clutch(ranking, umbral_clutch):
    '''Retorna el conjunto de códigos con KDA mayor o igual al umbral clutch.'''
    return {registro[1] for registro in ranking if es_clutch(registro[0], umbral_clutch)}


# ============================================================
# 7) Datos de los reportes
# ============================================================

def reporte_por_equipo(codigo_equipo, torneo):
    '''Retorna los jugadores de un equipo con sus estadísticas y los partidos del equipo.'''
    stats_por_jugador = acumular_stats_por_jugador(torneo["estadisticas"])
    filas = []
    for jugador in jugadores_de_equipo(torneo["jugadores"], codigo_equipo):
        codigo = jugador["codigo_jugador"]
        stats = {"bajas": 0, "muertes": 0, "asistencias": 0, "partidos": 0}
        if codigo in stats_por_jugador:
            stats = stats_por_jugador[codigo]
        filas.append((codigo, jugador["nickname"], stats["bajas"], stats["muertes"], stats["asistencias"],
                      calcular_kda(stats["bajas"], stats["muertes"], stats["asistencias"]), stats["partidos"]))
    partidos = torneo["partidos"]
    del_equipo = [partidos[clave] for clave in partidos
                  if partidos[clave]["equipo_a"] == codigo_equipo or partidos[clave]["equipo_b"] == codigo_equipo]
    return {"equipo": torneo["equipos"][codigo_equipo], "jugadores": filas, "partidos": del_equipo}


def reporte_por_fase(fase, partidos):
    '''Retorna los partidos de una fase.'''
    return [partidos[clave] for clave in partidos if partidos[clave]["fase"] == fase]


def reporte_por_fecha(fecha, torneo):
    '''Retorna una lista de tuplas (partido, mejores KDA) con los partidos jugados en esa fecha.'''
    partidos = torneo["partidos"]
    resultado = []
    for clave in partidos:
        if partidos[clave]["jugado"] and partidos[clave]["fecha"] == fecha:
            filas = [fila for fila in torneo["estadisticas"] if fila["id_partido"] == clave]
            ranking = construir_ranking(torneo["jugadores"], acumular_stats_por_jugador(filas))
            resultado.append((partidos[clave], obtener_mvp(ranking)))
    return resultado


def reporte_general(torneo):
    '''Retorna todos los datos calculados del informe general y del resumen de únicos.'''
    config = torneo["config"]
    partidos = torneo["partidos"]
    estadisticas = torneo["estadisticas"]
    stats_por_jugador = acumular_stats_por_jugador(estadisticas)
    ranking = construir_ranking(torneo["jugadores"], stats_por_jugador)
    mejor_total, letales = equipos_mas_letales(bajas_por_equipo(estadisticas, torneo["jugadores"]))
    return {
        "ranking": ranking,
        "top3": obtener_top3(ranking),
        "mvp": obtener_mvp(ranking),
        "mejor_total": mejor_total,
        "letales": letales,
        "jugados": contar_partidos_jugados(partidos),
        "total_partidos": len(partidos),
        "partidos_por_fase": partidos_por_fase(partidos, config["fases"]),
        "promedio": promedio_bajas(stats_por_jugador),
        "kda_superior": contar_kda_superior(ranking, config["umbral_kda"]),
        "jugadores_con_partidos": jugadores_con_partidos(estadisticas),
        "equipos_con_victoria": equipos_con_victoria(partidos),
        "equipos_eliminados": equipos_eliminados(partidos),
        "jugadores_clutch": jugadores_clutch(ranking, config["umbral_clutch"]),
    }


# ============================================================
# 8) Condiciones críticas (alertas)
# ============================================================

def alertas_de_partido(partido, filas, jugadores, config):
    '''Retorna las alertas A1, A2 y A3 de un partido jugado, como tuplas (código, detalle).'''
    alertas = []
    id_partido = partido["id_partido"]
    rondas = partido["rondas_a"] + partido["rondas_b"]
    equipo_a = partido["equipo_a"]
    equipo_b = partido["equipo_b"]
    bajas = {equipo_a: 0, equipo_b: 0}
    muertes = {equipo_a: 0, equipo_b: 0}

    for fila in filas:
        codigo = fila["codigo_jugador"]
        if fila["muertes"] > rondas:
            alertas.append(("A1", f"Partido {id_partido}: {codigo} tiene {fila['muertes']} muertes en {rondas} rondas"))
        if codigo in jugadores and jugadores[codigo]["codigo_equipo"] in bajas:
            bajas[jugadores[codigo]["codigo_equipo"]] += fila["bajas"]
            muertes[jugadores[codigo]["codigo_equipo"]] += fila["muertes"]

    for equipo, rival in ((equipo_a, equipo_b), (equipo_b, equipo_a)):
        if bajas[equipo] > muertes[rival]:
            alertas.append(("A2", f"Partido {id_partido}: bajas de {equipo} ({bajas[equipo]}) mayores que muertes de {rival} ({muertes[rival]})"))
        elif bajas[equipo] < muertes[rival]:
            alertas.append(("A2", f"Partido {id_partido}: bajas de {equipo} ({bajas[equipo]}) menores que muertes de {rival} ({muertes[rival]})"))

    esperadas = 2 * config["jugadores_por_equipo"]
    if len(filas) != esperadas:
        alertas.append(("A3", f"Partido {id_partido}: tiene {len(filas)} filas de estadísticas y debería tener {esperadas}"))
    return alertas


def detectar_alertas(partidos, jugadores, estadisticas, incidencias, config):
    '''Recorre el historial completo y retorna la lista de alertas (código, detalle).'''
    alertas = []
    for clave in partidos:
        if partidos[clave]["jugado"]:
            filas = [fila for fila in estadisticas if fila["id_partido"] == clave]
            alertas = alertas + alertas_de_partido(partidos[clave], filas, jugadores, config)

    ranking = construir_ranking(jugadores, acumular_stats_por_jugador(estadisticas))
    for registro in ranking:
        if registro[0] < config["umbral_kda_bajo"]:
            alertas.append(("A4", f"{registro[2]} ({registro[1]}) tiene KDA acumulado {registro[0]:.2f}"))

    for incidencia in incidencias:
        alertas.append(("A5", f"{incidencia[0]}, línea {incidencia[1]}: {incidencia[2]}"))
    return alertas
