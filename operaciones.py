import random
import datos

# La siguiente función, agrega un partido al final de todas las listas paralelas de una sola vez, manteniendo el indice alineado entre ellas.
# El Marcador arranca en -1 (no cargado) y jugado en False

def _agregar_partido(id_partido, fase, equipoA, equipoB): # Función reutilizable para evitar repetir código en el caso de los append

    datos.partidos_id.append(id_partido)
    datos.partidos_fase.append(fase)
    datos.partidos_equipoA.append(equipoA)
    datos.partidos_equipoB.append(equipoB)
    datos.partidos_rondasA.append(-1)
    datos.partidos_rondasB.append(-1)
    datos.partidos_jugados.append(False)
    
# Generación del sorteo

# La función sortea los 8 equipos (una sola vez) y arma los 4 cuartos de final
# También crea la estructura de las 2 semifinales y la final, con participantes desconocidos ""
# Escribe sobre las listas parelelas (fuente unica)

def generar_cuadro():

    # Copia local solo de los códigos de equipo para sortear sin utilizar datos.equipos. (Lo utilizo para no cambiar la lista original)

    codigos = [equipo[0] for equipo in datos.equipos]
    random.shuffle(codigos)

    # Partidos 1 a 4: Cuartos de final, con equipos tomados de a pares

    for i in range(0, 8, 2):
        _agregar_partido( 

            id_partido= len(datos.partidos_id) + 1,
            fase= datos.FASES[0], # Cuartos de Final
            equipoA=codigos[i],
            equipoB=codigos[i+1],
        )


    # Partidos 5 y 6: Semifinales, participantes desconocidos por ahora

    _agregar_partido(len(datos.partidos_id) + 1, datos.FASES[1], "","")
    _agregar_partido(len(datos.partidos_id) + 1, datos.FASES[1], "","")

    # Partido 7: Final, participantes desconocidos por ahora

    _agregar_partido(len(datos.partidos_id) + 1, datos.FASES[2], "", "")

    datos.cuadro_generado = True


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
    a_gano = rondas_A == datos.RONDAS_PARA_GANAR
    b_gano = rondas_B == datos.RONDAS_PARA_GANAR

    if not a_gano and not b_gano:
        return False, f"Ningun equipo llego a {datos.RONDAS_PARA_GANAR} rondas: el partido no esta terminado."

    if a_gano and b_gano:
        return False, "No puede haber empate: ambos no pueden tener 13 rondas."

    # El perdedor debe tener menos de 13 (esto tambien descarta el empate 13-13).
    if a_gano:
        perdedor = rondas_B
    else:
        perdedor = rondas_A

    if perdedor >= datos.RONDAS_PARA_GANAR:
        return False, f"El perdedor debe tener menos de {datos.RONDAS_PARA_GANAR} rondas."


    return True, ""



# Control de carga única

# Devuelve el INDICE (posicion) del partido cuyo id coincide con id_partido.
# Si no existe ningun partido con ese id, devuelve -1.
# El indice sirve para acceder al mismo partido en todas las listas paralelas.


def buscar_indice_partido(id_partido):
   
    for i in range(len(datos.partidos_id)):
        if datos.partidos_id[i] == id_partido:
            return i
    return -1