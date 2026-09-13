import random
import re # Revisar
from datos import N_EQUIPOS, FASES, RONDAS_PARA_GANAR, UMBRAL_KDA, UMBRAL_CLUTCH, COL_BAJAS, COL_MUERTES, COL_ASISTENCIAS, NOMBRES_ESTADISTICAS, LONGITUD_MIN_NOMBRE, LONGITUD_MAX_NOMBRE, N_JUGADORES

# ------------------------------------------------------------
# 1) Inscripcion y Validaciones (Opciones 1 y 2 - Persona A)
# ------------------------------------------------------------

def normalizar_cadena(cadena):
    return cadena.strip().upper()

def es_nombre_valido(nombre): # Revisar
    if not nombre or nombre.isspace():
        return False
    if not (LONGITUD_MIN_NOMBRE <= len(nombre) <= LONGITUD_MAX_NOMBRE):
        return False
    if not re.match(r'^[A-Za-z0-9_]+$', nombre):
        return False
    if not re.search(r'[A-Za-z]', nombre):
        return False
    return True

def registrar_equipo(equipos, jugadores, matriz_stats, partidos_por_jugador, inscripcion_cerrada):
    if inscripcion_cerrada:
        print("La inscripcion esta cerrada. El cuadro del torneo ya fue generado.")
        return
        
    if len(equipos) >= N_EQUIPOS:
        print(f"Inscripcion cerrada: Ya se registraron los {N_EQUIPOS} equipos permitidos.")
        return

    nombre_equipo = input("Ingrese el nombre del equipo: ")
    nombre_norm = normalizar_cadena(nombre_equipo)
    
    if not es_nombre_valido(nombre_norm):
        print(f"Error: Nombre de equipo invalido ({LONGITUD_MIN_NOMBRE}-{LONGITUD_MAX_NOMBRE} caracteres, letras, numeros, sin espacios multiples).")
        return
        
    for codigo, nombre in equipos:
        if normalizar_cadena(nombre) == nombre_norm:
            print("Error: El equipo ya se encuentra registrado.")
            return
            
    codigo_equipo = f"E{len(equipos) + 1}"
    jugadores_temporales = []
    
    print(f"\n--- Registrando jugadores para {nombre_equipo} ---")
    while len(jugadores_temporales) < 5:
        username = input(f"Ingrese el username del jugador {len(jugadores_temporales) + 1}/5: ")
        user_norm = normalizar_cadena(username)
        
        if not es_nombre_valido(user_norm):
            print("Error: Username invalido.")
            continue
            
        duplicado_global = any(normalizar_cadena(j[1]) == user_norm for j in jugadores) # Revisar
        duplicado_local = any(normalizar_cadena(j[1]) == user_norm for j in jugadores_temporales) # Revisar
        
        if duplicado_global or duplicado_local:
            print("Error: Ese jugador ya esta registrado en el torneo o en este equipo.")
            continue
            
        num_jugador_actual = len(jugadores) + len(jugadores_temporales) + 1
        cod_jugador = "J" + str(num_jugador_actual).zfill(2) # Corrección en base a lo visto en clase
        jugadores_temporales.append((cod_jugador, username, codigo_equipo))
        print(f"Jugador '{username}' aceptado.")
        
    # Guardamos el equipo y los jugadores
    equipos.append((codigo_equipo, nombre_equipo))
    
    for jug in jugadores_temporales:
        jugadores.append(jug)
        # LLAMADA CLAVE: Sincronizamos las matrices de estadisticas
        agregar_fila_stats(matriz_stats, partidos_por_jugador)
        
    print(f"\nAlta exitosa! El equipo '{nombre_equipo}' y sus 5 jugadores estan listos.\n")

def listar_equipos_jugadores(equipos, jugadores):
    if not equipos:
        print("No hay equipos registrados actualmente.")
        return
        
    print("\n----- LISTADO DE EQUIPOS Y JUGADORES -----")
    for cod_eq, nom_eq in equipos:
        print(f"\n[{cod_eq}] Equipo: {nom_eq}")
        jugadores_del_equipo = [j for j in jugadores if j[2] == cod_eq]
        for cod_j, username, _ in jugadores_del_equipo:
            print(f"  - {cod_j}: {username}")
    print("-" * 42)


# La siguiente función, agrega un partido al final de todas las listas paralelas de una sola vez, manteniendo el indice alineado entre ellas.
# El Marcador arranca en -1 (no cargado) y jugado en False

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
    
# Generación del sorteo

# La función sortea los 8 equipos (una sola vez) y arma los 4 cuartos de final
# También crea la estructura de las 2 semifinales y la final, con participantes desconocidos ""
# Escribe sobre las listas parelelas (fuente unica)

def generar_cuadro(equipos, partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                   partidos_rondasA, partidos_rondasB, partidos_jugado):
    # Copia local SOLO de los codigos de equipo, para sortear sin tocar la lista original.
    codigos = [equipo[0] for equipo in equipos]
    random.shuffle(codigos)

    # Partidos 1 a 4: Cuartos de Final, con equipos reales tomados de a pares.
    for i in range(0, N_EQUIPOS, 2):
        agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                        partidos_rondasA, partidos_rondasB, partidos_jugado,
                        len(partidos_id) + 1, FASES[0], codigos[i], codigos[i + 1])


      # Partidos 5 y 6: Semifinales, participantes desconocidos por ahora.
    agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    len(partidos_id) + 1, FASES[1], "", "")
    agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    len(partidos_id) + 1, FASES[1], "", "")

    # Partido 7: Final, participantes desconocidos por ahora.
    agregar_partido(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    len(partidos_id) + 1, FASES[2], "", "")

    return True

# Devuelve el INDICE (posicion) del partido cuyo id coincide con id_partido.
# Si no existe ningun partido con ese id, devuelve -1.
def buscar_indice_partido(partidos_id, id_partido):
    for i in range(len(partidos_id)):
        if partidos_id[i] == id_partido:
            return i
    return -1



# Validación del marcador

#Punto 13: valida un marcador segun la regla simplificada.
    #Regla: gana quien llega primero a RONDAS_PARA_GANAR (13), sin prorroga.
    #Devuelve (True, "") si es valido, o (False, mensaje) si no lo es.

    #Un marcador es valido solo si:
     # - Ambos valores son numeros enteros.
     # - Ninguno es negativo.
     # - Exactamente uno de los dos vale RONDAS_PARA_GANAR (el ganador).
     # - El otro (el perdedor) es menor a RONDAS_PARA_GANAR.


def validar_marcador(rondas_A, rondas_B):
   
    # Que no sean negativos.
    if rondas_A < 0 or rondas_B < 0:
        return False, "Las rondas no pueden ser negativas."

    # Que exactamente uno haya llegado a 13.
    a_gano = rondas_A == RONDAS_PARA_GANAR
    b_gano = rondas_B == RONDAS_PARA_GANAR

    if not a_gano and not b_gano:
        return False, f"Ningun equipo llego a {RONDAS_PARA_GANAR} rondas: el partido no esta terminado."

    if a_gano and b_gano:
        return False, "No puede haber empate: ambos no pueden tener 13 rondas."

    # El perdedor debe tener menos de 13 (esto tambien descarta el empate 13-13).
    if a_gano:
        perdedor = rondas_B
    else:
        perdedor = rondas_A

    if perdedor >= RONDAS_PARA_GANAR:
        return False, f"El perdedor debe tener menos de {RONDAS_PARA_GANAR} rondas."


    return True, ""


# Punto 14

# Valida que un resultado se pueda cargar antes de aceptarlo.

def validar_carga_partido(partidos_id, partidos_equipoA, partidos_equipoB, partidos_jugado,
                          id_partido, rondas_A, rondas_B):
    # 1) El partido debe existir.
    indice = buscar_indice_partido(partidos_id, id_partido)
    if indice == -1:
        return False, -1, f"No existe un partido con id {id_partido}."

    # 2) El partido no debe haber sido cargado antes.
    if partidos_jugado[indice]:
        return False, -1, f"El partido {id_partido} ya tiene su resultado cargado."

    # 3) Ambos equipos deben estar definidos (no vacios).
    if partidos_equipoA[indice] == "" or partidos_equipoB[indice] == "":
        return False, -1, f"El partido {id_partido} todavia no tiene definidos sus dos equipos."

    # 4) El marcador debe cumplir la regla del punto 13.
    marcador_ok, mensaje = validar_marcador(rondas_A, rondas_B)
    if not marcador_ok:
        return False, -1, mensaje

    return True, indice, ""


# Punto 12: determina automaticamente el codigo del equipo ganador de un partido.
# Precondicion: el marcador ya fue validado (no hay empate).
def determinar_ganador(partidos_equipoA, partidos_equipoB,
                       partidos_rondasA, partidos_rondasB, indice):

    
    if partidos_rondasA[indice] > partidos_rondasB[indice]:
        return partidos_equipoA[indice]
    else:
        return partidos_equipoB[indice]




# Carga del resultado

#Pasos:
    #1. Valida la carga ( existe, no jugado, equipos definidos, marcador ok).
    #2. Si es valida, escribe las rondas en las listas paralelas.
    #3. Marca el partido como jugado.
    #4. Determina el ganador .
    #5. Hace avanzar el cuadro con ese ganador .
    #Devuelve (True, mensaje_exito) o (False, mensaje_error).


# Carga el resultado de un partido. Junta los puntos 12, 13 y 14.
# Devuelve (True, mensaje_exito) o (False, mensaje_error).
def cargar_resultado(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                     partidos_rondasA, partidos_rondasB, partidos_jugado,
                     id_partido, rondas_A, rondas_B):
    # 1) Validar todo antes de tocar nada.
    es_valido, indice, mensaje = validar_carga_partido(
        partidos_id, partidos_equipoA, partidos_equipoB, partidos_jugado,
        id_partido, rondas_A, rondas_B)
    if not es_valido:
        return False, mensaje, ""

    # 2) Escribir el marcador en la fila del partido.
    partidos_rondasA[indice] = rondas_A
    partidos_rondasB[indice] = rondas_B

    # 3) Marcar el partido como ya jugado.
    partidos_jugado[indice] = True

    # 4) Determinar automaticamente el ganador.
    ganador = determinar_ganador(partidos_equipoA, partidos_equipoB,
                                 partidos_rondasA, partidos_rondasB, indice)

    # 5) Hacer avanzar el cuadro colocando al ganador donde corresponda.
    #    Si se cerro la final, devuelve el codigo del campeon; si no, "".
    campeon = avanzar_cuadro(partidos_equipoA, partidos_equipoB, indice, ganador)

    return True, f"Resultado del partido {id_partido} cargado. Ganador: {ganador}.", campeon

# Colocar al ganador de un partido en el partido siguiente que corresponda.
# Recibe el indice del partido recien cerrado y el codigo del equipo ganador.
# Devuelve el codigo del campeon si se cerro la final, o "" si todavia no.


def avanzar_cuadro(partidos_equipoA, partidos_equipoB, indice, ganador):

    # Ganadores de CUARTOS (indices 0 a 3) van a las SEMIFINALES (4 y 5)

    if indice == 0: #primera partida
        partidos_equipoA[4] = ganador   # ganador del cuarto 1 -> Semifinal 1, lado A

    elif indice == 1:
        partidos_equipoB[4] = ganador   # ganador del cuarto 2 -> Semifinal 1, lado B

    elif indice == 2:
        partidos_equipoA[5] = ganador   # ganador del cuarto 3 -> Semifinal 2, lado A

    elif indice == 3:
        partidos_equipoB[5] = ganador   # ganador del cuarto 4 -> Semifinal 2, lado B

    # ----- Ganadores de SEMIFINALES (indices 4 y 5) van a la FINAL (6) -----
    elif indice == 4:
        partidos_equipoA[6] = ganador   # ganador de Semifinal 1 -> Final, lado A

    elif indice == 5:
        partidos_equipoB[6] = ganador   # ganador de Semifinal 2 -> Final, lado B

    # Ganador de la FINAL (indice 6) es el campeon

    elif indice == 6:
        return ganador   # se devuelve el campeon

    # Si el partido cerrado no era la final, todavia no hay campeon.

    return ""

# Indicar si se puede generar el cuadro de cuartos.
# Solo se permite cuando hay exactamente N_EQUIPOS (8) registrados y el cuadro aun no se genero.

def se_puede_generar_cuadro(equipos, cuadro_generado):

    if cuadro_generado:
        return False
    if len(equipos) < N_EQUIPOS:
        return False

    return True


# Indicar si un partido puntual esta listo para cargar su resultado.
# Un partido esta listo cuando ya tiene definidos sus dos equipos (no estan en "") y todavia no fue jugado.


def se_puede_cargar_partido(partidos_equipoA, partidos_equipoB, partidos_jugado, indice):

    # Si el indice no es valido, no se puede.

    if indice < 0 or indice >= len(partidos_jugado):
        return False
    
    # Si ya se jugo, no se puede volver a cargar.

    if partidos_jugado[indice]:
        return False

    # Si alguno de los dos equipos todavia no esta definido, no se puede.

    if partidos_equipoA[indice] == "" or partidos_equipoB[indice] == "":
        return False
    return True


# Indicar si ya se cargo al menos un partido con resultado.
# Sirve para bloquear consultas de informes/estadisticas cuando no hay datos aun (lo pidio la profe: no consultar MVP, rankings, etc. sin partidos cargados).

def hay_partidos_jugados(partidos_jugado):

    for jugado in partidos_jugado:
        if jugado:
            return True


    return False


# Pide un numero entero por consola de forma segura.
# Si el usuario escribe algo que no es un numero entero, avisa y vuelve a pedir.
# No deja avanzar hasta recibir un entero valido.

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



# Muestra el estado completo del cuadro del torneo.
# Recorre las 7 listas paralelas por indice y arma una linea por partido.
# Si el partido ya se jugo, muestra el marcador; si no, lo marca como pendiente.

def mostrar_cuadro(partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                   partidos_rondasA, partidos_rondasB, partidos_jugado, campeon):
    
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

        # Arma la parte del marcador segun si el partido ya se jugo o no.
        if partidos_jugado[i]:
            marcador = f"{partidos_rondasA[i]} - {partidos_rondasB[i]}"
        else:
            marcador = "pendiente"

        # Linea final del partido.
        print(f"Partido {partidos_id[i]} ({partidos_fase[i]}): {equipoA} vs {equipoB}  [{marcador}]")

    # Al final, el estado del campeon.
    if campeon == "":
        print("Campeon: aun no definido.")
    else:
        print(f"Campeon del torneo: {campeon}")


# Devuelve el INDICE del equipo cuyo codigo coincide (case-insensitive, normalizado).
# Si no existe, devuelve -1.
def buscar_indice_equipo(equipos, codigo_buscado):
    # Normalizamos: sin espacios de los costados y en mayusculas, para comparar parejo.
    codigo_normalizado = codigo_buscado.strip().upper()
    for i in range(len(equipos)):
        # equipos[i] es la tupla (codigo_equipo, nombre_equipo); [0] es el codigo.
        if equipos[i][0].strip().upper() == codigo_normalizado:
            return i
    return -1


# Muestra los datos de un equipo (por su codigo): nombre, jugadores y partidos donde aparece.
# Recibe las estructuras necesarias y el codigo que ingreso el usuario.
def mostrar_equipo(equipos, jugadores, partidos_id, partidos_fase,
                   partidos_equipoA, partidos_equipoB, codigo_buscado):
    indice = buscar_indice_equipo(equipos, codigo_buscado)

    # Si no se encontro, avisamos y cortamos.
    if indice == -1:
        print(f"No existe un equipo con codigo '{codigo_buscado}'.")
        return

    # Datos basicos del equipo.
    codigo_equipo = equipos[indice][0]
    nombre_equipo = equipos[indice][1]
    print()
    print(f"----- EQUIPO {codigo_equipo}: {nombre_equipo} -----")

    # Jugadores del equipo: recorremos la lista de jugadores y filtramos por codigo_equipo.
    print("Jugadores:")
    hay_jugadores = False
    for jugador in jugadores:
        # jugador es la tupla (codigo_jugador, nickname, codigo_equipo); [2] es su equipo.
        if jugador[2] == codigo_equipo:
            print(f"  - {jugador[0]}: {jugador[1]}")
            hay_jugadores = True
    if hay_jugadores == False:
        print("  (sin jugadores registrados)")

    # Partidos donde aparece este equipo (como A o como B).
    print("Partidos en el cuadro:")
    aparece = False
    for i in range(len(partidos_id)):
        if partidos_equipoA[i] == codigo_equipo or partidos_equipoB[i] == codigo_equipo:
            print(f"  - Partido {partidos_id[i]} ({partidos_fase[i]})")
            aparece = True
    if aparece == False:
        print("  (todavia no aparece en ningun partido)")

# ============================================================
# PARTE C - Estadisticas, KDA e informes
# Estas funciones van PEGADAS AL FINAL de operaciones.py
# Recordar ampliar el import de arriba de operaciones.py a:
#   from datos import (N_EQUIPOS, N_JUGADORES, FASES, RONDAS_PARA_GANAR,
#                      UMBRAL_KDA, UMBRAL_CLUTCH,
#                      COL_BAJAS, COL_MUERTES, COL_ASISTENCIAS,
#                      NOMBRES_ESTADISTICAS)
# ============================================================


# ------------------------------------------------------------
# 1) Sincronizacion de matriz_stats  (el hueco que nadie tenia)
# ------------------------------------------------------------

# Agrega la fila de estadisticas de UN jugador nuevo.
# Debe llamarse UNA VEZ por cada jugador que se agrega a la lista jugadores,
# inmediatamente despues del append del jugador (lo hace la Parte A).
# Asi la fila i de matriz_stats corresponde siempre al jugador i.
def agregar_fila_stats(matriz_stats, partidos_por_jugador):
    matriz_stats.append([0, 0, 0])   # [bajas, muertes, asistencias] acumuladas
    partidos_por_jugador.append(0)   # cuantos partidos disputo ese jugador


# ------------------------------------------------------------
# 2) Normalizacion y busquedas
# ------------------------------------------------------------

# Deja un texto listo para comparar: sin espacios de los costados y en minusculas.
def normalizar_texto(texto):
    return texto.strip().lower()


# Devuelve el INDICE del jugador cuyo codigo O nickname coincide.
# La comparacion es case-insensitive y normalizada. Si no existe, devuelve -1.
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


# ------------------------------------------------------------
# 3) Carga de estadisticas de un partido (punto 10)
# ------------------------------------------------------------

# Pide un numero entero mayor o igual a cero. Reutiliza pedir_entero de la Parte B.
def pedir_estadistica(mensaje):
    seguir = True
    valor = 0
    while seguir == True:
        valor = pedir_entero(mensaje)
        if valor < 0:
            print("Valor invalido: no puede ser negativo.")
        else:
            seguir = False
    return valor


# Carga las estadisticas de los 5 jugadores de UN equipo y las ACUMULA en la matriz.
def cargar_stats_de_equipo(jugadores, matriz_stats, partidos_por_jugador, codigo_equipo):
    indices = indices_de_equipo(jugadores, codigo_equipo)
    print()
    print(f"--- Estadisticas del equipo {codigo_equipo} ---")
    for i in indices:
        print(f"Jugador {jugadores[i][0]} ({jugadores[i][1]}):")
        bajas = pedir_estadistica("  Bajas: ")
        muertes = pedir_estadistica("  Muertes: ")
        asistencias = pedir_estadistica("  Asistencias: ")

        # Se SUMAN a lo que ya tenia acumulado del torneo (no se reemplaza).
        matriz_stats[i][COL_BAJAS] = matriz_stats[i][COL_BAJAS] + bajas
        matriz_stats[i][COL_MUERTES] = matriz_stats[i][COL_MUERTES] + muertes
        matriz_stats[i][COL_ASISTENCIAS] = matriz_stats[i][COL_ASISTENCIAS] + asistencias

        # Se registra que este jugador disputo un partido mas.
        partidos_por_jugador[i] = partidos_por_jugador[i] + 1


# Carga las estadisticas de los 10 jugadores de un partido (5 por equipo).
# Se llama DESPUES de que cargar_resultado devolvio True.
def cargar_estadisticas_partido(jugadores, matriz_stats, partidos_por_jugador,
                                codigo_equipoA, codigo_equipoB):
    cargar_stats_de_equipo(jugadores, matriz_stats, partidos_por_jugador, codigo_equipoA)
    cargar_stats_de_equipo(jugadores, matriz_stats, partidos_por_jugador, codigo_equipoB)
    print()
    print("Estadisticas del partido cargadas correctamente.")


# ------------------------------------------------------------
# 4) KDA (punto 16)
# ------------------------------------------------------------

# KDA = (bajas + asistencias) / muertes   si muertes > 0
# KDA = bajas + asistencias               si muertes == 0
def calcular_kda(matriz_stats, indice):
    bajas = matriz_stats[indice][COL_BAJAS]
    muertes = matriz_stats[indice][COL_MUERTES]
    asistencias = matriz_stats[indice][COL_ASISTENCIAS]

    if muertes > 0:
        return (bajas + asistencias) / muertes
    else:
        return bajas + asistencias


# Indica si el jugador disputo al menos un partido.
def jugo_algun_partido(partidos_por_jugador, indice):
    return partidos_por_jugador[indice] > 0


# Jugador clutch: KDA acumulado mayor o igual a UMBRAL_CLUTCH (punto 21).
def es_clutch(kda):
    return kda >= UMBRAL_CLUTCH


# ------------------------------------------------------------
# 5) Ranking (comprehension + lambda + slicing)  (punto 23)
# ------------------------------------------------------------

# Construye el ranking de jugadores por KDA, de mayor a menor.
# Solo incluye a los que disputaron al menos un partido.
# Cada fila del ranking es: [kda, codigo_jugador, nickname, codigo_equipo]
def construir_ranking(jugadores, matriz_stats, partidos_por_jugador):
    # COMPREHENSION: arma la lista de KDA de todos los jugadores.
    kdas = [calcular_kda(matriz_stats, i) for i in range(len(jugadores))]

    ranking = []
    for i in range(len(jugadores)):
        if jugo_algun_partido(partidos_por_jugador, i):
            ranking.append([kdas[i], jugadores[i][0], jugadores[i][1], jugadores[i][2]])

    # LAMBDA: ordena por el KDA (posicion 0 de cada fila), de mayor a menor.
    ranking.sort(key=lambda fila: fila[0], reverse=True)
    return ranking


# Informe 2: ranking completo de jugadores por KDA.
def mostrar_ranking_completo(ranking):
    print()
    print("----- RANKING DE JUGADORES POR KDA -----")
    if len(ranking) == 0:
        print("Todavia no hay jugadores con partidos disputados.")
        return

    posicion = 1
    for fila in ranking:
        kda = fila[0]
        if es_clutch(kda):
            marca = "  [CLUTCH]"
        else:
            marca = ""
        print(f"{posicion}. {fila[2]} ({fila[1]}) - equipo {fila[3]} - KDA: {kda:.2f}{marca}")
        posicion = posicion + 1


# Informe 3: Top 3 por KDA. Usa SLICING.
def mostrar_top3(ranking):
    print()
    print("----- TOP 3 DE JUGADORES POR KDA -----")
    if len(ranking) == 0:
        print("Todavia no hay jugadores con partidos disputados.")
        return

    top3 = ranking[:3]   # SLICING
    posicion = 1
    for fila in top3:
        print(f"{posicion}. {fila[2]} ({fila[1]}) - KDA: {fila[0]:.2f}")
        posicion = posicion + 1


# ------------------------------------------------------------
# 6) MVP, equipo mas letal, promedio y conteo (puntos 17 a 20)
# ------------------------------------------------------------

# Informe 4: MVP del torneo = jugador con mayor KDA acumulado.
# Si hay empate en el KDA maximo, se informan TODOS (punto 17).
def mostrar_mvp(ranking):
    print()
    print("----- MVP DEL TORNEO -----")
    if len(ranking) == 0:
        print("Todavia no hay jugadores con partidos disputados.")
        return

    # El ranking ya esta ordenado de mayor a menor: el maximo esta en la posicion 0.
    kda_maximo = ranking[0][0]

    empatados = []
    for fila in ranking:
        if fila[0] == kda_maximo:
            empatados.append(fila)

    if len(empatados) == 1:
        fila = empatados[0]
        print(f"MVP: {fila[2]} ({fila[1]}) - equipo {fila[3]} - KDA: {fila[0]:.2f}")
    else:
        print(f"Hay {len(empatados)} jugadores empatados con KDA {kda_maximo:.2f}:")
        for fila in empatados:
            print(f"  - {fila[2]} ({fila[1]}) - equipo {fila[3]}")


# Devuelve el total de bajas acumuladas por los jugadores de un equipo.
def bajas_de_equipo(jugadores, matriz_stats, codigo_equipo):
    total = 0
    for i in indices_de_equipo(jugadores, codigo_equipo):
        total = total + matriz_stats[i][COL_BAJAS]
    return total


# Informe 5: equipo mas letal = el que acumula mas bajas en total (punto 18).
def mostrar_equipo_mas_letal(equipos, jugadores, matriz_stats):
    print()
    print("----- EQUIPO MAS LETAL -----")
    if len(equipos) == 0:
        print("Todavia no hay equipos registrados.")
        return

    mejor_total = -1
    empatados = []

    for equipo in equipos:
        codigo = equipo[0]
        nombre = equipo[1]
        total = bajas_de_equipo(jugadores, matriz_stats, codigo)

        if total > mejor_total:
            mejor_total = total
            empatados = [[codigo, nombre]]
        elif total == mejor_total:
            empatados.append([codigo, nombre])

    if mejor_total <= 0:
        print("Todavia no hay bajas cargadas en el torneo.")
        return

    if len(empatados) == 1:
        print(f"{empatados[0][1]} ({empatados[0][0]}) con {mejor_total} bajas.")
    else:
        print(f"Hay {len(empatados)} equipos empatados con {mejor_total} bajas:")
        for fila in empatados:
            print(f"  - {fila[1]} ({fila[0]})")


# Punto 19: promedio de bajas por jugador, contando solo a los que jugaron.
def promedio_bajas_por_jugador(matriz_stats, partidos_por_jugador):
    total_bajas = 0
    cantidad = 0
    for i in range(len(matriz_stats)):
        if jugo_algun_partido(partidos_por_jugador, i):
            total_bajas = total_bajas + matriz_stats[i][COL_BAJAS]
            cantidad = cantidad + 1

    if cantidad == 0:
        return 0.0
    return total_bajas / cantidad


# Punto 20: cantidad de jugadores con KDA superior al umbral configurado.
def contar_kda_superior(matriz_stats, partidos_por_jugador, umbral):
    cantidad = 0
    for i in range(len(matriz_stats)):
        if jugo_algun_partido(partidos_por_jugador, i):
            if calcular_kda(matriz_stats, i) > umbral:
                cantidad = cantidad + 1
    return cantidad


# ------------------------------------------------------------
# 7) Busqueda de jugador (punto 22, menu 6)
# ------------------------------------------------------------

# Muestra la ficha completa de un jugador buscado por codigo o nickname.
def mostrar_jugador(jugadores, matriz_stats, partidos_por_jugador, texto_buscado):
    indice = buscar_indice_jugador(jugadores, texto_buscado)

    if indice == -1:
        print(f"No existe un jugador con codigo o nickname '{texto_buscado}'.")
        return

    codigo = jugadores[indice][0]
    nickname = jugadores[indice][1]
    codigo_equipo = jugadores[indice][2]

    print()
    print(f"----- JUGADOR {codigo}: {nickname} -----")
    print(f"Equipo: {codigo_equipo}")
    print(f"Partidos disputados: {partidos_por_jugador[indice]}")
    print(f"{NOMBRES_ESTADISTICAS[COL_BAJAS]}: {matriz_stats[indice][COL_BAJAS]}")
    print(f"{NOMBRES_ESTADISTICAS[COL_MUERTES]}: {matriz_stats[indice][COL_MUERTES]}")
    print(f"{NOMBRES_ESTADISTICAS[COL_ASISTENCIAS]}: {matriz_stats[indice][COL_ASISTENCIAS]}")

    if jugo_algun_partido(partidos_por_jugador, indice):
        kda = calcular_kda(matriz_stats, indice)
        print(f"KDA acumulado: {kda:.2f}")
        if es_clutch(kda):
            print("Condicion: JUGADOR CLUTCH (KDA >= 3.0)")
    else:
        print("KDA acumulado: sin partidos disputados.")


# ------------------------------------------------------------
# 8) Resumen general (informe 6)
# ------------------------------------------------------------

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


# Informe 6: resumen general del torneo.
def mostrar_resumen_general(equipos, jugadores, matriz_stats, partidos_por_jugador,
                            partidos_equipoA, partidos_equipoB,
                            partidos_rondasA, partidos_rondasB, partidos_jugado):
    print()
    print("----- RESUMEN GENERAL DEL TORNEO -----")

    jugados = contar_partidos_jugados(partidos_jugado)
    print(f"Partidos jugados: {jugados} de {len(partidos_jugado)}")

    eliminados = equipos_eliminados(partidos_equipoA, partidos_equipoB,
                                    partidos_rondasA, partidos_rondasB, partidos_jugado)
    if len(eliminados) == 0:
        print("Equipos eliminados: ninguno todavia.")
    else:
        print(f"Equipos eliminados ({len(eliminados)}):")
        for codigo in eliminados:
            indice_equipo = buscar_indice_equipo(equipos, codigo)
            if indice_equipo == -1:
                print(f"  - {codigo}")
            else:
                print(f"  - {equipos[indice_equipo][1]} ({codigo})")

    promedio = promedio_bajas_por_jugador(matriz_stats, partidos_por_jugador)
    print(f"Promedio de bajas por jugador: {promedio:.2f}")

    cantidad = contar_kda_superior(matriz_stats, partidos_por_jugador, UMBRAL_KDA)
    print(f"Jugadores con KDA mayor a {UMBRAL_KDA}: {cantidad}")


# ============================================================
# PARTE A (RESPALDO) - Inscripcion y validaciones
# Esto es un PLAN B: se usa solo si el integrante a cargo no entrega.
# Va pegado en operaciones.py igual que la Parte C.
# ============================================================


# ------------------------------------------------------------
# Punto 5: definicion de nombre / nickname valido
# ------------------------------------------------------------

# Verifica que un texto contenga SOLO letras, numeros y guion bajo.
def solo_caracteres_permitidos(texto):
    for caracter in texto:
        if caracter.isalnum() == False and caracter != "_":
            return False
    return True


# Verifica que el texto tenga al menos una letra
# (asi se descarta un nombre compuesto solo por numeros y/o guiones bajos).
def tiene_al_menos_una_letra(texto):
    for caracter in texto:
        if caracter.isalpha():
            return True
    return False


# Valida un nombre de equipo o un nickname de jugador segun el punto 5.
# Devuelve (True, "") si es valido, o (False, mensaje) si no lo es.
def validar_nombre(nombre):
    limpio = nombre.strip()

    if limpio == "":
        return False, "El nombre no puede estar vacio ni tener solo espacios."

    if len(limpio) < LONGITUD_MIN_NOMBRE:
        return False, f"El nombre debe tener al menos {LONGITUD_MIN_NOMBRE} caracteres."

    if len(limpio) > LONGITUD_MAX_NOMBRE:
        return False, f"El nombre no puede superar los {LONGITUD_MAX_NOMBRE} caracteres."

    if solo_caracteres_permitidos(limpio) == False:
        return False, "Solo se permiten letras, numeros y guion bajo (sin espacios ni simbolos)."

    if tiene_al_menos_una_letra(limpio) == False:
        return False, "El nombre no puede estar compuesto solo por numeros o guiones bajos."

    return True, ""


# ------------------------------------------------------------
# Controles de duplicados
# ------------------------------------------------------------

# Indica si ya existe un equipo con ese nombre (comparacion normalizada).
def existe_nombre_equipo(equipos, nombre):
    buscado = normalizar_texto(nombre)
    for equipo in equipos:
        if normalizar_texto(equipo[1]) == buscado:
            return True
    return False


# Indica si ya existe un jugador con ese nickname en TODO el torneo.
# Esto cubre las dos reglas del punto 4: sin duplicados dentro del equipo
# y sin un mismo jugador en dos equipos distintos.
def existe_nickname(jugadores, nickname):
    buscado = normalizar_texto(nickname)
    for jugador in jugadores:
        if normalizar_texto(jugador[1]) == buscado:
            return True
    return False


# ------------------------------------------------------------
# Pedido de datos con validacion
# ------------------------------------------------------------

# Pide un nombre de equipo hasta que sea valido y no este repetido.
def pedir_nombre_equipo(equipos):
    seguir = True
    nombre = ""
    while seguir == True:
        nombre = input("Nombre del equipo: ").strip()
        es_valido, mensaje = validar_nombre(nombre)

        if es_valido == False:
            print(f"Nombre invalido: {mensaje}")
        elif existe_nombre_equipo(equipos, nombre):
            print("Nombre invalido: ya existe un equipo con ese nombre.")
        else:
            seguir = False
    return nombre


# Pide un nickname hasta que sea valido y no este repetido en el torneo.
def pedir_nickname(jugadores, numero_jugador):
    seguir = True
    nickname = ""
    while seguir == True:
        nickname = input(f"  Nickname del jugador {numero_jugador}: ").strip()
        es_valido, mensaje = validar_nombre(nickname)

        if es_valido == False:
            print(f"  Nickname invalido: {mensaje}")
        elif existe_nickname(jugadores, nickname):
            print("  Nickname invalido: ese jugador ya esta registrado en el torneo.")
        else:
            seguir = False
    return nickname


# ------------------------------------------------------------
# Punto 6: registrar un equipo completo
# ------------------------------------------------------------

# Registra UN equipo con sus 5 jugadores.
# El equipo se agrega a la lista recien cuando los 5 jugadores son validos,
# por eso los jugadores se juntan primero en una lista temporal.
# Devuelve True si el alta se completo, False si no se pudo.
def registrar_equipo(equipos, jugadores, matriz_stats, partidos_por_jugador,
                     inscripcion_cerrada):
    # Control de estado: no se registra nada si la inscripcion ya cerro.
    if inscripcion_cerrada:
        print("La inscripcion esta cerrada: el cuadro del torneo ya fue generado.")
        return False

    # Control de estado: no puede haber un noveno equipo.
    if len(equipos) >= N_EQUIPOS:
        print(f"Ya hay {N_EQUIPOS} equipos registrados. No se admiten mas.")
        return False

    codigo_equipo = f"E{len(equipos) + 1}"
    print()
    print(f"----- REGISTRO DEL EQUIPO {codigo_equipo} -----")

    nombre_equipo = pedir_nombre_equipo(equipos)

    # Los jugadores se cargan en una lista temporal.
    # Si el alta se completa, recien ahi pasan a la lista definitiva.
    nicknames_nuevos = []
    for numero in range(1, N_JUGADORES + 1):
        # Se valida contra los jugadores ya registrados MAS los de este equipo,
        # para que no se repita un nickname dentro del mismo alta.
        seguir = True
        nickname = ""
        while seguir == True:
            nickname = pedir_nickname(jugadores, numero)
            repetido = False
            for cargado in nicknames_nuevos:
                if normalizar_texto(cargado) == normalizar_texto(nickname):
                    repetido = True
            if repetido:
                print("  Nickname invalido: ya lo cargaste en este mismo equipo.")
            else:
                seguir = False
        nicknames_nuevos.append(nickname)

    # Alta efectiva: el equipo se cierra con exactamente N_JUGADORES jugadores.
    equipos.append((codigo_equipo, nombre_equipo))

    for nickname in nicknames_nuevos:
        codigo_jugador = "J" + str(len(jugadores) + 1).zfill(2)
        jugadores.append((codigo_jugador, nickname, codigo_equipo))
        # IMPORTANTE: cada jugador nuevo necesita su fila de estadisticas,
        # para que el indice de jugadores y el de matriz_stats queden alineados.
        agregar_fila_stats(matriz_stats, partidos_por_jugador)

    print(f"Equipo {codigo_equipo} ({nombre_equipo}) registrado con {N_JUGADORES} jugadores.")
    print(f"Equipos registrados: {len(equipos)} de {N_EQUIPOS}.")
    return True


# ------------------------------------------------------------
# Menu 2: listar equipos y jugadores
# ------------------------------------------------------------

def listar_equipos_y_jugadores(equipos, jugadores):
    print()
    print("----- EQUIPOS Y JUGADORES -----")

    if len(equipos) == 0:
        print("Todavia no hay equipos registrados.")
        return

    for equipo in equipos:
        codigo_equipo = equipo[0]
        nombre_equipo = equipo[1]
        print()
        print(f"{codigo_equipo} - {nombre_equipo}")
        for jugador in jugadores:
            if jugador[2] == codigo_equipo:
                print(f"   {jugador[0]}: {jugador[1]}")

    print()
    print(f"Total: {len(equipos)} equipos y {len(jugadores)} jugadores.")