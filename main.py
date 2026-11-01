# ------------------------------------------------------------
# main.py - Login, menú, entradas del usuario y presentación
# ------------------------------------------------------------
# Único módulo con input() y print(). La lógica vive en operaciones.py
# y validaciones.py, los textos en reportes.py y los archivos en archivos.py.

import archivos
import operaciones
import reportes
import validaciones


# ============================================================
# Entrada de datos
# ============================================================

def pedir_dato(mensaje, validar):
    '''Pide un dato hasta que la función validar lo acepte y retorna lo que ella devuelve.'''
    valor = None
    valido = False
    while not valido:
        try:
            valor = validar(input(mensaje))
            valido = True
        except ValueError as error:
            print(f"Dato inválido: {error}.")
    return valor


def pedir_entero(mensaje):
    '''Pide un número entero no negativo hasta que sea válido.'''
    return pedir_dato(mensaje, validaciones.validar_entero_no_negativo)


def pedir_marcador(partido, config):
    '''Pide las rondas de los dos equipos hasta que el marcador sea válido.'''
    marcador = None
    while marcador is None:
        rondas_a = pedir_entero(f"Rondas de {partido['equipo_a']}: ")
        rondas_b = pedir_entero(f"Rondas de {partido['equipo_b']}: ")
        try:
            marcador = validaciones.validar_marcador(rondas_a, rondas_b, config["rondas_para_ganar"])
        except ValueError as error:
            print(f"Marcador inválido: {error}.")
    return marcador


def pedir_fecha_partido(id_partido, torneo):
    '''Pide la fecha de un partido hasta que sea real y respete el orden del cuadro.'''
    partidos = torneo["partidos"]
    cuadro = torneo["config"]["cuadro"]
    return pedir_dato("Fecha del partido (DD/MM/AAAA): ",
                      lambda texto: validaciones.validar_orden_fechas(validaciones.validar_fecha(texto), id_partido, partidos, cuadro))


def pedir_planilla_equipo(id_partido, codigo_equipo, rondas_totales, torneo):
    '''Pide bajas, muertes y asistencias de los jugadores de un equipo y retorna sus filas.'''
    filas = []
    print(f"--- Estadísticas de {reportes.texto_equipo(codigo_equipo, torneo['equipos'])} ---")
    for jugador in operaciones.jugadores_de_equipo(torneo["jugadores"], codigo_equipo):
        print(f"Jugador {jugador['codigo_jugador']} ({jugador['nickname']}):")
        bajas = pedir_entero("  Bajas: ")
        muertes = pedir_dato("  Muertes: ",
                             lambda texto: validaciones.validar_muertes_posibles(validaciones.validar_entero_no_negativo(texto), rondas_totales))
        asistencias = pedir_entero("  Asistencias: ")
        filas.append({"id_partido": id_partido, "codigo_jugador": jugador["codigo_jugador"],
                      "bajas": bajas, "muertes": muertes, "asistencias": asistencias})
    return filas


# ============================================================
# Presentación
# ============================================================

def mostrar_lineas(lineas):
    '''Muestra en pantalla las líneas de un informe.'''
    print()
    for linea in lineas:
        print(linea)


def texto_estado(torneo):
    '''Retorna el estado del torneo que se muestra en el encabezado del menú.'''
    config = torneo["config"]
    campeon = operaciones.obtener_campeon(torneo["partidos"], config["cuadro"])
    if campeon != "":
        return f"Torneo finalizado — Campeón: {torneo['equipos'][campeon]['nombre_equipo']}"
    elif len(torneo["partidos"]) > 0:
        return "Inscripción cerrada — Torneo en curso"
    return f"Inscripción abierta: {len(torneo['equipos'])}/{config['cantidad_equipos']} equipos"


def mostrar_menu(torneo):
    '''Muestra el menú según el rol del usuario y el estado del torneo.'''
    opciones = (("1", "Registrar equipo (con sus 5 jugadores)"),
                ("2", "Listar equipos y jugadores"),
                ("3", "Generar cuadro de cuartos de final (sorteo)"),
                ("4", "Consultar cuadro del torneo"),
                ("5", "Cargar resultado y estadísticas de un partido"),
                ("6", "Buscar jugador / equipo"),
                ("7", "Consultar rankings (general y Top 3)"),
                ("8", "Consultar estadísticas e informes"),
                ("9", "Reporte filtrado (equipo / fase / fecha)"),
                ("10", "Reporte general y alertas"),
                ("0", "Salir"))
    usuario = torneo["usuario_actual"]
    print()
    print(f"===== {torneo['config']['nombre_torneo']} =====")
    print(f"Usuario: {usuario['usuario']} ({usuario['rol']}) | {texto_estado(torneo)}")
    for numero, texto in opciones:
        motivo = operaciones.motivo_no_disponible(numero, torneo)
        if motivo == "":
            print(f"{numero}. {texto}")
        else:
            print(f"{numero}. {texto} (no disponible: {motivo})")


def actualizar_alertas(torneo):
    '''Recalcula las alertas, las escribe en alertas.txt y retorna la lista.'''
    config = torneo["config"]
    alertas = operaciones.detectar_alertas(torneo["partidos"], torneo["jugadores"], torneo["estadisticas"],
                                           torneo["incidencias"], config)
    archivos.escribir_lineas(config["archivos"]["alertas"], reportes.lineas_alertas(config["nombre_torneo"], alertas))
    return alertas


# ============================================================
# Opciones del menú
# ============================================================

def registrar_equipo(torneo):
    '''Opción 1: pide un equipo con sus jugadores, lo guarda y recién después lo agrega a la memoria.'''
    config = torneo["config"]
    equipos = torneo["equipos"]
    jugadores = torneo["jugadores"]
    print()
    print(f"----- REGISTRO DEL EQUIPO E{len(equipos) + 1} -----")
    nombres = operaciones.nombres_registrados(equipos)
    nombre = pedir_dato("Nombre del equipo: ",
                        lambda texto: validaciones.validar_no_repetido(validaciones.validar_nombre(texto), nombres, "un equipo"))

    registrados = operaciones.nicknames_registrados(jugadores)
    nicknames = []
    for numero in range(1, config["jugadores_por_equipo"] + 1):
        nickname = pedir_dato(f"  Nickname del jugador {numero}/{config['jugadores_por_equipo']}: ",
                              lambda texto: validaciones.validar_no_repetido(validaciones.validar_nombre(texto), registrados, "un jugador"))
        registrados.add(nickname)
        nicknames.append(nickname)

    equipo, jugadores_nuevos = operaciones.armar_equipo(nombre, nicknames, equipos, jugadores, config)
    archivos.registrar_equipo_en_archivos(config["archivos"]["equipos"], config["archivos"]["jugadores"],
                                          equipo, jugadores_nuevos, jugadores)
    equipos[equipo["codigo_equipo"]] = equipo
    for jugador in jugadores_nuevos:
        jugadores[jugador["codigo_jugador"]] = jugador
    print(f"Equipo {equipo['codigo_equipo']} registrado con {len(jugadores_nuevos)} jugadores.")


def generar_cuadro(torneo):
    '''Opción 3: sortea los cuartos, guarda el cuadro y cierra la inscripción.'''
    config = torneo["config"]
    partidos = operaciones.generar_partidos(operaciones.sortear_equipos(torneo["equipos"]), config)
    archivos.guardar_partidos(config["archivos"]["partidos"], partidos)
    torneo["partidos"] = partidos
    print("Cuadro generado. La inscripción quedó cerrada.")
    mostrar_lineas(reportes.lineas_cuadro(partidos, torneo["equipos"], ""))


def cargar_partido(torneo):
    '''Opción 5: pide resultado y planilla, valida, guarda y recién después actualiza la memoria.'''
    config = torneo["config"]
    print()
    print("Partidos disponibles para cargar:")
    for partido in operaciones.partidos_cargables(torneo["partidos"]):
        print(reportes.texto_partido(partido, torneo["equipos"]))

    id_partido = pedir_entero("Id del partido a cargar: ")
    partido = validaciones.validar_partido_cargable(id_partido, torneo["partidos"])
    rondas_a, rondas_b = pedir_marcador(partido, config)
    fecha = pedir_fecha_partido(id_partido, torneo)
    rondas_totales = rondas_a + rondas_b
    filas = (pedir_planilla_equipo(id_partido, partido["equipo_a"], rondas_totales, torneo)
             + pedir_planilla_equipo(id_partido, partido["equipo_b"], rondas_totales, torneo))

    partidos_nuevos = operaciones.preparar_carga_partido(id_partido, fecha, rondas_a, rondas_b, filas, torneo)
    archivos.registrar_partido_en_archivos(config["archivos"]["estadisticas"], config["archivos"]["partidos"],
                                           filas, partidos_nuevos, torneo["estadisticas"])
    torneo["partidos"] = partidos_nuevos
    torneo["estadisticas"] = torneo["estadisticas"] + filas

    ganador = operaciones.determinar_ganador(partidos_nuevos[id_partido])
    print(f"Resultado del partido {id_partido} cargado. Ganador: {reportes.texto_equipo(ganador, torneo['equipos'])}.")
    campeon = operaciones.obtener_campeon(partidos_nuevos, config["cuadro"])
    if campeon != "":
        print(f"El torneo terminó. Campeón: {reportes.texto_equipo(campeon, torneo['equipos'])}.")


def buscar(torneo):
    '''Opción 6: busca un jugador por código o por nickname (recursiva), o un equipo por código.'''
    config = torneo["config"]
    print()
    print("1. Buscar jugador por código")
    print("2. Buscar jugador por nickname")
    print("3. Buscar equipo por código")
    sub = input("Qué querés buscar: ").strip()

    if sub == "1" or sub == "2":
        if sub == "1":
            codigo = validaciones.validar_codigo_jugador(input("Código del jugador: ").strip().upper(), config)
            jugador = operaciones.buscar_por_codigo(torneo["jugadores"], codigo)
        else:
            nickname = input("Nickname del jugador: ").strip().lower()
            jugador = operaciones.buscar_jugador_recursivo(list(torneo["jugadores"].values()), nickname)
        if jugador is None:
            print("No se encontró el jugador.")
        else:
            stats = operaciones.acumular_stats_por_jugador(torneo["estadisticas"])
            mostrar_lineas(reportes.lineas_ficha_jugador(jugador, stats, torneo["equipos"], config["umbral_clutch"]))
    elif sub == "3":
        codigo = validaciones.validar_codigo_equipo(input("Código del equipo: ").strip().upper(), config)
        if operaciones.buscar_por_codigo(torneo["equipos"], codigo) is None:
            print("No se encontró el equipo.")
        else:
            mostrar_lineas(reportes.lineas_datos_equipo(operaciones.reporte_por_equipo(codigo, torneo), torneo["equipos"]))
    else:
        print("Opción inválida: elegí 1, 2 o 3.")


def mostrar_informe(opcion, torneo):
    '''Opciones 7 y 8: muestra rankings o estadísticas e informes.'''
    datos = operaciones.reporte_general(torneo)
    if opcion == "7":
        mostrar_lineas(reportes.lineas_rankings(datos))
    else:
        mostrar_lineas(reportes.lineas_informes(datos, torneo["equipos"], torneo["config"]["umbral_kda"]))


def lineas_filtro_equipo(torneo):
    '''Pide un equipo y retorna las líneas de su reporte, o [] si no existe.'''
    config = torneo["config"]
    codigo = validaciones.validar_codigo_equipo(input("Código del equipo: ").strip().upper(), config)
    if operaciones.buscar_por_codigo(torneo["equipos"], codigo) is None:
        print("No se encontró el equipo.")
        return []
    datos = operaciones.reporte_por_equipo(codigo, torneo)
    return reportes.lineas_reporte_equipo(config["nombre_torneo"], datos, torneo["equipos"])


def lineas_filtro_fase(torneo):
    '''Pide una fase y retorna las líneas de su reporte, o [] si la opción no existe.'''
    config = torneo["config"]
    fases = config["fases"]
    for i in range(len(fases)):
        print(f"{i + 1}. {fases[i]}")
    numero = pedir_entero("Fase: ")
    if numero < 1 or numero > len(fases):
        print("Opción inválida: esa fase no existe.")
        return []
    fase = fases[numero - 1]
    partidos_fase = operaciones.reporte_por_fase(fase, torneo["partidos"])
    return reportes.lineas_reporte_fase(config["nombre_torneo"], fase, partidos_fase, torneo["equipos"])


def lineas_filtro_fecha(torneo):
    '''Pide una fecha y retorna las líneas de su reporte.'''
    fecha = pedir_dato("Fecha (DD/MM/AAAA): ", validaciones.validar_fecha)
    resultados = operaciones.reporte_por_fecha(fecha, torneo)
    return reportes.lineas_reporte_fecha(torneo["config"]["nombre_torneo"], fecha, resultados, torneo["equipos"])


def reporte_filtrado(torneo):
    '''Opción 9: pide el filtro, muestra el reporte y lo escribe en reporte_filtrado.txt.'''
    print()
    print("1. Filtrar por equipo")
    print("2. Filtrar por fase")
    print("3. Filtrar por fecha")
    sub = input("Filtro: ").strip()
    lineas = []
    if sub == "1":
        lineas = lineas_filtro_equipo(torneo)
    elif sub == "2":
        lineas = lineas_filtro_fase(torneo)
    elif sub == "3":
        lineas = lineas_filtro_fecha(torneo)
    else:
        print("Opción inválida: elegí 1, 2 o 3.")

    if len(lineas) > 0:
        ruta = torneo["config"]["archivos"]["reporte_filtrado"]
        archivos.escribir_lineas(ruta, lineas)
        mostrar_lineas(lineas)
        print(f"Reporte guardado en {ruta}.")


def reporte_general(torneo):
    '''Opción 10: muestra el reporte general y las alertas y los escribe en sus archivos.'''
    config = torneo["config"]
    campeon = operaciones.obtener_campeon(torneo["partidos"], config["cuadro"])
    lineas = reportes.lineas_reporte_general(config["nombre_torneo"], operaciones.reporte_general(torneo),
                                             torneo["partidos"], torneo["equipos"], campeon, config["umbral_kda"])
    archivos.escribir_lineas(config["archivos"]["reporte_general"], lineas)
    alertas = actualizar_alertas(torneo)
    mostrar_lineas(lineas)
    mostrar_lineas(reportes.lineas_alertas(config["nombre_torneo"], alertas))
    print(f"Reportes guardados en {config['archivos']['reporte_general']} y {config['archivos']['alertas']}.")


def ejecutar_opcion(opcion, torneo):
    '''Ejecuta una opción del menú si está habilitada; si no, muestra el motivo.'''
    motivo = operaciones.motivo_no_disponible(opcion, torneo)
    if motivo != "":
        print(f"Opción no disponible: {motivo}.")
    elif opcion == "0":
        print("Saliendo del programa. ¡Hasta luego!")
    elif opcion == "1":
        registrar_equipo(torneo)
    elif opcion == "2":
        mostrar_lineas(reportes.lineas_equipos_y_jugadores(torneo["equipos"], torneo["jugadores"]))
    elif opcion == "3":
        generar_cuadro(torneo)
    elif opcion == "4":
        campeon = operaciones.obtener_campeon(torneo["partidos"], torneo["config"]["cuadro"])
        mostrar_lineas(reportes.lineas_cuadro(torneo["partidos"], torneo["equipos"], campeon))
    elif opcion == "5":
        cargar_partido(torneo)
    elif opcion == "6":
        buscar(torneo)
    elif opcion == "7" or opcion == "8":
        mostrar_informe(opcion, torneo)
    elif opcion == "9":
        reporte_filtrado(torneo)
    elif opcion == "10":
        reporte_general(torneo)
    else:
        print("Opción inválida: elegí un número del 0 al 10.")


def menu_principal(torneo):
    '''Repite el menú hasta que se elija salir. Un error no impide seguir operando.'''
    opcion = ""
    while opcion != "0":
        mostrar_menu(torneo)
        opcion = input("Elegí una opción: ").strip()
        try:
            ejecutar_opcion(opcion, torneo)
        except ValueError as error:
            print(f"Error: {error}.")
        except OSError as error:
            print(f"Error de archivo: {error}. No se guardó ningún cambio.")


# ============================================================
# Login e inicio
# ============================================================

def login(usuarios):
    '''Pide usuario y clave con 3 intentos. Retorna {"usuario", "rol"} o None.'''
    print("===== INICIO DE SESIÓN =====")
    usuario_actual = None
    intentos = 0
    autenticado = False
    while intentos < 3 and not autenticado:
        usuario = input("Usuario: ")
        clave = input("Clave: ")
        try:
            usuario_actual = validaciones.autenticar_usuario(usuario, clave, usuarios)
            autenticado = True
        except ValueError as error:
            intentos += 1
            print(f"{error}. Intento {intentos} de 3.")
    return usuario_actual


def avisar_alertas(torneo):
    '''Actualiza alertas.txt al iniciar e informa cuántas alertas hay. Si no se puede escribir, avisa y sigue.'''
    try:
        alertas = actualizar_alertas(torneo)
        if len(alertas) > 0:
            print(f"Se detectaron {len(alertas)} alertas. Detalle en {torneo['config']['archivos']['alertas']}.")
    except OSError as error:
        print(f"No se pudo escribir el archivo de alertas: {error}.")


def main():
    ruta_configuracion = "configuracion.json"
    try:
        config = validaciones.validar_configuracion(archivos.leer_configuracion(ruta_configuracion))
        usuarios, incidencias_usuarios = archivos.leer_usuarios(config["archivos"]["usuarios"])
        usuario_actual = login(usuarios)
        if usuario_actual is None:
            print("Se agotaron los intentos. El programa finaliza.")
        else:
            torneo = archivos.cargar_torneo(config)
            torneo["usuario_actual"] = usuario_actual
            torneo["incidencias"] = incidencias_usuarios + torneo["incidencias"]
            avisar_alertas(torneo)
            menu_principal(torneo)
    except FileNotFoundError as error:
        print(f"No se encontró {error.filename}. El programa finaliza.")
    except ValueError as error:
        print(f"Error: {error}. El programa finaliza.")
    except OSError as error:
        print(f"Error de archivo: {error}. El programa finaliza.")


# Punto de entrada: se llama a main para arrancar el programa.
main()
