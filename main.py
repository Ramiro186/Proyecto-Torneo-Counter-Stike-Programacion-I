import operaciones
import datos


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
        print("5. Cargar resultado de un partido")
        print("6. Buscar jugador / equipo")
        print("7. Consultar rankings (general y Top 3)")
        print("8. Consultar estadisticas e informes")
        print("9. Salir")

        opcion = operaciones.pedir_entero("Elegi una opcion: ")

        if opcion == 1:
            print("[Opcion 1] La resuelve Persona A (inscripcion).")

        elif opcion == 2:
            print("[Opcion 2] La resuelve Persona A (inscripcion).")

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

                # cargar_resultado hace toda la validacion y, si corresponde, avanza el cuadro.
                ok, mensaje, nuevo_campeon = operaciones.cargar_resultado(
                    partidos_id, partidos_fase, partidos_equipoA, partidos_equipoB,
                    partidos_rondasA, partidos_rondasB, partidos_jugado,
                    id_partido, rondas_A, rondas_B)

                # Mostramos el resultado (exito o el motivo del error).
                print(mensaje)

                # Si esta carga cerro la final, guardamos el campeon en la bandera de main.
                if nuevo_campeon != "":
                    campeon = nuevo_campeon
                    print(f"El torneo termino. Campeon: {campeon}")

        elif opcion == 6:
            print("[Opcion 6] Buscar. (la completamos ahora)")

        elif opcion == 7:
            print("[Opcion 7] La resuelve Persona C (rankings).")

        elif opcion == 8:
            print("[Opcion 8] La resuelve Persona C (informes).")

        elif opcion == 9:
            print("Saliendo del programa. Hasta luego!")
            seguir = False

        else:
            print("Opcion invalida: elegi un numero del 1 al 9.")

# Punto de entrada del programa: se llama a main para arrancar.
main()