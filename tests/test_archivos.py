# Pruebas 18 a 23: archivos y consistencia.
# Cada prueba prepara sus archivos en tests/archivos_prueba/ con modo wt.

from archivos import (guardar_estadisticas, leer_estadisticas, registrar_equipo_en_archivos,
                      verificar_combinacion_archivos)


def escribir_estadisticas(ruta, lineas):
    with open(ruta, "wt", encoding="utf-8") as arch:
        arch.write("id_partido;codigo_jugador;bajas;muertes;asistencias\n")
        for linea in lineas:
            arch.write(linea + "\n")


def test_leer_archivo_inexistente_lanza_error():
    hubo_error = False
    try:
        leer_estadisticas("tests/archivos_prueba/no_existe.csv")
    except FileNotFoundError:
        hubo_error = True
    assert hubo_error, "Leer un archivo que no existe debería lanzar FileNotFoundError"


def test_guardar_y_leer_estadisticas():
    ruta = "tests/archivos_prueba/estadisticas_guardadas.csv"
    registros = [{"id_partido": 1, "codigo_jugador": "J01", "bajas": 24, "muertes": 15, "asistencias": 6},
                 {"id_partido": 1, "codigo_jugador": "J02", "bajas": 18, "muertes": 17, "asistencias": 4}]
    guardar_estadisticas(ruta, registros)
    leidos, incidencias = leer_estadisticas(ruta)
    assert leidos == registros, "Se deberían recuperar los mismos registros, con los números como enteros"
    assert incidencias == [], "No debería haber incidencias"


def test_fila_invalida_se_descarta():
    ruta = "tests/archivos_prueba/estadisticas_invalida.csv"
    escribir_estadisticas(ruta, ["1;J01;24;15;6", "1;J02;diez;17;4", "1;J03;18;17;4"])
    registros, incidencias = leer_estadisticas(ruta)
    assert len(registros) == 2, "Las dos filas válidas deberían cargarse"
    assert len(incidencias) == 1, "La fila inválida debería registrarse como incidencia"


def test_combinacion_duplicada_se_descarta():
    ruta = "tests/archivos_prueba/estadisticas_duplicada.csv"
    escribir_estadisticas(ruta, ["1;J01;24;15;6", "1;J01;24;15;6"])
    registros, incidencias = leer_estadisticas(ruta)
    assert len(registros) == 1, "La combinación repetida no debería cargarse dos veces"
    assert len(incidencias) == 1, "La fila repetida debería registrarse como incidencia"


def test_combinaciones_de_archivos():
    assert verificar_combinacion_archivos(False, True, True, True, True) == "inconsistente", "Sin equipos no se puede reconstruir"
    assert verificar_combinacion_archivos(False, False, False, False, False) == "torneo_nuevo", "Sin archivos es un torneo nuevo"


def test_alta_equipo_con_falla_no_deja_el_equipo():
    ruta_equipos = "tests/archivos_prueba/equipos_alta.csv"
    with open(ruta_equipos, "wt", encoding="utf-8") as arch:
        arch.write("codigo_equipo;nombre_equipo\n")
    equipo = {"codigo_equipo": "E1", "nombre_equipo": "furia_cs"}
    jugadores_nuevos = [{"codigo_jugador": "J01", "nickname": "kscerato", "codigo_equipo": "E1"}]

    hubo_error = False
    try:
        registrar_equipo_en_archivos(ruta_equipos, "tests/archivos_prueba/carpeta_inexistente/jugadores.csv",
                                     equipo, jugadores_nuevos, {})
    except OSError:
        hubo_error = True

    with open(ruta_equipos, "rt", encoding="utf-8") as arch:
        contenido = arch.read()
    assert hubo_error, "Si no se puede escribir jugadores.csv debería lanzarse OSError"
    assert contenido == "codigo_equipo;nombre_equipo\n", "equipos.csv debería seguir solo con el encabezado"
