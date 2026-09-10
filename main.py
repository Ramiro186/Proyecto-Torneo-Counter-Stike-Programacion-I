import operaciones


# Funcion principal: crea todas las estructuras en memoria y coordina el menu.
def main():
    # ----- Estructuras iniciales de inscripcion -----
    equipos = []          # lista de tuplas (codigo_equipo, nombre_equipo)
    jugadores = []        # lista de tuplas (codigo_jugador, nickname, codigo_equipo)
    matriz_stats = []     # fila = jugador, columnas = bajas/muertes/asistencias

    # ----- Partidos: 7 listas paralelas (el indice i identifica al MISMO partido) -----
    partidos_id = []        # int: 1..7
    partidos_fase = []      # str: una de FASES
    partidos_equipoA = []   # str: codigo_equipo, o "" si aun no se conoce
    partidos_equipoB = []   # str: codigo_equipo, o "" si aun no se conoce
    partidos_rondasA = []   # int: rondas ganadas por A, o -1 si no se cargo
    partidos_rondasB = []   # int: rondas ganadas por B, o -1 si no se cargo
    partidos_jugado = []    # bool: True si ya se cargo el resultado

    # ----- Banderas de estado del torneo -----
    inscripcion_cerrada = False
    cuadro_generado = False
    campeon = ""

    # A partir de aca va el menu, que usa estas estructuras y las pasa a operaciones.
    # (lo armamos mas adelante)

# Punto de entrada del programa: se llama a main para arrancar.
main()
    