# ------------------------------------------------------------
# datos.py - Configuracion del torneo
# ------------------------------------------------------------
# Por criterio de la etapa no se declaran variables a nivel de modulo.
# Los valores se crean dentro de esta funcion; main() la llama una sola vez,
# desempaqueta el resultado y pasa cada valor por parametro a quien lo necesite.

# Devuelve, en una tupla fija, todos los valores de configuracion del torneo.
# Orden: (n_equipos, n_jugadores, longitud_min, longitud_max, rondas_para_ganar,
#         umbral_kda, umbral_clutch, fases, nombres_estadisticas)
def crear_configuracion():
    n_equipos = 8           # equipos que participan del torneo
    n_jugadores = 5         # jugadores titulares por equipo
    longitud_min = 3        # largo minimo de nombre de equipo / nickname
    longitud_max = 20       # largo maximo de nombre de equipo / nickname
    rondas_para_ganar = 13  # regla de marcador: gana quien llega primero a 13 (sin prorroga)
    umbral_kda = 2.0        # conteo de jugadores con KDA superior a este valor
    umbral_clutch = 3.0     # KDA minimo para considerar a un jugador "clutch"

    # Tuplas fijas: no se modifican durante la ejecucion.
    fases = ("Cuartos de Final", "Semifinal", "Final")
    nombres_estadisticas = ("Bajas", "Muertes", "Asistencias")  # columnas 0, 1 y 2 de matriz_stats

    return (n_equipos, n_jugadores, longitud_min, longitud_max, rondas_para_ganar,
            umbral_kda, umbral_clutch, fases, nombres_estadisticas)