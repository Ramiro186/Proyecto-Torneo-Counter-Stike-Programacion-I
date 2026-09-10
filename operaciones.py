import random
from datos import N_EQUIPOS, FASES, RONDAS_PARA_GANAR

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