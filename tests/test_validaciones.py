# Pruebas 1 a 6: validaciones y reglas.

from validaciones import convertir_cuadro, validar_fecha, validar_marcador, validar_nombre


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
