# ------------------------------------------------------------
# operaciones.py - Logica del torneo
# ------------------------------------------------------------
# Validaciones, busquedas, calculos e informes.
# Ninguna funcion de este modulo usa input() ni print():
# devuelven valores (o mensajes como texto) y main.py se encarga de mostrarlos.

import random


# ============================================================
# 1) Normalizacion y validacion de nombres (punto 5)
# ============================================================

# Deja un texto en su forma normalizada: sin espacios en los costados y en minusculas.
# Se usa ANTES de comparar y ANTES de guardar, para que "Sniper", " sniper " y "SNIPER"
# sean siempre el mismo nombre.
def normalizar_texto(texto):
    return texto.strip().lower()


# Verifica que un texto contenga SOLO letras, numeros y guion bajo.
def solo_caracteres_permitidos(texto):
    for caracter in texto:
        if caracter.isalnum() == False and caracter != "_":
            return False
    return True


# Verifica que el texto tenga al menos una letra
# (descarta nombres compuestos solo por numeros y/o guiones bajos).
def tiene_al_menos_una_letra(texto):
    for caracter in texto:
        if caracter.isalpha():
            return True
    return False


# Valida un nombre de equipo o un nickname de jugador segun el punto 5.
# Devuelve (True, "") si es valido, o (False, mensaje) si no lo es.
def validar_nombre(nombre, longitud_min, longitud_max):
    limpio = normalizar_texto(nombre)

    if limpio == "":
        return False, "El nombre no puede estar vacio ni tener solo espacios."

    if len(limpio) < longitud_min:
        return False, f"El nombre debe tener al menos {longitud_min} caracteres."

    if len(limpio) > longitud_max:
        return False, f"El nombre no puede superar los {longitud_max} caracteres."

    if solo_caracteres_permitidos(limpio) == False:
        return False, "Solo se permiten letras, numeros y guion bajo (sin espacios ni simbolos)."

    if tiene_al_menos_una_letra(limpio) == False:
        return False, "El nombre no puede estar compuesto solo por numeros o guiones bajos."

    return True, ""


# ============================================================
# 2) Inscripcion de equipos y jugadores (puntos 2 a 6)
# ============================================================

# Indica si ya existe un equipo con ese nombre (comparacion normalizada).
def existe_nombre_equipo(equipos, nombre):
    buscado = normalizar_texto(nombre)
    for equipo in equipos:
        if normalizar_texto(equipo[1]) == buscado:
            return True
    return False


# Indica si un nickname ya esta usado por algun jugador ya registrado en el torneo.
def existe_nickname(jugadores, nickname):
    buscado = normalizar_texto(nickname)
    for jugador in jugadores:
        if normalizar_texto(jugador[1]) == buscado:
            return True
    return False


# Indica si un nickname ya fue cargado en la lista temporal del equipo en curso.
def nickname_repetido_en_alta(nicknames_nuevos, nickname):
    buscado = normalizar_texto(nickname)
    for cargado in nicknames_nuevos:
        if normalizar_texto(cargado) == buscado:
            return True
    return False


# Control de estado: indica si se puede dar de alta un equipo nuevo.
# Devuelve (True, "") o (False, motivo).
def se_puede_registrar_equipo(equipos, inscripcion_cerrada, n_equipos):
    if inscripcion_cerrada:
        return False, "La inscripcion esta cerrada: el cuadro del torneo ya fue generado."
    if len(equipos) >= n_equipos:
        return False, f"Ya hay {n_equipos} equipos registrados. No se admiten mas."
    return True, ""


# Agrega la fila de estadisticas de UN jugador nuevo.
# Se llama una vez por cada jugador agregado a la lista jugadores,
# asi la fila i de matriz_stats corresponde siempre al jugador i.
def agregar_fila_stats(matriz_stats, partidos_por_jugador):
    matriz_stats.append([0, 0, 0])   # [bajas, muertes, asistencias] acumuladas
    partidos_por_jugador.append(0)   # cantidad de partidos disputados


# Alta definitiva de un equipo con sus jugadores (punto 6).
# Recibe el nombre y los nicknames YA validados y normalizados por la interfaz.
# Recien aca se tocan las estructuras definitivas: o entra el equipo completo o no entra nada.
# Devuelve (True, mensaje) o (False, motivo).
def registrar_equipo(equipos, jugadores, matriz_stats, partidos_por_jugador,
                     nombre_equipo, nicknames_nuevos, n_jugadores):
    # Control de consistencia interna: exactamente n_jugadores.
    if len(nicknames_nuevos) != n_jugadores:
        return False, f"El equipo debe tener exactamente {n_jugadores} jugadores."

    codigo_equipo = "E" + str(len(equipos) + 1)
    equipos.append((codigo_equipo, normalizar_texto(nombre_equipo)))

    for nickname in nicknames_nuevos:
        codigo_jugador = "J" + str(len(jugadores) + 1).zfill(2)
        jugadores.append((codigo_jugador, normalizar_texto(nickname), codigo_equipo))
        # Cada jugador nuevo recibe su fila de estadisticas en el mismo indice.
        agregar_fila_stats(matriz_stats, partidos_por_jugador)

    return True, f"Equipo {codigo_equipo} registrado con {n_jugadores} jugadores."


# ============================================================
# 3) Cuadro del torneo: sorteo y estructura de partidos (puntos 7 a 9)
# ============================================================

# Agrega un partido al final de TODAS las listas paralelas de una sola vez,
# manteniendo el indice alineado entre ellas.
# El marcador arranca en -1 (no cargado) y jugado en False.
def agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    id_partido, fase, equipoA, equipoB):
    partidos_id.append(id_partido)
    partidos_fase.append(fase)
    partidos_equipoA.append(equipoA)
    partidos_equipoB.append(equipoB)
    partidos_rondasA.append(-1)
    partidos_rondasB.append(-1)
    partidos_jugado.append(False)


# Sortea los equipos una sola vez y arma los 4 cuartos de final.
# Tambien crea las 2 semifinales y la final con participantes desconocidos ("").
# Escribe directamente sobre las listas paralelas (fuente unica de informacion).
def generar_cuadro(equipos, partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                   partidos_rondasA, partidos_rondasB, partidos_jugado, n_equipos, fases):
    # Copia local SOLO de los codigos de equipo, para sortear sin tocar la lista original.
    codigos = [equipo[0] for equipo in equipos]
    random.shuffle(codigos)

    # Partidos 1 a 4: Cuartos de Final, con equipos reales tomados de a pares.
    for i in range(0, n_equipos, 2):
        agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                        partidos_rondasA, partidos_rondasB, partidos_jugado,
                        len(partidos_id) + 1, fases[0], codigos[i], codigos[i + 1])

    # Partidos 5 y 6: Semifinales, participantes desconocidos por ahora.
    agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    len(partidos_id) + 1, fases[1], "", "")
    agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    len(partidos_id) + 1, fases[1], "", "")

    # Partido 7: Final, participantes desconocidos por ahora.
    agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    len(partidos_id) + 1, fases[2], "", "")

    return True


# Control de estado: solo se genera el cuadro con los n_equipos registrados
# y si todavia no se genero.
def se_puede_generar_cuadro(equipos, cuadro_generado, n_equipos):
    if cuadro_generado:
        return False
    if len(equipos) < n_equipos:
        return False
    return True


# Devuelve el INDICE (posicion) del partido cuyo id coincide con id_partido, o -1 si no existe.
def buscar_indice_partido(partidos_id, id_partido):
    for i in range(len(partidos_id)):
        if partidos_id[i] == id_partido:
            return i
    return -1


# ============================================================
# 4) Carga de resultados y progresion del cuadro (puntos 12 a 15)
# ============================================================

# Valida un marcador segun la regla simplificada:
# gana quien llega primero a rondas_para_ganar (13), sin prorroga.
# Valido solo si: ninguno es negativo, exactamente uno vale 13 y el otro es menor a 13.
# Devuelve (True, "") o (False, mensaje).
def validar_marcador(rondas_A, rondas_B, rondas_para_ganar):
    if rondas_A < 0 or rondas_B < 0:
        return False, "Las rondas no pueden ser negativas."

    a_gano = rondas_A == rondas_para_ganar
    b_gano = rondas_B == rondas_para_ganar

    if not a_gano and not b_gano:
        return False, f"Ningun equipo llego a {rondas_para_ganar} rondas: el partido no esta terminado."

    if a_gano and b_gano:
        return False, f"No puede haber empate: ambos no pueden tener {rondas_para_ganar} rondas."

    if a_gano:
        perdedor = rondas_B
    else:
        perdedor = rondas_A

    if perdedor >= rondas_para_ganar:
        return False, f"El perdedor debe tener menos de {rondas_para_ganar} rondas."

    return True, ""


# Valida que un resultado se pueda cargar antes de aceptarlo (punto 14).
# Devuelve (True, indice, "") si es valido, o (False, -1, mensaje) si algo falla.
def validar_carga_partido(partidos_id, partidos_equipoA, partidos_equipoB, partidos_jugado,
                          id_partido, rondas_A, rondas_B, rondas_para_ganar):
    # 1) El partido debe existir.
    indice = buscar_indice_partido(partidos_id, id_partido)
    if indice == -1:
        return False, -1, f"No existe un partido con id {id_partido}."

    # 2) El partido no debe haber sido cargado antes.
    if partidos_jugado[indice]:
        return False, -1, f"El partido {id_partido} ya tiene su resultado cargado."

    # 3) Ambos equipos deben estar definidos (semis y final dependen de partidos previos).
    if partidos_equipoA[indice] == "" or partidos_equipoB[indice] == "":
        return False, -1, f"El partido {id_partido} todavia no tiene definidos sus dos equipos."

    # 4) El marcador debe cumplir la regla del punto 13.
    marcador_ok, mensaje = validar_marcador(rondas_A, rondas_B, rondas_para_ganar)
    if not marcador_ok:
        return False, -1, mensaje

    return True, indice, ""


# Determina automaticamente el codigo del equipo ganador (punto 12).
# Precondicion: el marcador ya fue validado (no hay empate).
def determinar_ganador(partidos_equipoA, partidos_equipoB,
                       partidos_rondasA, partidos_rondasB, indice):
    if partidos_rondasA[indice] > partidos_rondasB[indice]:
        return partidos_equipoA[indice]
    else:
        return partidos_equipoB[indice]


# Coloca al ganador en el partido siguiente que corresponda (punto 15).
# Devuelve el codigo del campeon si se cerro la final, o "" si todavia no.
def avanzar_cuadro(partidos_equipoA, partidos_equipoB, indice, ganador):
    # Ganadores de CUARTOS (indices 0 a 3) van a las SEMIFINALES (4 y 5)
    if indice == 0:
        partidos_equipoA[4] = ganador   # ganador del cuarto 1 -> Semifinal 1, lado A
    elif indice == 1:
        partidos_equipoB[4] = ganador   # ganador del cuarto 2 -> Semifinal 1, lado B
    elif indice == 2:
        partidos_equipoA[5] = ganador   # ganador del cuarto 3 -> Semifinal 2, lado A
    elif indice == 3:
        partidos_equipoB[5] = ganador   # ganador del cuarto 4 -> Semifinal 2, lado B
    # Ganadores de SEMIFINALES (indices 4 y 5) van a la FINAL (6)
    elif indice == 4:
        partidos_equipoA[6] = ganador   # ganador de Semifinal 1 -> Final, lado A
    elif indice == 5:
        partidos_equipoB[6] = ganador   # ganador de Semifinal 2 -> Final, lado B
    # Ganador de la FINAL (indice 6) es el campeon
    elif indice == 6:
        return ganador

    return ""


# Carga el resultado de un partido: valida, escribe el marcador, marca jugado,
# determina el ganador y avanza el cuadro.
# Devuelve (True, mensaje, campeon) o (False, mensaje, "").
def cargar_resultado(partidos_id, partidos_equipoA, partidos_equipoB,
                     partidos_rondasA, partidos_rondasB, partidos_jugado,
                     id_partido, rondas_A, rondas_B, rondas_para_ganar):
    # 1) Validar todo antes de tocar nada.
    es_valido, indice, mensaje = validar_carga_partido(
        partidos_id, partidos_equipoA, partidos_equipoB, partidos_jugado,
        id_partido, rondas_A, rondas_B, rondas_para_ganar)
    if not es_valido:
        return False, mensaje, ""

    # 2) Escribir el marcador en la posicion del partido.
    partidos_rondasA[indice] = rondas_A
    partidos_rondasB[indice] = rondas_B

    # 3) Marcar el partido como ya jugado.
    partidos_jugado[indice] = True

    # 4) Determinar automaticamente el ganador.
    ganador = determinar_ganador(partidos_equipoA, partidos_equipoB,
                                 partidos_rondasA, partidos_rondasB, indice)

    # 5) Avanzar el cuadro. Si se cerro la final, devuelve el campeon.
    campeon = avanzar_cuadro(partidos_equipoA, partidos_equipoB, indice, ganador)

    return True, f"Resultado del partido {id_partido} cargado. Ganador: {ganador}.", campeon


# Indica si ya se cargo al menos un partido (bloquea rankings e informes sin datos).
def hay_partidos_jugados(partidos_jugado):
    for jugado in partidos_jugado:
        if jugado:
            return True
    return False


# ============================================================
# 5) Busquedas (punto 22)
# ============================================================

# Devuelve el INDICE del equipo cuyo codigo coincide (comparacion normalizada), o -1.
def buscar_indice_equipo(equipos, codigo_buscado):
    buscado = normalizar_texto(codigo_buscado)
    for i in range(len(equipos)):
        if normalizar_texto(equipos[i][0]) == buscado:
            return i
    return -1


# Devuelve el INDICE del jugador cuyo codigo O nickname coincide (normalizado), o -1.
def buscar_indice_jugador(jugadores, texto_buscado):
    buscado = normalizar_texto(texto_buscado)
    for i in range(len(jugadores)):
        codigo = normalizar_texto(jugadores[i][0])
        nickname = normalizar_texto(jugadores[i][1])
        if codigo == buscado or nickname == buscado:
            return i
    return -1


# Devuelve una LISTA DE INDICES de los jugadores que pertenecen a un equipo.
def indices_de_equipo(jugadores, codigo_equipo):
    indices = []
    for i in range(len(jugadores)):
        if jugadores[i][2] == codigo_equipo:
            indices.append(i)
    return indices


# Devuelve una LISTA DE INDICES de los partidos donde aparece un equipo (como A o como B).
def indices_partidos_de_equipo(partidos_equipoA, partidos_equipoB, codigo_equipo):
    indices = []
    for i in range(len(partidos_equipoA)):
        if partidos_equipoA[i] == codigo_equipo or partidos_equipoB[i] == codigo_equipo:
            indices.append(i)
    return indices


# ============================================================
# 6) Estadisticas y KDA (puntos 10, 11, 16, 21)
# ============================================================
# Orden fijo de columnas de matriz_stats: 0 = bajas, 1 = muertes, 2 = asistencias.
# Ese orden se resuelve solo en estas dos funciones; el resto del programa las reutiliza.

# Devuelve las estadisticas acumuladas de un jugador como (bajas, muertes, asistencias).
def obtener_stats(matriz_stats, indice):
    fila = matriz_stats[indice]
    return fila[0], fila[1], fila[2]


# SUMA las estadisticas de un partido a lo acumulado del jugador (no reemplaza)
# y registra que disputo un partido mas.
def acumular_stats(matriz_stats, partidos_por_jugador, indice, bajas, muertes, asistencias):
    matriz_stats[indice][0] = matriz_stats[indice][0] + bajas
    matriz_stats[indice][1] = matriz_stats[indice][1] + muertes
    matriz_stats[indice][2] = matriz_stats[indice][2] + asistencias
    partidos_por_jugador[indice] = partidos_por_jugador[indice] + 1


# KDA = (bajas + asistencias) / muertes   si muertes > 0
# KDA = bajas + asistencias               si muertes == 0
def calcular_kda(matriz_stats, indice):
    bajas, muertes, asistencias = obtener_stats(matriz_stats, indice)
    if muertes > 0:
        return (bajas + asistencias) / muertes
    else:
        return bajas + asistencias


# Indica si el jugador disputo al menos un partido.
def jugo_algun_partido(partidos_por_jugador, indice):
    return partidos_por_jugador[indice] > 0


# Jugador clutch: KDA acumulado mayor o igual al umbral configurado.
def es_clutch(kda, umbral_clutch):
    return kda >= umbral_clutch


# ============================================================
# 7) Ranking, MVP y equipo mas letal (puntos 17, 18, 23)
# ============================================================

# Construye el ranking de jugadores por KDA, de mayor a menor.
# Solo incluye a los que disputaron al menos un partido.
# Cada registro es una TUPLA fija: (kda, codigo_jugador, nickname, codigo_equipo).
def construir_ranking(jugadores, matriz_stats, partidos_por_jugador):
    # COMPRENSION: lista de KDA de todos los jugadores (mismo indice que jugadores).
    kdas = [calcular_kda(matriz_stats, i) for i in range(len(jugadores))]

    ranking = []
    for i in range(len(jugadores)):
        if jugo_algun_partido(partidos_por_jugador, i):
            ranking.append((kdas[i], jugadores[i][0], jugadores[i][1], jugadores[i][2]))

    # LAMBDA: ordena por el KDA (posicion 0 de cada tupla), de mayor a menor.
    ranking.sort(key=lambda registro: registro[0], reverse=True)
    return ranking


# SLICING: los tres primeros del ranking (si hay menos de 3, devuelve los que haya).
def obtener_top3(ranking):
    return ranking[:3]


# MVP: jugador(es) con el KDA maximo. Si hay empate se devuelven todos.
# Como el ranking ya esta ordenado, el maximo esta en la posicion 0.
def obtener_mvp(ranking):
    if len(ranking) == 0:
        return []
    kda_maximo = ranking[0][0]
    return [registro for registro in ranking if registro[0] == kda_maximo]


# Total de bajas acumuladas por los jugadores de un equipo.
def bajas_de_equipo(jugadores, matriz_stats, codigo_equipo):
    total = 0
    for i in indices_de_equipo(jugadores, codigo_equipo):
        bajas, muertes, asistencias = obtener_stats(matriz_stats, i)
        total = total + bajas
    return total


# Equipo(s) mas letal(es): los que acumulan mas bajas. Contempla empates.
# Devuelve (mejor_total, lista de tuplas de equipo empatadas).
def obtener_equipos_mas_letales(equipos, jugadores, matriz_stats):
    mejor_total = -1
    empatados = []
    for equipo in equipos:
        total = bajas_de_equipo(jugadores, matriz_stats, equipo[0])
        if total > mejor_total:
            mejor_total = total
            empatados = [equipo]
        elif total == mejor_total:
            empatados.append(equipo)
    return mejor_total, empatados


# ============================================================
# 8) Indicadores del resumen general (puntos 19, 20, informe 6)
# ============================================================

# Promedio de bajas por jugador, contando solo a los que jugaron al menos un partido.
def promedio_bajas_por_jugador(matriz_stats, partidos_por_jugador):
    total_bajas = 0
    cantidad = 0
    for i in range(len(matriz_stats)):
        if jugo_algun_partido(partidos_por_jugador, i):
            bajas, muertes, asistencias = obtener_stats(matriz_stats, i)
            total_bajas = total_bajas + bajas
            cantidad = cantidad + 1

    if cantidad == 0:   # evita dividir por cero si nadie jugo
        return 0.0
    return total_bajas / cantidad


# Cantidad de jugadores (que jugaron) con KDA superior al umbral configurado.
def contar_kda_superior(matriz_stats, partidos_por_jugador, umbral):
    cantidad = 0
    for i in range(len(matriz_stats)):
        if jugo_algun_partido(partidos_por_jugador, i):
            if calcular_kda(matriz_stats, i) > umbral:
                cantidad = cantidad + 1
    return cantidad


# Cuenta cuantos partidos ya tienen resultado cargado.
def contar_partidos_jugados(partidos_jugado):
    cantidad = 0
    for jugado in partidos_jugado:
        if jugado:
            cantidad = cantidad + 1
    return cantidad


# Devuelve la lista de codigos de equipos que ya perdieron un partido (eliminados).
def equipos_eliminados(partidos_equipoA, partidos_equipoB,
                       partidos_rondasA, partidos_rondasB, partidos_jugado):
    eliminados = []
    for i in range(len(partidos_jugado)):
        if partidos_jugado[i]:
            if partidos_rondasA[i] > partidos_rondasB[i]:
                perdedor = partidos_equipoB[i]
            else:
                perdedor = partidos_equipoA[i]
            eliminados.append(perdedor)
    return eliminados