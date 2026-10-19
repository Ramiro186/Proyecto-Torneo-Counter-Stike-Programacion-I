# Proyecto-Torneo-Counter-Stike-Programacion-I
Proyecto integrador Etapa 1. 
Integrantes: Muraro Ramiro | Pota Santino | Slivka Alexis

Problemática:
El organizador de un torneo de Counter Strike	necesita registrar 8 equipos con sus jugadores, validar que cumplan las restricciones de ingreso (nombres validos, cantidad exacta de integrante, etc), generar automáticamente las llaves de cuartos de final, cargar los resultados con estadísticas básicas (bajas, muertes, asistencias) y calcular métricas de rendimiento (KDA, equipo más letal, MVP del torneo) sin recurrir a bases de datos externas.

Alcance:

1. Formato del torneo

8 equipos, eliminación directa, sin partido por tercer puesto.
Fases: `("Cuartos de Final", "Semifinal", "Final")` → 4 + 2 + 1 = **7 partidos totales**.
Solo se sortea (una vez), al generar los cuartos de final. Semifinal y final se arman automáticamente a partir de los ganadores (Punto 8).

2. Datos de equipo


Campo
Tipo
Notas
codigo_equipo 
String: “E1”,”E2”,”E6”,etc
Identificador para utilizar en cuanto a búsquedas y referencias internas
nombre_equipo 
String
Se explica a detalle en Punto 5
Jugadores
Se relaciona cada jugador con su respectivo código_equipo
Esto para que no se aniden las listas de jugadores dentro de los equipos


Representación en el código: lista equipos de tuplas (codigo_equipo, nombre_equipo). Se agrega un equipo a esta lista recién cuando completó sus 5 jugadores válidos (Punto 6).



3. Datos de jugador

Campo
Tipo
Notas
codigo_jugador
String. Ej: J01, J02, etc.
Identificador único
username
String
Validado (Punto 5)
codigo_equipo
String
Relaciona al jugador con su equipo


Representación en el código: lista jugadores de tuplas (codigo_jugador, nickname, codigo_equipo). Cada tupla es fija una vez creada; la lista crece a medida que se registran jugadores.

Las estadísticas numéricas no viven acá (ver punto 11) — se relacionan por posición/índice.


4. Reglas de validación de equipo

Un equipo se considera válido y se cierra su alta en el sistema una vez dadas las siguientes condiciones:

Contiene **exactamente 5 jugadores**, ni más ni menos.
Ningún jugador está duplicado dentro del equipo.
Ningún jugador pertenece simultáneamente a otro equipo.
Ningún username está vacío.
El equipo no supera los 5 integrantes en ningún momento de la carga.

## 5. Definición de "nombre válido" (equipos y jugadores)

- No está vacío ni compuesto solo de espacios.
- Longitud mínima de 3 caracteres y máxima de 20.
- Contiene solo letras, números y guion bajo (sin símbolos ni espacios).
- **Se normaliza antes de comparar y antes de guardar**: se quitan los espacios de los costados y se pasa a minúsculas. El valor que queda guardado es el normalizado, así "Sniper", " sniper " y "SNIPER" son el mismo nombre.
- No puede estar compuesto solo de números o guiones bajos.


6. Cierre de inscripción

Una vez registrados los 8 equipos completos y generado el cuadro de cuartos de final:

Se cierra la inscripción.
No se pueden registrar equipos nuevos ni modificar los existentes.
El menú debe reflejar este estado (Punto 24).

## 7. Reglas del sorteo de cuartos de final

- Se sortea sobre los códigos de los 8 equipos (`random.shuffle` sobre una copia local).
- Cada equipo aparece exactamente una vez y ningún equipo se enfrenta a sí mismo (se recorre la lista sorteada de a pares).
- Se generan exactamente 4 enfrentamientos, una sola vez durante la ejecución.
- **Los cruces se cargan directamente en los partidos 1 a 4** de las listas paralelas de partidos. No existe una estructura `llaves_cuartos` separada: hay una única fuente de información.

8. Progresión del cuadro (semifinales y final)

No se vuelve a sortear una vez definidos los Cuartos de final. Los cruces surgen de los ganadores:

Semifinal 1: ganador Cuarto 1 vs ganador Cuarto 2
Semifinal 2: ganador Cuarto 3 vs ganador Cuarto 4
Final: ganador Semifinal 1 vs ganador Semifinal 2
El ganador de la Final queda registrado como campeón del torneo.

## 9. Estructura de los partidos

Los 7 partidos se representan con **siete listas paralelas homogéneas**; el índice `i` identifica al mismo partido en todas:

| Lista | Tipo | Valor mientras no se conoce |
|---|---|---|
| `partidos_id` | int (1 a 7) | — |
| `partidos_fase` | str (una de `fases`) | — |
| `partidos_equipoA` | str (código de equipo) | `""` |
| `partidos_equipoB` | str (código de equipo) | `""` |
| `partidos_rondasA` | int | `-1` |
| `partidos_rondasB` | int | `-1` |
| `partidos_jugado` | bool | `False` |

Al generar el cuadro se crean los 7 partidos: los cuartos con sus equipos reales y las semifinales y la final con `""`, que se completan con los ganadores.

10. Datos que se cargan al finalizar un partido

- Partido seleccionado (por `id_partido`).
- Rondas ganadas por Equipo A.
- Rondas ganadas por Equipo B.
- Bajas, muertes y asistencias de cada uno de los 10 jugadores (5 por equipo) de ese partido.

11. Matriz de estadísticas

- Filas → jugadores (mismo orden/índice que la lista `jugadores`).
- Columnas → `("Bajas", "Muertes", "Asistencias")` (tupla fija de nombres de columnas).
- Cada celda: valor numérico **acumulado durante todo el torneo** (no por partido individual).
- Al cargar un partido, las estadísticas nuevas se **suman** a las ya existentes en la fila del jugador correspondiente.
- La matriz contiene **solo valores numéricos** — nombres y códigos de jugador se mantienen en la lista `jugadores` y se relacionan por posición.

Ejemplo conceptual (40 jugadores × 3 estadísticas):

```
matriz_stats[i] = [bajas_totales, muertes_totales, asistencias_totales]
```
donde `i` es el mismo índice que ocupa el jugador en la lista `jugadores`.

12. Determinación automática del ganador

- El usuario **nunca** ingresa el ganador manualmente.
- Se calcula: `ganador = equipoA if rondas_A > rondas_B else equipoB`.

## 13. Reglas válidas del marcador

Regla simplificada, sin prórroga: **gana el primer equipo que llega a 13 rondas**.

- Ambos valores deben ser enteros no negativos.
- Exactamente uno de los dos debe ser 13 (el ganador).
- El otro debe ser menor a 13 (de 0 a 12).
- Con esto quedan rechazados el empate (13-13), los marcadores de partidos no terminados (1-0, 12-10) y los valores por encima de 13.

## 14. Control de carga única de partido

Antes de aceptar un resultado se valida que el `id_partido` exista, que no haya sido cargado previamente, que sus dos equipos ya estén definidos (no se puede cargar una semifinal o la final antes de tiempo) y que el marcador cumpla el punto 13.

15. Progresión automática del cuadro

Al cerrar un partido de cuartos:

- El ganador se coloca automáticamente como `equipoA` o `equipoB` en la semifinal que corresponda.

Al cerrar una semifinal:

- El ganador se coloca automáticamente en la final.

Al cerrar la final:

- Se registra el campeón del torneo.

16. Fórmula de KDA

```
KDA = (bajas + asistencias) / muertes      si muertes > 0
KDA = bajas + asistencias                  si muertes == 0
```

Se documenta y aplica siempre de la misma manera, usando los valores **acumulados** de la matriz de estadísticas.

17. Definición de MVP del torneo

- Jugador con **mayor KDA acumulado** durante el torneo, considerando solo jugadores que disputaron al menos un partido.
- **Empate**: si dos o más jugadores comparten el KDA máximo, se informan **todos**, sin desempate adicional en esta etapa.

18. Definición de "equipo más letal"

- Equipo cuyos jugadores **acumulan la mayor cantidad total de bajas** del torneo.
- Se calcula recorriendo la matriz de estadísticas de los jugadores pertenecientes a cada equipo y sumando su columna de bajas.

19. Promedio explícito

- Promedio de bajas por jugador del torneo: suma total de bajas de todos los jugadores con al menos un partido jugado, dividido esa cantidad de jugadores.

## 20. Conteo explícito

Cantidad de jugadores con KDA superior a 2.0 (umbral configurable en `crear_configuracion()` de `datos.py`).

21. Condición destacable del dominio

- **Jugador clutch: aquel cuyo KDA acumulado es mayor o igual a 3.0 → se marca/destaca en el informe general.

22. Búsqueda concreta

- Buscar jugador por `código_jugador` o por `nickname` (búsqueda case-insensitive, normalizada igual que en el punto 5).

## 23. Uso de comprensión, slicing y lambda

- **Comprensión**: `kdas = [calcular_kda(matriz_stats, i) for i in range(len(jugadores))]`.
- **Lambda**: `ranking.sort(key=lambda registro: registro[0], reverse=True)`, donde cada registro del ranking es la tupla `(kda, codigo_jugador, nickname, codigo_equipo)`.
- **Slicing**: `ranking[:3]` para el Top 3.

24. Menú principal

1. Registrar equipo (con sus 5 jugadores)
2. Listar equipos y jugadores
3. Generar cuadro de cuartos de final (sorteo)
4. Consultar cuadro del torneo
5. Cargar resultado y estadísticas de un partido
6. Buscar jugador / equipo
7. Consultar rankings (general y Top 3)
8. Consultar estadísticas e informes (MVP, equipo más letal, resumen)
9. Salir


25. Informes finales (mínimo 5 → se definen 6)

1. Cuadro actual del torneo: cuartos, semifinales, final y campeón (o fases pendientes).
2. Ranking completo de jugadores por KDA.
3. Top 3 de jugadores por KDA.
4. MVP del torneo (con manejo de empate).
5. Equipo más letal.
6. Resumen general: partidos jugados, equipos eliminados, promedio de bajas por jugador, conteo de jugadores con KDA > umbral.


26. Control de estado del torneo

El menú no debe habilitar todas las opciones en cualquier momento:

- No se puede generar el cuadro de cuartos con menos de 8 equipos registrados.
- No se puede registrar un noveno equipo.
- No se puede modificar la inscripción una vez iniciado el torneo (cuadro generado).
- No se puede cargar el resultado de una semifinal antes de conocer sus participantes (cuartos correspondientes sin jugar).
- No se puede cargar la final antes de completar ambas semifinales.

27. Validaciones obligatorias (listado consolidado)

- Código de equipo duplicado.
- Nombre de equipo inválido (según regla del punto 5).
- Jugador duplicado (mismo jugador dos veces, o en dos equipos).
- Cantidad de jugadores por equipo distinta de 5.
- Nickname vacío o inválido.
- Partido inexistente (`id_partido` no encontrado).
- Partido ya cargado.
- Marcador inválido (empate, negativo, no numérico, fuera de rango).
- Estadísticas (bajas/muertes/asistencias) negativas o no numéricas.
- Búsqueda de jugador/equipo inexistente.
- Opción de menú incorrecta.

Todos los errores muestran un mensaje comprensible y permiten continuar operando sin cerrar el programa.

---
## Estructuras de datos — resumen final

| Estructura | Contenido | Tipo |
|---|---|---|
| `equipos` | `(codigo_equipo, nombre_equipo)` × 8 | Lista de tuplas |
| `jugadores` | `(codigo_jugador, nickname, codigo_equipo)` × 40 | Lista de tuplas |
| `matriz_stats` | fila = jugador; columnas 0 = bajas, 1 = muertes, 2 = asistencias (acumuladas) | Matriz numérica |
| `partidos_por_jugador` | partidos disputados por cada jugador (paralela a `jugadores`) | Lista de enteros |
| `partidos_id`, `partidos_fase`, `partidos_equipoA`, `partidos_equipoB`, `partidos_rondasA`, `partidos_rondasB`, `partidos_jugado` | datos de los 7 partidos | 7 listas paralelas homogéneas |
| ranking | `(kda, codigo_jugador, nickname, codigo_equipo)` | Lista de tuplas |
| `fases` | `("Cuartos de Final", "Semifinal", "Final")` | Tupla fija |
| `nombres_estadisticas` | `("Bajas", "Muertes", "Asistencias")` | Tupla fija |

## Módulos

```
proyecto_etapa1/
├── main.py         # menú, entradas (input), mensajes y funciones de presentación (print)
├── datos.py        # crear_configuracion(): devuelve las constantes y tuplas fijas (sin variables globales)
├── operaciones.py  # validaciones, sorteo, carga de partidos, progresión, KDA, ranking, búsquedas
└── README.md
```

`operaciones.py` no usa `input()` ni `print()`: devuelve resultados y mensajes, y `main.py` los muestra.

## Fuera de alcance (Etapa 1)

- Persistencia en archivos: los datos se pierden al cerrar el programa.
- Diccionarios y conjuntos.
- Modificar o dar de baja equipos y jugadores ya registrados.
- Partido por el tercer puesto, prórrogas y desempate del MVP.
- Corrección de un resultado de partido ya cargado.

