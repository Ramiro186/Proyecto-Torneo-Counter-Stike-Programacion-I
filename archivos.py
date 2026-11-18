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


def texto_csv(encabezado, lineas):
    '''Retorna el contenido completo de un CSV: el encabezado y sus líneas.'''
    return encabezado + "\n" + "".join(lineas)


# ============================================================
# 4) Escritura con respaldo
# ============================================================
# Toda escritura pasa por escribir_con_respaldo: antes de tocar un archivo se guarda
# su contenido y, si cualquier escritura falla, cada archivo tocado vuelve a como estaba.

def leer_texto(ruta):
    '''Retorna el contenido completo de un archivo, o None si no existe.'''
    try:
        with open(ruta, "rt", encoding="utf-8") as arch:
            texto = arch.read()
    except FileNotFoundError:
        texto = None
    return texto


def escribir_texto(ruta, modo, texto):
    '''Escribe el texto en el archivo con el modo indicado (wt o at), en una sola escritura.'''
    with open(ruta, modo, encoding="utf-8") as arch:
        arch.write(texto)


def restaurar_archivo(ruta, texto_anterior):
    '''Deja el archivo con su contenido anterior, o vacío si no existía. Retorna False si no se pudo.'''
    restaurado = True
    try:
        if leer_texto(ruta) != texto_anterior:
            if texto_anterior is None:
                escribir_texto(ruta, "wt", "")
            else:
                escribir_texto(ruta, "wt", texto_anterior)
    except OSError:
        restaurado = False
    return restaurado


def escribir_con_respaldo(cambios):
    '''Aplica en orden cada cambio (ruta, modo, texto). Si uno falla, restaura los archivos tocados y lanza OSError.'''
    try:
        respaldos = [leer_texto(cambio[0]) for cambio in cambios]
    except OSError as error:
        raise OSError(f"No se pudo leer {error.filename} antes de escribir. No se guardó ningún cambio")

    escritos = 0
    falla = None
    while escritos < len(cambios) and falla is None:
        try:
            escribir_texto(cambios[escritos][0], cambios[escritos][1], cambios[escritos][2])
            escritos += 1
        except OSError as error:
            falla = error

    if falla is not None:
        sin_restaurar = []
        for i in range(escritos + 1):
            if not restaurar_archivo(cambios[i][0], respaldos[i]):
                sin_restaurar.append(cambios[i][0])
        motivo = falla.strerror
        if motivo is None:
            motivo = str(falla)
        if len(sin_restaurar) > 0:
            raise OSError(f"No se pudo escribir {cambios[escritos][0]} ({motivo}) ni restaurar {', '.join(sin_restaurar)}. "
                          "Revisá esos archivos antes de volver a iniciar")
        raise OSError(f"No se pudo escribir {cambios[escritos][0]} ({motivo}). Se restauraron los archivos y no se guardó ningún cambio")


def guardar_partidos(ruta, partidos):
    '''Reescribe partidos.csv desde el diccionario de partidos.'''
    texto = texto_csv(encabezados()["partidos"], [linea_partido(partidos[clave]) for clave in partidos])
    escribir_con_respaldo([(ruta, "wt", texto)])


def guardar_estadisticas(ruta, estadisticas):
    '''Reescribe estadisticas.csv desde la lista de registros.'''
    texto = texto_csv(encabezados()["estadisticas"], [linea_estadistica(fila) for fila in estadisticas])
    escribir_con_respaldo([(ruta, "wt", texto)])


def registrar_equipo_en_archivos(ruta_equipos, ruta_jugadores, equipo, jugadores_nuevos):
    '''Agrega los jugadores y después el equipo. Si algo falla, los dos archivos quedan como estaban.'''
    lineas_jugadores = "".join([linea_jugador(jugador) for jugador in jugadores_nuevos])
    escribir_con_respaldo([(ruta_jugadores, "at", lineas_jugadores), (ruta_equipos, "at", linea_equipo(equipo))])


def registrar_partido_en_archivos(ruta_estadisticas, ruta_partidos, filas_nuevas, partidos_nuevos):
    '''Agrega las estadísticas y reescribe los partidos. Si algo falla, los dos archivos quedan como estaban.'''
    lineas_estadisticas = "".join([linea_estadistica(fila) for fila in filas_nuevas])
    texto_partidos = texto_csv(encabezados()["partidos"], [linea_partido(partidos_nuevos[clave]) for clave in partidos_nuevos])
    escribir_con_respaldo([(ruta_estadisticas, "at", lineas_estadisticas), (ruta_partidos, "wt", texto_partidos)])


def escribir_lineas(ruta, lineas):
    '''Escribe un reporte de texto desde cero, una línea por elemento.'''
    escribir_con_respaldo([(ruta, "wt", "".join([linea + "\n" for linea in lineas]))])


# ============================================================
# 5) Consistencia entre archivos
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
    '''Indica si el archivo existe y no está vacío. Vacío es como queda un archivo cuya creación falló.'''
    texto = leer_texto(ruta)
    return texto is not None and texto != ""


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
        raise ValueError(f"Los archivos son inconsistentes y no se puede reconstruir el torneo. Falta o está vacío: {', '.join(faltantes)}")

    escribir_con_respaldo([(rutas[nombre], "wt", titulos[nombre] + "\n") for nombre in existe if not existe[nombre]])


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
