# Cantidad de equipos y jugadores que participan (por cada equipo).
N_EQUIPOS = 8
N_JUGADORES = 5

# Limite de longitud de nombres (de jugadores)
LONGITUD_MIN_NOMBRE = 3
LONGITUD_MAX_NOMBRE = 20

# Limites de rondas
RONDAS_MIN = 0
RONDAS_MAX = 24

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


# Equipos, jugadores, matriz de stats, las llaves y partidos a jugar.
equipos = []
jugadores = []
matriz_stats = []
llaves_cuartos = []
partidos = []

# Inscripción, cuadro de enfrentamientos y campeon
inscripcion_cerrada = False
cuadro_generado = False
campeon = None