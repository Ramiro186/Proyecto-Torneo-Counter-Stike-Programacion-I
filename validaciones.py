# ------------------------------------------------------------
# validaciones.py - Expresiones regulares, reglas y configuración
# ------------------------------------------------------------
# Las funciones reciben el dato por parámetro, devuelven el valor normalizado
# y lanzan ValueError con el formato esperado. No usan input() ni print().

import re


# ============================================================
# 1) Nombres y códigos
# ============================================================

def validar_nombre(nombre):
    '''Retorna el nombre de equipo o nickname normalizado, o lanza ValueError.'''
    normalizado = nombre.strip().lower()
    if re.match("^[a-z0-9_]{3,20}$", normalizado) is None or re.search("[a-z]", normalizado) is None:
        raise ValueError("Debe tener entre 3 y 20 caracteres: letras, números o guion bajo, con al menos una letra")
    return normalizado


def validar_no_repetido(valor, registrados, descripcion):
    '''Retorna el valor si no está en el conjunto de registrados, o lanza ValueError.'''
    if valor in registrados:
        raise ValueError(f"Ya existe {descripcion} con el valor '{valor}'")
    return valor


def validar_codigo_equipo(codigo, config):
    '''Retorna el código de equipo si tiene formato válido y está en rango, o lanza ValueError.'''
    cantidad = config["cantidad_equipos"]
    mensaje = f"El código de equipo debe tener el formato E1 a E{cantidad}"
    if re.match("^E[0-9]{1,2}$", codigo) is None:
        raise ValueError(mensaje)
    numero = int(codigo[1:])
    if numero < 1 or numero > cantidad:
        raise ValueError(mensaje)
    return codigo


def validar_formato_codigo_jugador(codigo):
    '''Retorna el código de jugador si cumple el formato J00, o lanza ValueError.'''
    if re.match("^J[0-9]{2}$", codigo) is None:
        raise ValueError("El código de jugador debe tener el formato J01 a J40")
    return codigo


def validar_codigo_jugador(codigo, config):
    '''Retorna el código de jugador si tiene formato válido y está en rango, o lanza ValueError.'''
    validar_formato_codigo_jugador(codigo)
    maximo = config["cantidad_equipos"] * config["jugadores_por_equipo"]
    numero = int(codigo[1:])
    if numero < 1 or numero > maximo:
        raise ValueError(f"El código de jugador debe tener el formato J01 a J{maximo}")
    return codigo


# ============================================================
# 2) Login
# ============================================================

def validar_usuario(usuario):
    '''Retorna el usuario normalizado si cumple el formato, o lanza ValueError.'''
    normalizado = usuario.strip().lower()
    if re.match("^[a-z][a-z0-9_]{3,15}$", normalizado) is None:
        raise ValueError("El usuario debe empezar con letra y tener entre 4 y 16 caracteres")
    return normalizado


def validar_clave(clave):
    '''Retorna la clave tal cual si cumple el formato, o lanza ValueError.'''
    mensaje = "La clave debe tener entre 6 y 20 letras o números, con al menos una letra y un número"
    if re.match("^[A-Za-z0-9]{6,20}$", clave) is None:
        raise ValueError(mensaje)
    if re.search("[A-Za-z]", clave) is None or re.search("[0-9]", clave) is None:
        raise ValueError(mensaje)
    return clave


def validar_rol(rol):
    '''Retorna el rol si es uno de los permitidos, o lanza ValueError.'''
    if rol != "organizador" and rol != "espectador":
        raise ValueError("El rol debe ser organizador o espectador")
    return rol


def autenticar_usuario(usuario, clave, usuarios):
    '''Retorna {"usuario", "rol"} si los datos coinciden con usuarios, o lanza ValueError.'''
    usuario_normalizado = validar_usuario(usuario)
    validar_clave(clave)
    if usuario_normalizado not in usuarios or usuarios[usuario_normalizado]["clave"] != clave:
        raise ValueError("Usuario o clave incorrectos")
    return {"usuario": usuario_normalizado, "rol": usuarios[usuario_normalizado]["rol"]}


# ============================================================
# 3) Números, fechas y marcador
# ============================================================

def validar_entero_no_negativo(texto):
    '''Retorna el texto convertido a entero no negativo, o lanza ValueError.'''
    try:
        numero = int(texto)
    except ValueError:
        raise ValueError(f"'{texto}' no es un número entero")
    if numero < 0:
        raise ValueError(f"'{texto}' no puede ser negativo")
    return numero


def dias_del_mes(mes, anio):
    '''Retorna la cantidad de días de un mes (de 1 a 12) en ese año.'''
    if mes == 2:
        if (anio % 4 == 0 and anio % 100 != 0) or anio % 400 == 0:
            return 29
        return 28
    elif mes == 4 or mes == 6 or mes == 9 or mes == 11:
        return 30
    return 31


def validar_fecha(fecha):
    '''Retorna la fecha si tiene formato DD/MM/AAAA y es una fecha real, o lanza ValueError.'''
    mensaje = "La fecha debe tener el formato DD/MM/AAAA y ser una fecha válida"
    normalizada = fecha.strip()
    if re.match("^[0-9]{2}/[0-9]{2}/[0-9]{4}$", normalizada) is None:
        raise ValueError(mensaje)
    partes = normalizada.split("/")
    dia = int(partes[0])
    mes = int(partes[1])
    anio = int(partes[2])
    if mes < 1 or mes > 12 or dia < 1 or dia > dias_del_mes(mes, anio):
        raise ValueError(mensaje)
    return normalizada


def clave_fecha(fecha):
    '''Retorna la tupla (año, mes, día) de una fecha válida, para poder compararla.'''
    partes = fecha.split("/")
    return (int(partes[2]), int(partes[1]), int(partes[0]))


def validar_marcador(rondas_a, rondas_b, rondas_para_ganar):
    '''Retorna (rondas_a, rondas_b) si exactamente uno llegó a rondas_para_ganar y el otro no, o lanza ValueError.'''
    if rondas_a < 0 or rondas_b < 0:
        raise ValueError("Las rondas no pueden ser negativas")
    if rondas_a == rondas_para_ganar and rondas_b == rondas_para_ganar:
        raise ValueError(f"No puede haber empate: solo un equipo puede llegar a {rondas_para_ganar} rondas")
    if rondas_a != rondas_para_ganar and rondas_b != rondas_para_ganar:
        raise ValueError(f"Ningún equipo llegó a {rondas_para_ganar} rondas: el partido no está terminado")
    if rondas_a > rondas_para_ganar or rondas_b > rondas_para_ganar:
        raise ValueError(f"El perdedor debe tener menos de {rondas_para_ganar} rondas")
    return (rondas_a, rondas_b)


# ============================================================
# 4) Reglas de carga de equipos y partidos
# ============================================================

def validar_cantidad_jugadores(nicknames, config):
    '''Lanza ValueError si el equipo no tiene exactamente jugadores_por_equipo jugadores.'''
    if len(nicknames) != config["jugadores_por_equipo"]:
        raise ValueError(f"El equipo debe tener exactamente {config['jugadores_por_equipo']} jugadores")


def validar_partido_cargable(id_partido, partidos):
    '''Retorna el partido si existe, tiene sus dos equipos y no fue jugado, o lanza ValueError.'''
    if id_partido not in partidos:
        raise ValueError(f"No existe un partido con id {id_partido}")
    partido = partidos[id_partido]
    if partido["jugado"]:
        raise ValueError(f"El partido {id_partido} ya tiene su resultado cargado")
    if partido["equipo_a"] == "" or partido["equipo_b"] == "":
        raise ValueError(f"El partido {id_partido} todavía no tiene definidos sus dos equipos")
    return partido


def validar_orden_fechas(fecha, id_partido, partidos, cuadro):
    '''Lanza ValueError si la fecha es anterior a la de los partidos que alimentan a id_partido.'''
    if id_partido in cuadro:
        for origen in cuadro[id_partido]:
            if clave_fecha(fecha) < clave_fecha(partidos[origen]["fecha"]):
                raise ValueError(f"La fecha no puede ser anterior a la del partido {origen} ({partidos[origen]['fecha']})")
    return fecha


def validar_muertes_posibles(muertes, rondas_totales):
    '''Retorna las muertes si no superan las rondas jugadas, o lanza ValueError.'''
    if muertes > rondas_totales:
        raise ValueError(f"Un jugador no puede morir más veces que rondas jugadas ({rondas_totales})")
    return muertes


def validar_planilla(filas, partido, jugadores, estadisticas, config):
    '''Lanza ValueError si la planilla de un partido no cumple las reglas 1 a 3 del punto 10.'''
    esperadas = 2 * config["jugadores_por_equipo"]
    if len(filas) != esperadas:
        raise ValueError(f"La planilla debe tener exactamente {esperadas} filas")

    equipo_a = partido["equipo_a"]
    equipo_b = partido["equipo_b"]
    rondas_totales = partido["rondas_a"] + partido["rondas_b"]
    combinaciones_cargadas = {(fila["id_partido"], fila["codigo_jugador"]) for fila in estadisticas}
    bajas = {equipo_a: 0, equipo_b: 0}
    muertes = {equipo_a: 0, equipo_b: 0}

    for fila in filas:
        combinacion = (fila["id_partido"], fila["codigo_jugador"])
        codigo = fila["codigo_jugador"]
        if combinacion in combinaciones_cargadas:
            raise ValueError(f"El jugador {codigo} ya está cargado en este partido")
        combinaciones_cargadas.add(combinacion)
        if codigo not in jugadores or jugadores[codigo]["codigo_equipo"] not in bajas:
            raise ValueError(f"El jugador {codigo} no pertenece a ninguno de los dos equipos del partido")
        if fila["bajas"] < 0 or fila["muertes"] < 0 or fila["asistencias"] < 0:
            raise ValueError(f"Las estadísticas del jugador {codigo} no pueden ser negativas")
        validar_muertes_posibles(fila["muertes"], rondas_totales)
        bajas[jugadores[codigo]["codigo_equipo"]] += fila["bajas"]
        muertes[jugadores[codigo]["codigo_equipo"]] += fila["muertes"]

    if bajas[equipo_a] != muertes[equipo_b]:
        raise ValueError(f"Las bajas de {equipo_a} ({bajas[equipo_a]}) deben coincidir con las muertes de {equipo_b} ({muertes[equipo_b]})")
    if bajas[equipo_b] != muertes[equipo_a]:
        raise ValueError(f"Las bajas de {equipo_b} ({bajas[equipo_b]}) deben coincidir con las muertes de {equipo_a} ({muertes[equipo_a]})")


def fase_de_partido(id_partido, fases):
    '''Retorna la fase que le corresponde a un partido según su id (1 a 7).'''
    if id_partido <= 4:
        return fases[0]
    elif id_partido <= 6:
        return fases[1]
    return fases[2]


# ============================================================
# 5) Configuración
# ============================================================

def convertir_cuadro(cuadro):
    '''Retorna el cuadro con claves enteras y pares en tupla, o lanza ValueError.'''
    convertido = {}
    try:
        for clave in cuadro:
            par = cuadro[clave]
            if type(par) != list or len(par) != 2 or type(par[0]) != int or type(par[1]) != int:
                raise ValueError(f"El valor de cuadro['{clave}'] debe ser un par de enteros")
            if re.match("^[0-9]+$", clave) is None:
                raise ValueError(f"La clave '{clave}' de cuadro debe ser un número de partido")
            convertido[int(clave)] = (par[0], par[1])
    except TypeError:
        raise ValueError("La clave 'cuadro' debe ser un objeto con pares de partidos")
    if sorted(convertido) != [5, 6, 7]:
        raise ValueError("La clave 'cuadro' debe tener exactamente las claves 5, 6 y 7")
    origenes = []
    for destino in convertido:
        origenes = origenes + list(convertido[destino])
        if convertido[destino][0] >= destino or convertido[destino][1] >= destino:
            raise ValueError(f"cuadro['{destino}'] debe recibir ganadores de partidos anteriores")
    if sorted(origenes) != [1, 2, 3, 4, 5, 6]:
        raise ValueError("La clave 'cuadro' debe usar cada partido del 1 al 6 exactamente una vez")
    return convertido


def validar_entero_positivo_config(valor, clave):
    '''Lanza ValueError si el valor de esa clave no es un entero positivo.'''
    if type(valor) != int or valor <= 0:
        raise ValueError(f"La clave '{clave}' debe ser un entero positivo")


def validar_numero_config(valor, clave):
    '''Lanza ValueError si el valor de esa clave no es un número no negativo.'''
    if (type(valor) != int and type(valor) != float) or valor < 0:
        raise ValueError(f"La clave '{clave}' debe ser un número no negativo")


def validar_archivos_config(archivos):
    '''Lanza ValueError si falta alguna ruta o no es un texto.'''
    claves = ("usuarios", "equipos", "jugadores", "partidos", "estadisticas",
              "reporte_filtrado", "reporte_general", "alertas")
    for clave in claves:
        if clave not in archivos:
            raise ValueError(f"Falta la clave 'archivos.{clave}' en la configuración")
        if type(archivos[clave]) != str or archivos[clave] == "":
            raise ValueError(f"La clave 'archivos.{clave}' debe ser una ruta")


def validar_configuracion(crudo):
    '''Retorna el diccionario config ya validado y convertido, o lanza ValueError.'''
    try:
        nombre_torneo = crudo["nombre_torneo"]
        cantidad_equipos = crudo["cantidad_equipos"]
        jugadores_por_equipo = crudo["jugadores_por_equipo"]
        fases = crudo["fases"]
        cuadro = crudo["cuadro"]
        rondas_para_ganar = crudo["rondas_para_ganar"]
        umbral_kda = crudo["umbral_kda"]
        umbral_clutch = crudo["umbral_clutch"]
        umbral_kda_bajo = crudo["umbral_kda_bajo"]
        rutas = crudo["archivos"]
        validar_archivos_config(rutas)
    except KeyError as error:
        raise ValueError(f"Falta la clave {error} en la configuración")
    except TypeError:
        raise ValueError("La configuración debe ser un objeto JSON con las claves y tipos esperados")

    if type(nombre_torneo) != str:
        raise ValueError("La clave 'nombre_torneo' debe ser un texto")
    validar_entero_positivo_config(cantidad_equipos, "cantidad_equipos")
    validar_entero_positivo_config(jugadores_por_equipo, "jugadores_por_equipo")
    validar_entero_positivo_config(rondas_para_ganar, "rondas_para_ganar")
    validar_numero_config(umbral_kda, "umbral_kda")
    validar_numero_config(umbral_clutch, "umbral_clutch")
    validar_numero_config(umbral_kda_bajo, "umbral_kda_bajo")
    if cantidad_equipos != 8:
        raise ValueError("La clave 'cantidad_equipos' debe ser 8: el cuadro tiene 7 partidos")
    if cantidad_equipos * jugadores_por_equipo > 99:
        raise ValueError("La clave 'jugadores_por_equipo' es demasiado grande para los códigos J01 a J99")
    if type(fases) != list or len(fases) != 3:
        raise ValueError("La clave 'fases' debe ser una lista de 3 fases")

    return {
        "nombre_torneo": nombre_torneo,
        "cantidad_equipos": cantidad_equipos,
        "jugadores_por_equipo": jugadores_por_equipo,
        "fases": tuple(fases),
        "cuadro": convertir_cuadro(cuadro),
        "rondas_para_ganar": rondas_para_ganar,
        "umbral_kda": umbral_kda,
        "umbral_clutch": umbral_clutch,
        "umbral_kda_bajo": umbral_kda_bajo,
        "archivos": rutas,
    }
