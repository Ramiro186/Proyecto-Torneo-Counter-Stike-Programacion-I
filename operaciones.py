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
        return False, mensaje

    # 2) Escribir el marcador en la fila del partido.
    partidos_rondasA[indice] = rondas_A
    partidos_rondasB[indice] = rondas_B

    # 3) Marcar el partido como ya jugado.
    partidos_jugado[indice] = True

    # 4) Determinar automaticamente el ganador.
    ganador = determinar_ganador(partidos_equipoA, partidos_equipoB,
                                 partidos_rondasA, partidos_rondasB, indice)

    # 5) PENDIENTE (punto 15): avanzar_cuadro(...) para colocar al ganador
    #    en la semifinal o final que corresponda.

    return True, f"Resultado del partido {id_partido} cargado. Ganador: {ganador}."