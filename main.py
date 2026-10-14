# ------------------------------------------------------------
# main.py - Menu, entradas del usuario y presentacion
# ------------------------------------------------------------
# Aca se concentran input() y print(). La logica vive en operaciones.py
# y la configuracion en datos.py (se obtiene con una funcion, sin variables globales).

import datos
import operaciones


# ============================================================
# Entrada de datos
# ============================================================

# Pide un numero entero por consola de forma segura.
# Si el usuario escribe algo que no es un entero, avisa y vuelve a pedir.
def pedir_entero(mensaje):
    seguir = True
    numero = 0
    while seguir == True:
        texto = input(mensaje)
        # strip() saca espacios de los costados; lstrip("-") saca un signo menos inicial
        # para poder aceptar negativos y que isdigit los reconozca.
        limpio = texto.strip()
        if limpio.lstrip("-").isdigit():
            numero = int(limpio)
            seguir = False
        else:
            print("Entrada invalida: escribi un numero entero.")
    return numero


# Pide un entero mayor o igual a cero (se usa para bajas, muertes y asistencias).
def pedir_entero_no_negativo(mensaje):
    seguir = True
    valor = 0
    while seguir == True:
        valor = pedir_entero(mensaje)
        if valor < 0:
            print("Valor invalido: no puede ser negativo.")
        else:
            seguir = False
    return valor


# Pide un nombre de equipo hasta que sea valido y no este repetido.
# Devuelve el nombre ya normalizado (asi se guarda).
def pedir_nombre_equipo(equipos, longitud_min, longitud_max):
    seguir = True
    nombre = ""
    while seguir == True:
        nombre = input("Nombre del equipo: ")
        es_valido, mensaje = operaciones.validar_nombre(nombre, longitud_min, longitud_max)
        if es_valido == False:
            print(f"Nombre invalido: {mensaje}")
        elif operaciones.existe_nombre_equipo(equipos, nombre):
            print("Nombre invalido: ya existe un equipo con ese nombre.")
        else:
            seguir = False
    return operaciones.normalizar_texto(nombre)


# Pide los nicknames del equipo en curso y los junta en una lista TEMPORAL.
# Cada nickname debe ser valido, no existir en el torneo y no repetirse en este mismo equipo.
# Las estructuras definitivas no se tocan aca: eso lo hace operaciones.registrar_equipo.
def pedir_nicknames_equipo(jugadores, n_jugadores, longitud_min, longitud_max):
    nicknames_nuevos = []
    for numero in range(1, n_jugadores + 1):
        seguir = True
        nickname = ""
        while seguir == True:
            nickname = input(f"  Nickname del jugador {numero}/{n_jugadores}: ")
            es_valido, mensaje = operaciones.validar_nombre(nickname, longitud_min, longitud_max)
            if es_valido == False:
                print(f"  Nickname invalido: {mensaje}")
            elif operaciones.existe_nickname(jugadores, nickname):
                print("  Nickname invalido: ese jugador ya esta registrado en el torneo.")
            elif operaciones.nickname_repetido_en_alta(nicknames_nuevos, nickname):
                print("  Nickname invalido: ya lo cargaste en este mismo equipo.")
            else:
                seguir = False
        nicknames_nuevos.append(operaciones.normalizar_texto(nickname))
    return nicknames_nuevos


# Pide bajas, muertes y asistencias de los 5 jugadores de un equipo y las acumula.
def pedir_estadisticas_equipo(jugadores, matriz_stats, partidos_por_jugador,
                              codigo_equipo, nombres_estadisticas):
    print()
    print(f"--- Estadisticas del equipo {codigo_equipo} ---")
    for i in operaciones.indices_de_equipo(jugadores, codigo_equipo):
        print(f"Jugador {jugadores[i][0]} ({jugadores[i][1]}):")
        bajas = pedir_entero_no_negativo(f"  {nombres_estadisticas[0]}: ")
        muertes = pedir_entero_no_negativo(f"  {nombres_estadisticas[1]}: ")
        asistencias = pedir_entero_no_negativo(f"  {nombres_estadisticas[2]}: ")
        operaciones.acumular_stats(matriz_stats, partidos_por_jugador, i,
                                   bajas, muertes, asistencias)


# ============================================================
# Presentacion
# ============================================================

# Muestra el menu reflejando el estado actual del torneo (punto 26).
def mostrar_menu(cantidad_equipos, n_equipos, inscripcion_cerrada, cuadro_generado, hay_jugados):
    if inscripcion_cerrada:
        estado_inscripcion = "[INSCRIPCION CERRADA]"
    elif cantidad_equipos >= n_equipos:
        estado_inscripcion = f"[CUPO COMPLETO {cantidad_equipos}/{n_equipos}]"
    else:
        estado_inscripcion = f"[{cantidad_equipos}/{n_equipos} inscriptos]"

    if cuadro_generado:
        estado_cuadro = "[YA GENERADO]"
    elif cantidad_equipos < n_equipos:
        estado_cuadro = f"[requiere {n_equipos} equipos]"
    else:
        estado_cuadro = "[DISPONIBLE]"

    if cuadro_generado:
        estado_partidos = ""
    else:
        estado_partidos = "[requiere cuadro generado]"

    if hay_jugados:
        estado_informes = ""
    else:
        estado_informes = "[requiere partidos jugados]"

    print()
    print("===== TORNEO COUNTER STRIKE =====")
    print(f"1. Registrar equipo (con sus 5 jugadores) {estado_inscripcion}")
    print("2. Listar equipos y jugadores")
    print(f"3. Generar cuadro de cuartos de final (sorteo) {estado_cuadro}")
    print(f"4. Consultar cuadro del torneo {estado_partidos}")
    print(f"5. Cargar resultado y estadisticas de un partido {estado_partidos}")
    print("6. Buscar jugador / equipo")
    print(f"7. Consultar rankings (general y Top 3) {estado_informes}")
    print(f"8. Consultar estadisticas e informes {estado_informes}")
    print("9. Salir")


# Listado de equipos con sus jugadores.
def mostrar_equipos_y_jugadores(equipos, jugadores):
    print()
    print("----- EQUIPOS Y JUGADORES -----")
    if len(equipos) == 0:
        print("Todavia no hay equipos registrados.")
        return
    for equipo in equipos:
        print()
        print(f"{equipo[0]} - {equipo[1]}")
        for i in operaciones.indices_de_equipo(jugadores, equipo[0]):
            print(f"   {jugadores[i][0]}: {jugadores[i][1]}")
    print()
    print(f"Total: {len(equipos)} equipos y {len(jugadores)} jugadores.")


# Informe 1: estado completo del cuadro del torneo.
def mostrar_cuadro(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                   partidos_rondasA, partidos_rondasB, partidos_jugado, campeon):
    print()
    print("----- CUADRO DEL TORNEO -----")
    for i in range(len(partidos_id)):
        # Si un equipo todavia no esta definido, se muestra "?" en vez de vacio.
        if partidos_equipoA[i] == "":
            equipoA = "?"
        else:
            equipoA = partidos_equipoA[i]
        if partidos_equipoB[i] == "":
            equipoB = "?"
        else:
            equipoB = partidos_equipoB[i]

        if partidos_jugado[i]:
            marcador = f"{partidos_rondasA[i]} - {partidos_rondasB[i]}"
        else:
            marcador = "pendiente"

        print(f"Partido {partidos_id[i]} ({partidos_fase[i]}): {equipoA} vs {equipoB}  [{marcador}]")

    if campeon == "":
        print("Campeon: aun no definido.")
    else:
        print(f"Campeon del torneo: {campeon}")


# Ficha de un jugador buscado por codigo o nickname.
def mostrar_jugador(jugadores, matriz_stats, partidos_por_jugador, texto_buscado,
                    nombres_estadisticas, umbral_clutch):
    indice = operaciones.buscar_indice_jugador(jugadores, texto_buscado)
    if indice == -1:
        print(f"No existe un jugador con codigo o nickname '{texto_buscado}'.")
        return

    bajas, muertes, asistencias = operaciones.obtener_stats(matriz_stats, indice)
    print()
    print(f"----- JUGADOR {jugadores[indice][0]}: {jugadores[indice][1]} -----")
    print(f"Equipo: {jugadores[indice][2]}")
    print(f"Partidos disputados: {partidos_por_jugador[indice]}")
    print(f"{nombres_estadisticas[0]}: {bajas}")
    print(f"{nombres_estadisticas[1]}: {muertes}")
    print(f"{nombres_estadisticas[2]}: {asistencias}")

    if operaciones.jugo_algun_partido(partidos_por_jugador, indice):
        kda = operaciones.calcular_kda(matriz_stats, indice)
        print(f"KDA acumulado: {kda:.2f}")
        if operaciones.es_clutch(kda, umbral_clutch):
            print(f"Condicion: JUGADOR CLUTCH (KDA >= {umbral_clutch})")
    else:
        print("KDA acumulado: sin partidos disputados.")


# Ficha de un equipo buscado por codigo: nombre, jugadores y partidos donde aparece.
def mostrar_equipo(equipos, jugadores, partidos_id, partidos_fase,
                   partidos_equipoA, partidos_equipoB, codigo_buscado):
    indice = operaciones.buscar_indice_equipo(equipos, codigo_buscado)
    if indice == -1:
        print(f"No existe un equipo con codigo '{codigo_buscado}'.")
        return

    codigo_equipo = equipos[indice][0]
    print()
    print(f"----- EQUIPO {codigo_equipo}: {equipos[indice][1]} -----")

    print("Jugadores:")
    for i in operaciones.indices_de_equipo(jugadores, codigo_equipo):
        print(f"  - {jugadores[i][0]}: {jugadores[i][1]}")

    print("Partidos en el cuadro:")
    indices_partidos = operaciones.indices_partidos_de_equipo(partidos_equipoA, partidos_equipoB,
                                                              codigo_equipo)
    if len(indices_partidos) == 0:
        print("  (todavia no aparece en ningun partido)")
    for i in indices_partidos:
        print(f"  - Partido {partidos_id[i]} ({partidos_fase[i]})")


# Informe 2: ranking completo por KDA (marca a los jugadores clutch).
def mostrar_ranking_completo(ranking, umbral_clutch):
    print()
    print("----- RANKING DE JUGADORES POR KDA -----")
    posicion = 1
    for registro in ranking:
        if operaciones.es_clutch(registro[0], umbral_clutch):
            marca = "  [CLUTCH]"
        else:
            marca = ""
        print(f"{posicion}. {registro[2]} ({registro[1]}) - equipo {registro[3]} - KDA: {registro[0]:.2f}{marca}")
        posicion = posicion + 1


# Informe 3: Top 3 por KDA.
def mostrar_top3(ranking):
    print()
    print("----- TOP 3 DE JUGADORES POR KDA -----")
    posicion = 1
    for registro in operaciones.obtener_top3(ranking):
        print(f"{posicion}. {registro[2]} ({registro[1]}) - KDA: {registro[0]:.2f}")
        posicion = posicion + 1


# Informe 4: MVP del torneo (con empates).
def mostrar_mvp(ranking):
    print()
    print("----- MVP DEL TORNEO -----")
    mvps = operaciones.obtener_mvp(ranking)
    if len(mvps) == 1:
        registro = mvps[0]
        print(f"MVP: {registro[2]} ({registro[1]}) - equipo {registro[3]} - KDA: {registro[0]:.2f}")
    else:
        print(f"Hay {len(mvps)} jugadores empatados con KDA {mvps[0][0]:.2f}:")
        for registro in mvps:
            print(f"  - {registro[2]} ({registro[1]}) - equipo {registro[3]}")


# Informe 5: equipo mas letal (con empates).
def mostrar_equipo_mas_letal(equipos, jugadores, matriz_stats):
    print()
    print("----- EQUIPO MAS LETAL -----")
    mejor_total, empatados = operaciones.obtener_equipos_mas_letales(equipos, jugadores, matriz_stats)
    if mejor_total <= 0:
        print("Todavia no hay bajas cargadas en el torneo.")
    elif len(empatados) == 1:
        print(f"{empatados[0][1]} ({empatados[0][0]}) con {mejor_total} bajas.")
    else:
        print(f"Hay {len(empatados)} equipos empatados con {mejor_total} bajas:")
        for equipo in empatados:
            print(f"  - {equipo[1]} ({equipo[0]})")


# Informe 6: resumen general del torneo.
def mostrar_resumen_general(equipos, matriz_stats, partidos_por_jugador,
                            partidos_equipoA, partidos_equipoB,
                            partidos_rondasA, partidos_rondasB, partidos_jugado, umbral_kda):
    print()
    print("----- RESUMEN GENERAL DEL TORNEO -----")

    jugados = operaciones.contar_partidos_jugados(partidos_jugado)
    print(f"Partidos jugados: {jugados} de {len(partidos_jugado)}")

    eliminados = operaciones.equipos_eliminados(partidos_equipoA, partidos_equipoB,
                                                partidos_rondasA, partidos_rondasB, partidos_jugado)
    if len(eliminados) == 0:
        print("Equipos eliminados: ninguno todavia.")
    else:
        print(f"Equipos eliminados ({len(eliminados)}):")
        for codigo in eliminados:
            indice_equipo = operaciones.buscar_indice_equipo(equipos, codigo)
            print(f"  - {equipos[indice_equipo][1]} ({codigo})")

    promedio = operaciones.promedio_bajas_por_jugador(matriz_stats, partidos_por_jugador)
    print(f"Promedio de bajas por jugador: {promedio:.2f}")

    cantidad = operaciones.contar_kda_superior(matriz_stats, partidos_por_jugador, umbral_kda)
    print(f"Jugadores con KDA mayor a {umbral_kda}: {cantidad}")


# ============================================================
# Funcion principal
# ============================================================

def main():
    # ----- Configuracion (se obtiene con una funcion: no hay variables globales) -----
    (n_equipos, n_jugadores, longitud_min, longitud_max, rondas_para_ganar,
     umbral_kda, umbral_clutch, fases, nombres_estadisticas) = datos.crear_configuracion()

    # ----- Estructuras de inscripcion -----
    equipos = []               # lista de tuplas (codigo_equipo, nombre_equipo)
    jugadores = []             # lista de tuplas (codigo_jugador, nickname, codigo_equipo)
    matriz_stats = []          # fila = jugador, columnas = bajas / muertes / asistencias
    partidos_por_jugador = []  # paralela a jugadores: partidos disputados por cada uno

    # ----- Partidos: 7 listas paralelas homogeneas (el indice i es el MISMO partido) -----
    partidos_id = []        # int: 1..7
    partidos_fase = []      # str: una de fases
    partidos_equipoA = []   # str: codigo_equipo, o "" si aun no se conoce
    partidos_equipoB = []   # str: codigo_equipo, o "" si aun no se conoce
    partidos_rondasA = []   # int: rondas ganadas por A, o -1 si no se cargo
    partidos_rondasB = []   # int: rondas ganadas por B, o -1 si no se cargo
    partidos_jugado = []    # bool: True si ya se cargo el resultado

    # ----- Banderas de estado del torneo -----
    inscripcion_cerrada = False
    cuadro_generado = False
    campeon = ""

    seguir = True
    while seguir == True:
        mostrar_menu(len(equipos), n_equipos, inscripcion_cerrada, cuadro_generado,
                     operaciones.hay_partidos_jugados(partidos_jugado))
        opcion = pedir_entero("Elegi una opcion: ")

        if opcion == 1:
            se_puede, motivo = operaciones.se_puede_registrar_equipo(equipos, inscripcion_cerrada, n_equipos)
            if se_puede == False:
                print(motivo)
            else:
                print()
                print(f"----- REGISTRO DEL EQUIPO E{len(equipos) + 1} -----")
                nombre_equipo = pedir_nombre_equipo(equipos, longitud_min, longitud_max)
                nicknames = pedir_nicknames_equipo(jugadores, n_jugadores, longitud_min, longitud_max)
                ok, mensaje = operaciones.registrar_equipo(equipos, jugadores, matriz_stats,
                                                           partidos_por_jugador, nombre_equipo,
                                                           nicknames, n_jugadores)
                print(mensaje)
                print(f"Equipos registrados: {len(equipos)} de {n_equipos}.")

        elif opcion == 2:
            mostrar_equipos_y_jugadores(equipos, jugadores)

        elif opcion == 3:
            if operaciones.se_puede_generar_cuadro(equipos, cuadro_generado, n_equipos):
                cuadro_generado = operaciones.generar_cuadro(
                    equipos, partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado, n_equipos, fases)
                inscripcion_cerrada = True
                print("Cuadro de cuartos generado. La inscripcion quedo cerrada.")
            elif cuadro_generado:
                print("El cuadro ya fue generado. No se puede volver a sortear.")
            else:
                print(f"Faltan equipos: hay {len(equipos)} de {n_equipos} necesarios.")

        elif opcion == 4:
            if cuadro_generado:
                mostrar_cuadro(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                               partidos_rondasA, partidos_rondasB, partidos_jugado, campeon)
            else:
                print("Todavia no se genero el cuadro. Usa la opcion 3 primero.")

        elif opcion == 5:
            if cuadro_generado == False:
                print("Todavia no se genero el cuadro. Usa la opcion 3 primero.")
            else:
                id_partido = pedir_entero("Id del partido a cargar: ")
                rondas_A = pedir_entero("Rondas ganadas por el equipo A: ")
                rondas_B = pedir_entero("Rondas ganadas por el equipo B: ")

                ok, mensaje, nuevo_campeon = operaciones.cargar_resultado(
                    partidos_id, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    id_partido, rondas_A, rondas_B, rondas_para_ganar)
                print(mensaje)

                # Solo si el resultado se cargo bien se piden las estadisticas
                # de los 10 jugadores (los 5 titulares de cada equipo).
                if ok:
                    indice = operaciones.buscar_indice_partido(partidos_id, id_partido)
                    pedir_estadisticas_equipo(jugadores, matriz_stats, partidos_por_jugador,
                                              partidos_equipoA[indice], nombres_estadisticas)
                    pedir_estadisticas_equipo(jugadores, matriz_stats, partidos_por_jugador,
                                              partidos_equipoB[indice], nombres_estadisticas)
                    print()
                    print("Estadisticas del partido cargadas correctamente.")

                if nuevo_campeon != "":
                    campeon = nuevo_campeon
                    print(f"El torneo termino. Campeon: {campeon}")

        elif opcion == 6:
            print()
            print("1. Buscar jugador (por codigo o nickname)")
            print("2. Buscar equipo (por codigo)")
            sub = pedir_entero("Que queres buscar: ")
            if sub == 1:
                texto = input("Codigo o nickname del jugador: ")
                mostrar_jugador(jugadores, matriz_stats, partidos_por_jugador, texto,
                                nombres_estadisticas, umbral_clutch)
            elif sub == 2:
                texto = input("Codigo del equipo: ")
                mostrar_equipo(equipos, jugadores, partidos_id, partidos_fase,
                               partidos_equipoA, partidos_equipoB, texto)
            else:
                print("Opcion invalida: elegi 1 o 2.")

        elif opcion == 7:
            if operaciones.hay_partidos_jugados(partidos_jugado) == False:
                print("Todavia no hay partidos cargados: no hay rankings para mostrar.")
            else:
                ranking = operaciones.construir_ranking(jugadores, matriz_stats, partidos_por_jugador)
                mostrar_ranking_completo(ranking, umbral_clutch)
                mostrar_top3(ranking)

        elif opcion == 8:
            if operaciones.hay_partidos_jugados(partidos_jugado) == False:
                print("Todavia no hay partidos cargados: no hay informes para mostrar.")
            else:
                ranking = operaciones.construir_ranking(jugadores, matriz_stats, partidos_por_jugador)
                mostrar_mvp(ranking)
                mostrar_equipo_mas_letal(equipos, jugadores, matriz_stats)
                mostrar_resumen_general(equipos, matriz_stats, partidos_por_jugador,
                                        partidos_equipoA, partidos_equipoB,
                                        partidos_rondasA, partidos_rondasB, partidos_jugado,
                                        umbral_kda)

        elif opcion == 9:
            print("Saliendo del programa. Hasta luego!")
            seguir = False

        else:
            print("Opcion invalida: elegi un numero del 1 al 9.")


# Punto de entrada: se llama a main para arrancar el programa.
main()