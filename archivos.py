# ------------------------------------------------------------
# archivos.py - Lectura y escritura de JSON, CSV y TXT
# ------------------------------------------------------------
# También decide si la combinación y el contenido de los archivos
# permiten reconstruir el torneo. No usa input() ni print().

import json

import operaciones
import validaciones


# ============================================================
# 1) Configuración y utilidades de lectura
# ============================================================

def leer_configuracion(ruta):
    '''Retorna el contenido de configuracion.json como diccionario, o lanza ValueError si no es JSON válido.'''
    with open(ruta, "rt", encoding="utf-8") as arch:
        texto = arch.read()
    try:
        return json.loads(texto)
    except ValueError:
        raise ValueError(f"El archivo {ruta} no tiene formato JSON válido")


def encabezados():
    '''Retorna el encabezado esperado de cada CSV.'''
    return {
        "usuarios": "usuario;clave;rol",
        "equipos": "codigo_equipo;nombre_equipo",
        "jugadores": "codigo_jugador;nickname;codigo_equipo",
        "partidos": "id_partido;fase;fecha;equipo_a;equipo_b;rondas_a;rondas_b;jugado",
        "estadisticas": "id_partido;codigo_jugador;bajas;muertes;asistencias",
    }


def leer_filas(ruta, encabezado):
    '''Retorna una lista de tuplas (número de línea, campos), o lanza ValueError si el encabezado no coincide.'''
    filas = []
    with open(ruta, "rt", encoding="utf-8") as arch:
        primera = arch.readline().rstrip("\n")
        if primera != encabezado:
            raise ValueError(f"El encabezado de {ruta} debe ser '{encabezado}'")
        numero_linea = 1
        for linea in arch:
            numero_linea += 1
            filas.append((numero_linea, linea.rstrip("\n").split(";")))
    return filas


def validar_cantidad_campos(campos, cantidad):
    '''Lanza ValueError si la fila no tiene la cantidad de campos esperada.'''
    if len(campos) != cantidad:
        raise ValueError(f"Debe tener {cantidad} campos y tiene {len(campos)}")


# ============================================================
# 2) Lectura de cada CSV
# ============================================================

def leer_usuarios(ruta):
    '''Retorna (usuarios, incidencias), o lanza ValueError si no hay ninguna fila válida.'''
    usuarios = {}
    incidencias = []
    for numero_linea, campos in leer_filas(ruta, encabezados()["usuarios"]):
        try:
            validar_cantidad_campos(campos, 3)
            usuario = validaciones.validar_no_repetido(validaciones.validar_usuario(campos[0]), usuarios, "un usuario")
            usuarios[usuario] = {"clave": validaciones.validar_clave(campos[1]), "rol": validaciones.validar_rol(campos[2])}
        except ValueError as error:
            incidencias.append((ruta, numero_linea, str(error)))
    if len(usuarios) == 0:
        raise ValueError(f"El archivo {ruta} no tiene usuarios válidos")
    return usuarios, incidencias


def leer_equipos(ruta, config):
    '''Retorna (equipos, incidencias). Las filas inválidas o repetidas se descartan.'''
    equipos = {}
    nombres = set()
    incidencias = []
    for numero_linea, campos in leer_filas(ruta, encabezados()["equipos"]):
        try:
            validar_cantidad_campos(campos, 2)
            codigo = validaciones.validar_no_repetido(validaciones.validar_codigo_equipo(campos[0], config), equipos, "un equipo")
            nombre = validaciones.validar_no_repetido(validaciones.validar_nombre(campos[1]), nombres, "un equipo")
            nombres.add(nombre)
            equipos[codigo] = {"codigo_equipo": codigo, "nombre_equipo": nombre}
        except ValueError as error:
            incidencias.append((ruta, numero_linea, str(error)))
    return equipos, incidencias


def leer_jugadores(ruta, config):
    '''Retorna (jugadores, incidencias). Las filas inválidas o repetidas se descartan.'''
    jugadores = {}
    nicknames = set()
    incidencias = []
    for numero_linea, campos in leer_filas(ruta, encabezados()["jugadores"]):
        try:
            validar_cantidad_campos(campos, 3)
            codigo = validaciones.validar_no_repetido(validaciones.validar_codigo_jugador(campos[0], config), jugadores, "un jugador")
            nickname = validaciones.validar_no_repetido(validaciones.validar_nombre(campos[1]), nicknames, "un jugador")
            codigo_equipo = validaciones.validar_codigo_equipo(campos[2], config)
            nicknames.add(nickname)
            jugadores[codigo] = {"codigo_jugador": codigo, "nickname": nickname, "codigo_equipo": codigo_equipo}
        except ValueError as error:
            incidencias.append((ruta, numero_linea, str(error)))
    return jugadores, incidencias


def convertir_partido(campos, config):
    '''Retorna el registro de partido de una fila ya separada, o lanza ValueError.'''
    validar_cantidad_campos(campos, 8)
    id_partido = validaciones.validar_entero_no_negativo(campos[0])
    if id_partido < 1 or id_partido > 7:
        raise ValueError("El id de partido debe estar entre 1 y 7")
    if campos[1] != validaciones.fase_de_partido(id_partido, config["fases"]):
        raise ValueError(f"La fase '{campos[1]}' no corresponde al partido {id_partido}")
    for codigo in (campos[3], campos[4]):
        if codigo != "":
            validaciones.validar_codigo_equipo(codigo, config)

    if campos[7] == "si":
        rondas_a = validaciones.validar_entero_no_negativo(campos[5])
        rondas_b = validaciones.validar_entero_no_negativo(campos[6])
        validaciones.validar_marcador(rondas_a, rondas_b, config["rondas_para_ganar"])
        validaciones.validar_fecha(campos[2])
        if campos[3] == "" or campos[4] == "":
            raise ValueError("Un partido jugado debe tener sus dos equipos")
    elif campos[7] == "no":
        rondas_a = -1
        rondas_b = -1
        if campos[2] != "" or campos[5] != "-1" or campos[6] != "-1":
            raise ValueError("Un partido no jugado debe tener fecha vacía y rondas en -1")
    else:
        raise ValueError("El campo jugado debe ser si o no")

    return {"id_partido": id_partido, "fase": campos[1], "fecha": campos[2], "equipo_a": campos[3],
            "equipo_b": campos[4], "rondas_a": rondas_a, "rondas_b": rondas_b, "jugado": campos[7] == "si"}


def leer_partidos(ruta, config):
    '''Retorna (partidos ordenados por id, incidencias). Las filas inválidas o repetidas se descartan.'''
    partidos = {}
    incidencias = []
    for numero_linea, campos in leer_filas(ruta, encabezados()["partidos"]):
        try:
            partido = convertir_partido(campos, config)
            validaciones.validar_no_repetido(partido["id_partido"], partidos, "un partido")
            partidos[partido["id_partido"]] = partido
        except ValueError as error:
            incidencias.append((ruta, numero_linea, str(error)))
    return {clave: partidos[clave] for clave in sorted(partidos)}, incidencias


def leer_estadisticas(ruta):
    '''Retorna (estadisticas, incidencias). Las filas inválidas o con combinación repetida se descartan.'''
    estadisticas = []
    combinaciones_cargadas = set()
    incidencias = []
    for numero_linea, campos in leer_filas(ruta, encabezados()["estadisticas"]):
        try:
            validar_cantidad_campos(campos, 5)
            id_partido = validaciones.validar_entero_no_negativo(campos[0])
            codigo = validaciones.validar_formato_codigo_jugador(campos[1])
            bajas = validaciones.validar_entero_no_negativo(campos[2])
            muertes = validaciones.validar_entero_no_negativo(campos[3])
            asistencias = validaciones.validar_entero_no_negativo(campos[4])
            if (id_partido, codigo) in combinaciones_cargadas:
                raise ValueError(f"Combinación repetida: partido {id_partido} y jugador {codigo}")
            combinaciones_cargadas.add((id_partido, codigo))
            estadisticas.append({"id_partido": id_partido, "codigo_jugador": codigo, "bajas": bajas,
                                 "muertes": muertes, "asistencias": asistencias})
        except ValueError as error:
            incidencias.append((ruta, numero_linea, str(error)))
    return estadisticas, incidencias


# ============================================================
# 3) Escritura de CSV
# ============================================================

def linea_equipo(equipo):
    '''Retorna la línea de CSV de un equipo.'''
    return equipo["codigo_equipo"] + ";" + equipo["nombre_equipo"] + "\n"


def linea_jugador(jugador):
    '''Retorna la línea de CSV de un jugador.'''
    return jugador["codigo_jugador"] + ";" + jugador["nickname"] + ";" + jugador["codigo_equipo"] + "\n"


def linea_partido(partido):
    '''Retorna la línea de CSV de un partido.'''
    jugado = "no"
    if partido["jugado"]:
        jugado = "si"
    return (str(partido["id_partido"]) + ";" + partido["fase"] + ";" + partido["fecha"] + ";"
            + partido["equipo_a"] + ";" + partido["equipo_b"] + ";"
            + str(partido["rondas_a"]) + ";" + str(partido["rondas_b"]) + ";" + jugado + "\n")


def linea_estadistica(fila):
    '''Retorna la línea de CSV de una fila de estadísticas.'''
    return (str(fila["id_partido"]) + ";" + fila["codigo_jugador"] + ";" + str(fila["bajas"]) + ";"
            + str(fila["muertes"]) + ";" + str(fila["asistencias"]) + "\n")


def escribir_csv(ruta, encabezado, lineas):
    '''Escribe un CSV desde cero con su encabezado y sus líneas.'''
    with open(ruta, "wt", encoding="utf-8") as arch:
        arch.write(encabezado + "\n" + "".join(lineas))


def agregar_lineas(ruta, lineas):
    '''Agrega líneas al final de un archivo en una sola escritura.'''
    with open(ruta, "at", encoding="utf-8") as arch:
        arch.write("".join(lineas))


def guardar_jugadores(ruta, jugadores):
    '''Reescribe jugadores.csv desde el diccionario de jugadores.'''
    escribir_csv(ruta, encabezados()["jugadores"], [linea_jugador(jugadores[codigo]) for codigo in jugadores])


def guardar_partidos(ruta, partidos):
    '''Reescribe partidos.csv desde el diccionario de partidos.'''
    escribir_csv(ruta, encabezados()["partidos"], [linea_partido(partidos[clave]) for clave in partidos])


def guardar_estadisticas(ruta, estadisticas):
    '''Reescribe estadisticas.csv desde la lista de registros.'''
    escribir_csv(ruta, encabezados()["estadisticas"], [linea_estadistica(fila) for fila in estadisticas])


def registrar_equipo_en_archivos(ruta_equipos, ruta_jugadores, equipo, jugadores_nuevos, jugadores_actuales):
    '''Agrega los jugadores y después el equipo. Si algo falla, deshace y lanza OSError.'''
    try:
        agregar_lineas(ruta_jugadores, [linea_jugador(jugador) for jugador in jugadores_nuevos])
        agregar_lineas(ruta_equipos, [linea_equipo(equipo)])
    except OSError:
        try:
            guardar_jugadores(ruta_jugadores, jugadores_actuales)
        except OSError:
            raise OSError(f"No se pudo registrar el equipo ni restaurar {ruta_jugadores}")
        raise


def registrar_partido_en_archivos(ruta_estadisticas, ruta_partidos, filas_nuevas, partidos_nuevos, estadisticas_actuales):
    '''Agrega las estadísticas y reescribe los partidos. Si algo falla, deshace y lanza OSError.'''
    agregar_lineas(ruta_estadisticas, [linea_estadistica(fila) for fila in filas_nuevas])
    try:
        guardar_partidos(ruta_partidos, partidos_nuevos)
    except OSError:
        try:
            guardar_estadisticas(ruta_estadisticas, estadisticas_actuales)
        except OSError:
            raise OSError(f"No se pudo guardar el partido ni restaurar {ruta_estadisticas}")
        raise


def escribir_lineas(ruta, lineas):
    '''Escribe un reporte de texto desde cero, una línea por elemento.'''
    with open(ruta, "wt", encoding="utf-8") as arch:
        for linea in lineas:
            arch.write(linea + "\n")


# ============================================================
# 4) Consistencia entre archivos
# ============================================================

def verificar_combinacion_archivos(existe_equipos, existe_jugadores, existe_partidos, existe_estadisticas, hay_jugados):
    '''Retorna la situación que corresponde a qué archivos existen (tabla del punto 6.3).'''
    combinacion = (existe_equipos, existe_jugadores, existe_partidos, existe_estadisticas)
    if combinacion == (False, False, False, False):
        return "torneo_nuevo"
    elif combinacion == (True, True, False, False):
        return "inscripcion_en_curso"
    elif combinacion == (True, True, True, False) and not hay_jugados:
        return "cuadro_generado"
    elif combinacion == (True, True, True, True):
        return "torneo_existente"
    return "inconsistente"


def archivo_existe(ruta):
    '''Indica si el archivo se puede abrir para leer.'''
    try:
        with open(ruta, "rt", encoding="utf-8"):
            existe = True
    except FileNotFoundError:
        existe = False
    return existe


def preparar_archivos(config):
    '''Crea los CSV que faltan si la combinación es coherente; si no, lanza ValueError.'''
    rutas = config["archivos"]
    titulos = encabezados()
    existe = {nombre: archivo_existe(rutas[nombre]) for nombre in ("equipos", "jugadores", "partidos", "estadisticas")}

    hay_jugados = False
    if existe["partidos"]:
        partidos, incidencias = leer_partidos(rutas["partidos"], config)
        hay_jugados = operaciones.hay_partidos_jugados(partidos)

    situacion = verificar_combinacion_archivos(existe["equipos"], existe["jugadores"], existe["partidos"],
                                               existe["estadisticas"], hay_jugados)
    if situacion == "inconsistente":
        faltantes = [rutas[nombre] for nombre in existe if not existe[nombre]]
        raise ValueError(f"Los archivos son inconsistentes y no se puede reconstruir el torneo. Falta: {', '.join(faltantes)}")

    for nombre in existe:
        if not existe[nombre]:
            escribir_csv(rutas[nombre], titulos[nombre], [])


def verificar_equipos_y_jugadores(equipos, jugadores, config):
    '''Lanza ValueError si los jugadores no referencian a equipos existentes con su plantel completo.'''
    por_equipo = {codigo: 0 for codigo in equipos}
    for codigo in jugadores:
        codigo_equipo = jugadores[codigo]["codigo_equipo"]
        if codigo_equipo not in equipos:
            raise ValueError(f"El jugador {codigo} referencia al equipo inexistente {codigo_equipo}")
        por_equipo[codigo_equipo] += 1
    for codigo in por_equipo:
        if por_equipo[codigo] != config["jugadores_por_equipo"]:
            raise ValueError(f"El equipo {codigo} tiene {por_equipo[codigo]} jugadores y debe tener {config['jugadores_por_equipo']}")

    if set(equipos) != {"E" + str(i) for i in range(1, len(equipos) + 1)}:
        raise ValueError("Los códigos de equipo deben ser consecutivos desde E1")
    if set(jugadores) != {"J" + str(i).zfill(2) for i in range(1, len(jugadores) + 1)}:
        raise ValueError("Los códigos de jugador deben ser consecutivos desde J01")


def verificar_cuadro(equipos, partidos, config):
    '''Lanza ValueError si los partidos no forman un cuadro completo y coherente.'''
    if len(equipos) != config["cantidad_equipos"] or len(partidos) != 7:
        raise ValueError(f"Con el cuadro generado debe haber {config['cantidad_equipos']} equipos y 7 partidos")

    en_cuartos = set()
    for clave in (1, 2, 3, 4):
        equipo_a = partidos[clave]["equipo_a"]
        equipo_b = partidos[clave]["equipo_b"]
        if equipo_a not in equipos or equipo_b not in equipos or equipo_a == equipo_b:
            raise ValueError(f"El partido {clave} debe tener dos equipos existentes y distintos")
        if equipo_a in en_cuartos or equipo_b in en_cuartos:
            raise ValueError(f"El partido {clave} repite un equipo de otro cuarto de final")
        en_cuartos.add(equipo_a)
        en_cuartos.add(equipo_b)

    for destino in config["cuadro"]:
        origen_a, origen_b = config["cuadro"][destino]
        verificar_lugar(partidos[destino]["equipo_a"], partidos[origen_a], destino)
        verificar_lugar(partidos[destino]["equipo_b"], partidos[origen_b], destino)


def verificar_lugar(equipo, partido_origen, destino):
    '''Lanza ValueError si un lugar de un partido no es "" o el ganador del partido que lo alimenta.'''
    if partido_origen["jugado"]:
        esperado = operaciones.determinar_ganador(partido_origen)
    else:
        esperado = ""
    if equipo != esperado:
        raise ValueError(f"El partido {destino} no coincide con el resultado del partido {partido_origen['id_partido']}")


def verificar_estadisticas(estadisticas, jugadores, partidos):
    '''Lanza ValueError si una fila no corresponde a un partido jugado y a un jugador de ese partido.'''
    for fila in estadisticas:
        id_partido = fila["id_partido"]
        codigo = fila["codigo_jugador"]
        if id_partido not in partidos or not partidos[id_partido]["jugado"]:
            raise ValueError(f"Hay estadísticas del partido {id_partido}, que no existe o no está jugado")
        if codigo not in jugadores:
            raise ValueError(f"Hay estadísticas del jugador inexistente {codigo}")
        equipo = jugadores[codigo]["codigo_equipo"]
        if equipo != partidos[id_partido]["equipo_a"] and equipo != partidos[id_partido]["equipo_b"]:
            raise ValueError(f"El jugador {codigo} no pertenece a ningún equipo del partido {id_partido}")


def verificar_coherencia(equipos, jugadores, partidos, estadisticas, config):
    '''Lanza ValueError si el contenido de los archivos no permite reconstruir el torneo.'''
    verificar_equipos_y_jugadores(equipos, jugadores, config)
    if len(partidos) > 0:
        verificar_cuadro(equipos, partidos, config)
    verificar_estadisticas(estadisticas, jugadores, partidos)


def cargar_torneo(config):
    '''Prepara los archivos y retorna el diccionario torneo reconstruido, o lanza ValueError.'''
    rutas = config["archivos"]
    preparar_archivos(config)
    equipos, incidencias_equipos = leer_equipos(rutas["equipos"], config)
    jugadores, incidencias_jugadores = leer_jugadores(rutas["jugadores"], config)
    partidos, incidencias_partidos = leer_partidos(rutas["partidos"], config)
    estadisticas, incidencias_estadisticas = leer_estadisticas(rutas["estadisticas"])
    verificar_coherencia(equipos, jugadores, partidos, estadisticas, config)
    return {
        "config": config,
        "equipos": equipos,
        "jugadores": jugadores,
        "partidos": partidos,
        "estadisticas": estadisticas,
        "incidencias": incidencias_equipos + incidencias_jugadores + incidencias_partidos + incidencias_estadisticas,
        "usuario_actual": None,
    }
