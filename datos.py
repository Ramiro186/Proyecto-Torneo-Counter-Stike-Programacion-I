# Cantidad de equipos y jugadores que participan (por cada equipo).
N_EQUIPOS = 8
N_JUGADORES = 5

# Limite de longitud de nombres (de jugadores)
LONGITUD_MIN_NOMBRE = 3
LONGITUD_MAX_NOMBRE = 20

# Regla de marcador simplificada (sin prórrogas): gana quien llega primero a esta cantidad de rondas.
RONDAS_PARA_GANAR = 13

# Umbral KDA / Clutch
UMBRAL_KDA = 2.0
UMBRAL_CLUTCH = 3.0

#Fases a jugar
FASES = ("Cuartos de Final", "Semifinal", "Final")

# KDA, contador.
NOMBRES_ESTADISTICAS = ("Bajas", "Muertes", "Asistencias")
COL_BAJAS = 0
COL_MUERTES = 1
COL_ASISTENCIAS = 2


# Equipos, jugadores, matriz de stats, las llaves.
equipos = []
jugadores = []
matriz_stats = []
# Se elimina llaves_cuartos, porque se pisa con otra parte del código

# Partidos se divide en listas individuales

partidos_id = []
partidos_fase = []
partidos_equipoA = []
partidos_equipoB = []
partidos_rondasA = []
partidos_rondasB = []
partidos_jugado = []

# Inscripción, cuadro de enfrentamientos y campeon
inscripcion_cerrada = False
cuadro_generado = False
campeon = None