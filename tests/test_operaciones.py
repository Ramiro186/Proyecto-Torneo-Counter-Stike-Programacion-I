# Pruebas 7 a 17: cálculos y reglas del negocio.

from operaciones import (acumular_stats_por_jugador, bajas_por_equipo, buscar_jugador_recursivo, calcular_kda,
                         detectar_alertas, determinar_ganador, es_clutch, generar_partidos, obtener_mvp,
                         promedio_bajas)


def crear_partido_jugado():
    return {"id_partido": 1, "fase": "Cuartos de Final", "fecha": "10/10/2026", "equipo_a": "E1",
            "equipo_b": "E5", "rondas_a": 13, "rondas_b": 9, "jugado": True}


def crear_jugadores():
    return {"J01": {"codigo_jugador": "J01", "nickname": "kscerato", "codigo_equipo": "E1"},
            "J02": {"codigo_jugador": "J02", "nickname": "yuurih", "codigo_equipo": "E5"},
            "J03": {"codigo_jugador": "J03", "nickname": "fallen", "codigo_equipo": "E5"}}


def crear_config():
    return {"fases": ("Cuartos de Final", "Semifinal", "Final"), "cuadro": {5: (1, 2), 6: (3, 4), 7: (5, 6)},
            "jugadores_por_equipo": 5, "umbral_kda_bajo": 0.5}


def crear_fila(codigo, bajas, muertes):
    return {"id_partido": 1, "codigo_jugador": codigo, "bajas": bajas, "muertes": muertes, "asistencias": 0}


def codigos_de_alertas(alertas):
    return [alerta[0] for alerta in alertas]


def test_calcular_kda():
    assert calcular_kda(20, 10, 5) == 2.5, "Con 20 bajas, 10 muertes y 5 asistencias el KDA debería ser 2.5"


def test_kda_sin_muertes():
    assert calcular_kda(10, 0, 4) == 14, "Con 0 muertes el KDA debería ser bajas + asistencias"


def test_determinar_ganador():
    assert determinar_ganador(crear_partido_jugado()) == "E1", "E1 ganó 13 a 9"


def test_acumular_stats_por_jugador():
    registros = [{"id_partido": 1, "codigo_jugador": "J01", "bajas": 20, "muertes": 10, "asistencias": 5},
                 {"id_partido": 5, "codigo_jugador": "J01", "bajas": 10, "muertes": 5, "asistencias": 1},
                 {"id_partido": 1, "codigo_jugador": "J02", "bajas": 7, "muertes": 12, "asistencias": 3}]
    resultado = acumular_stats_por_jugador(registros)
    assert resultado["J01"] == {"bajas": 30, "muertes": 15, "asistencias": 6, "partidos": 2}, "J01 tiene dos filas para sumar"
    assert resultado["J02"] == {"bajas": 7, "muertes": 12, "asistencias": 3, "partidos": 1}, "J02 tiene una sola fila"


def test_bajas_por_equipo():
    registros = [crear_fila("J01", 20, 5), crear_fila("J02", 7, 10), crear_fila("J03", 8, 10)]
    assert bajas_por_equipo(registros, crear_jugadores()) == {"E1": 20, "E5": 15}, "Las bajas deberían sumarse por equipo"


def test_cuadro_guarda_equipos_de_cuartos():
    partidos = generar_partidos(["E3", "E7", "E1", "E5", "E8", "E2", "E6", "E4"], crear_config())
    assert len(partidos) == 7, "El cuadro debería tener 7 partidos"
    assert partidos[1]["equipo_a"] == "E3" and partidos[1]["equipo_b"] == "E7", "El partido 1 toma el primer par"
    assert partidos[4]["equipo_a"] == "E6" and partidos[4]["equipo_b"] == "E4", "El partido 4 toma el último par"
    for id_partido in (5, 6, 7):
        assert partidos[id_partido]["equipo_a"] == "" and partidos[id_partido]["equipo_b"] == "", "Semifinales y final empiezan sin equipos"


def test_detecta_muertes_imposibles():
    partidos = {1: crear_partido_jugado()}
    filas = [crear_fila("J01", 0, 30)]
    alertas = detectar_alertas(partidos, crear_jugadores(), filas, [], crear_config())
    assert "A1" in codigos_de_alertas(alertas), "30 muertes en 22 rondas debería generar la alerta A1"


def test_alerta_a2_por_defecto():
    partidos = {1: crear_partido_jugado()}
    filas = [crear_fila("J01", 40, 0), crear_fila("J02", 0, 21), crear_fila("J03", 0, 21)]
    alertas = detectar_alertas(partidos, crear_jugadores(), filas, [], crear_config())
    assert "A2" in codigos_de_alertas(alertas), "40 bajas contra 42 muertes del rival debería generar la alerta A2"


def test_busqueda_recursiva():
    lista = list(crear_jugadores().values())
    assert buscar_jugador_recursivo(lista, "fallen") == lista[2], "Debería encontrar el registro del jugador"
    assert buscar_jugador_recursivo(lista, "no_existe") is None, "Un nickname inexistente debería retornar None"


def test_kda_igual_al_umbral_es_clutch():
    assert es_clutch(3.0, 3.0), "Un KDA igual al umbral debería considerarse clutch"


def test_historial_vacio():
    assert obtener_mvp([]) == [], "Sin ranking no hay MVP"
    assert promedio_bajas({}) == 0, "Sin jugadores el promedio debería ser 0"
