import operaciones
import datos
 
 
# Funcion principal:
def main():
    # ----- Estructuras iniciales de inscripcion -----
    equipos = []          # lista de tuplas (codigo_equipo, nombre_equipo)
    jugadores = []        # lista de tuplas (codigo_jugador, nickname, codigo_equipo)
    matriz_stats = []     # fila = jugador, columnas = bajas/muertes/asistencias
 
    # Lista paralela a jugadores: cuantos partidos disputo cada jugador.
    # Hace falta para saber quien "jugo al menos un partido" (MVP, promedio, conteo),
    # porque la matriz de estadisticas sola no alcanza para eso.
    partidos_por_jugador = []
 
    # ----- Partidos: 7 listas paralelas (el indice i identifica al MISMO partido) -----
    partidos_id = []        # int: 1..7
    partidos_fase = []      # str: una de FASES
    partidos_equipoA = []   # str: codigo_equipo, o "" si aun no se conoce
    partidos_equipoB = []   # str: codigo_equipo, o "" si aun no se conoce
    partidos_rondasA = []   # int: rondas ganadas por A, o -1 si no se cargo
    partidos_rondasB = []   # int: rondas ganadas por B, o -1 si no se cargo
    partidos_jugado = []    # bool: True si ya se cargo el resultado
 
    # Banderas de estado del torneo
 
    inscripcion_cerrada = False
    cuadro_generado = False
    campeon = ""
 
    # Menú principal
 
    seguir = True
    while seguir == True:
        print()
        print("===== TORNEO COUNTER STRIKE =====")
        print("1. Registrar equipo (con sus 5 jugadores)")
        print("2. Listar equipos y jugadores")
        print("3. Generar cuadro de cuartos de final (sorteo)")
        print("4. Consultar cuadro del torneo")
        print("5. Cargar resultado y estadisticas de un partido")
        print("6. Buscar jugador / equipo")
        print("7. Consultar rankings (general y Top 3)")
        print("8. Consultar estadisticas e informes")
        print("9. Salir")
 
        opcion = operaciones.pedir_entero("Elegi una opcion: ")
 
        if opcion == 1:
            operaciones.registrar_equipo(equipos, jugadores, matriz_stats, partidos_por_jugador, inscripcion_cerrada)
 
        elif opcion == 2:
            operaciones.listar_equipos_jugadores(equipos, jugadores)
 
        elif opcion == 3:
 
            # Solo se puede generar si hay 8 equipos y no se genero antes.
 
            if operaciones.se_puede_generar_cuadro(equipos, cuadro_generado):
 
                cuadro_generado = operaciones.generar_cuadro(
                    equipos, partidos_id, partidos_fase,
                    partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado)
                inscripcion_cerrada = True
                print("Cuadro de cuartos generado. La inscripcion quedo cerrada.")
            elif cuadro_generado:
                print("El cuadro ya fue generado. No se puede volver a sortear.")
            else:
                print(f"Faltan equipos: hay {len(equipos)} de {datos.N_EQUIPOS} necesarios.")
 
        elif opcion == 4:
 
            # Solo tiene sentido mostrar el cuadro si ya se genero.
 
            if cuadro_generado:
                operaciones.mostrar_cuadro(
                    partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado, campeon)
            else:
                print("Todavia no se genero el cuadro. Usa la opcion 3 primero.")
 
        elif opcion == 5:
 
            # No tiene sentido cargar resultados si el cuadro no se genero.
 
            if cuadro_generado == False:
                print("Todavia no se genero el cuadro. Usa la opcion 3 primero.")
            else:
                # Pedimos los datos del partido a cargar.
                id_partido = operaciones.pedir_entero("Id del partido a cargar: ")
                rondas_A = operaciones.pedir_entero("Rondas ganadas por el equipo A: ")
                rondas_B = operaciones.pedir_entero("Rondas ganadas por el equipo B: ")
 
                # Guardamos el indice ANTES de cargar, para saber que equipos
                # jugaron ese partido y a quien pedirle las estadisticas.
                indice = operaciones.buscar_indice_partido(partidos_id, id_partido)
                if indice == -1:
                    codigo_equipoA = ""
                    codigo_equipoB = ""
                else:
                    codigo_equipoA = partidos_equipoA[indice]
                    codigo_equipoB = partidos_equipoB[indice]
 
                # cargar_resultado hace toda la validacion y, si corresponde, avanza el cuadro.
                ok, mensaje, nuevo_campeon = operaciones.cargar_resultado(
                    partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    id_partido, rondas_A, rondas_B)
 
                # Mostramos el resultado (exito o el motivo del error).
                print(mensaje)
 
                # Si el resultado se cargo bien, recien ahi se cargan las estadisticas
                # de los 10 jugadores de ese partido (5 por equipo).
                if ok:
                    operaciones.cargar_estadisticas_partido(
                        jugadores, matriz_stats, partidos_por_jugador,
                        codigo_equipoA, codigo_equipoB)
 
                # Si esta carga cerro la final, guardamos el campeon en la bandera de main.
                if nuevo_campeon != "":
                    campeon = nuevo_campeon
                    print(f"El torneo termino. Campeon: {campeon}")
 
        elif opcion == 6:
            print()
            print("1. Buscar jugador (por codigo o nickname)")
            print("2. Buscar equipo (por codigo)")
            sub = operaciones.pedir_entero("Que queres buscar: ")
 
            if sub == 1:
                texto = input("Codigo o nickname del jugador: ")
                operaciones.mostrar_jugador(jugadores, matriz_stats,
                                            partidos_por_jugador, texto)
            elif sub == 2:
                texto = input("Codigo del equipo: ")
                operaciones.mostrar_equipo(equipos, jugadores, partidos_id,
                                           partidos_fase, partidos_equipoA,
                                           partidos_equipoB, texto)
            else:
                print("Opcion invalida: elegi 1 o 2.")
 
        elif opcion == 7:
 
            # Sin partidos cargados no hay estadisticas que rankear.
 
            if operaciones.hay_partidos_jugados(partidos_jugado) == False:
                print("Todavia no hay partidos cargados: no hay rankings para mostrar.")
            else:
                ranking = operaciones.construir_ranking(jugadores, matriz_stats,
                                                        partidos_por_jugador)
                operaciones.mostrar_ranking_completo(ranking)
                operaciones.mostrar_top3(ranking)
 
        elif opcion == 8:
 
            if operaciones.hay_partidos_jugados(partidos_jugado) == False:
                print("Todavia no hay partidos cargados: no hay informes para mostrar.")
            else:
                ranking = operaciones.construir_ranking(jugadores, matriz_stats,
                                                        partidos_por_jugador)
                operaciones.mostrar_mvp(ranking)
                operaciones.mostrar_equipo_mas_letal(equipos, jugadores, matriz_stats)
                operaciones.mostrar_resumen_general(
                    equipos, jugadores, matriz_stats, partidos_por_jugador,
                    partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado)
 
        elif opcion == 9:
            print("Saliendo del programa. Hasta luego!")
            seguir = False
 
        else:
            print("Opcion invalida: elegi un numero del 1 al 9.")
 
 
# Punto de entrada del programa: se llama a main para arrancar.
main()