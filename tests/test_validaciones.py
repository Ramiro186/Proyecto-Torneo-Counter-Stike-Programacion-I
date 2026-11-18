# Pruebas 1 a 6 y 24 a 26: validaciones y reglas.

from validaciones import convertir_cuadro, validar_configuracion, validar_fecha, validar_marcador, validar_nombre


def crear_configuracion():
    return {"nombre_torneo": "Copa de prueba", "cantidad_equipos": 8, "jugadores_por_equipo": 5,
            "fases": ["Cuartos de Final", "Semifinal", "Final"], "cuadro": {"5": [1, 2], "6": [3, 4], "7": [5, 6]},
            "rondas_para_ganar": 13, "umbral_kda": 2.0, "umbral_clutch": 3.0, "umbral_kda_bajo": 0.5,
            "archivos": {"usuarios": "u.csv", "equipos": "e.csv", "jugadores": "j.csv", "partidos": "p.csv",
                         "estadisticas": "s.csv", "reporte_filtrado": "f.txt", "reporte_general": "g.txt",
                         "alertas": "a.txt"}}


def configuracion_lanza_error(clave, valor):
    crudo = crear_configuracion()
    crudo[clave] = valor
    hubo_error = False
    try:
        validar_configuracion(crudo)
    except ValueError:
        hubo_error = True
    return hubo_error


def test_nombre_valido_se_normaliza():
    assert validar_nombre("  KSCerato ") == "kscerato", "El nombre debería guardarse sin espacios y en minúsculas"


def test_nombre_sin_letras_lanza_error():
    hubo_error = False
    try:
        validar_nombre("___")
    except ValueError:
        hubo_error = True
    assert hubo_error, "Un nombre sin letras debería lanzar ValueError"


def test_fecha_inexistente_lanza_error():
    hubo_error = False
    try:
        validar_fecha("31/02/2026")
    except ValueError:
        hubo_error = True
    assert hubo_error, "El 31 de febrero no existe: debería lanzar ValueError"


def test_empate_lanza_error():
    hubo_error = False
    try:
        validar_marcador(13, 13, 13)
    except ValueError:
        hubo_error = True
    assert hubo_error, "Un empate 13-13 debería lanzar ValueError"


def test_marcador_13_a_12_es_valido():
    assert validar_marcador(13, 12, 13) == (13, 12), "El 13-12 es el límite del marcador y debería aceptarse"


def test_cuadro_con_claves_enteras():
    resultado = convertir_cuadro({"5": [1, 2], "6": [3, 4], "7": [5, 6]})
    assert resultado == {5: (1, 2), 6: (3, 4), 7: (5, 6)}, "Las claves deberían ser enteros y los pares, tuplas"


def test_configuracion_rechaza_nan_e_infinito():
    assert configuracion_lanza_error("umbral_kda", float("nan")), "json.loads acepta NaN: la configuración debería rechazarlo"
    assert configuracion_lanza_error("umbral_clutch", float("inf")), "json.loads acepta Infinity: la configuración debería rechazarlo"


def test_umbrales_desordenados_lanzan_error():
    assert configuracion_lanza_error("umbral_kda_bajo", 10.0), "El umbral de bajo rendimiento no puede superar al de clutch"


def test_rondas_para_ganar_limite():
    crudo = crear_configuracion()
    crudo["rondas_para_ganar"] = 16
    assert validar_configuracion(crudo)["rondas_para_ganar"] == 16, "16 rondas es el máximo permitido y debería aceptarse"
    assert configuracion_lanza_error("rondas_para_ganar", 17), "17 rondas supera el máximo y debería rechazarse"
