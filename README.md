# Proyecto-Torneo-Counter-Stike-Programacion-I
Proyecto integrador Etapa 2. Evolución, persistencia y pruebas.
Integrantes: Muraro Ramiro | Pota Santino | Slivka Alexis
 
Problemática:
El organizador de un torneo de Counter Strike necesita registrar 8 equipos con sus jugadores, validar que cumplan las restricciones de ingreso, generar automáticamente las llaves de cuartos de final, cargar los resultados con estadísticas básicas (bajas, muertes, asistencias) y calcular métricas de rendimiento (KDA, equipo más letal, MVP del torneo). En esta segunda etapa, además, el sistema debe conservar la información entre ejecuciones, permitir el acceso solo a usuarios registrados, trabajar con el historial de partidos, generar reportes y alertas en archivos de texto y comprobar automáticamente parte de su funcionamiento con pruebas unitarias.
 
Alcance:
 
## 1. Sentido de la segunda etapa
 
La etapa 2 convierte el gestor de torneo de la etapa 1 en un sistema persistente: el torneo sobrevive al cierre del programa, se reanuda en el mismo punto y parte de su lógica se verifica con pruebas automáticas.
 
- **Principio de continuidad:** se reutilizan el problema, las reglas y las funciones válidas de la etapa 1: formato de 8 equipos, regla de nombre válido, sorteo único de cuartos con `random.shuffle`, progresión del cuadro, marcador a 13 rondas, fórmula de KDA, MVP con empate, equipo más letal, promedio, conteo, jugador clutch, ranking ordenado con lambda y Top 3 con slicing.
- **Lo nuevo:** login de usuario, configuración en JSON, historial en CSV, reportes y alertas en archivos de texto, validación con expresiones regulares, manejo de excepciones, pruebas unitarias con pytest y una función recursiva.
- **Reglas de la rúbrica:** no se usan variables globales ni listas o matrices heterogéneas.
 
## 2. Correcciones aplicadas
 
### 2.1 Devolución de la etapa 1
 
| Criterio observado | Estado en la etapa 1 | Cómo se resuelve en la etapa 2 |
|---|---|---|
| Regla del marcador (alcance y código distintos) | NO CUMPLE | Se documenta la regla que implementa el código: gana el primer equipo que llega a 13 rondas; el otro tiene de 0 a 12. El valor 13 se lee de `config["rondas_para_ganar"]` (puntos 5 y 10). |
| Estructura de partidos vs. alcance | NO CUMPLE | El alcance ya no declara una lista heterogénea ni `llaves_cuartos`. Las 7 listas paralelas homogéneas pasan a un diccionario de partidos por `id_partido` (punto 3). |
| Variables globales en `datos.py` | NO CUMPLE | `datos.py` desaparece. Los parámetros se leen de `configuracion.json` dentro de `main()` y viajan por parámetro en el diccionario `config` (punto 5). |
| Ruptura de ciclos (`continue`) | NO CUMPLE | No se usan `break` ni `continue`. Todo ciclo termina por su propia condición (por ejemplo, `while intentos < 3 and not autenticado`), y no se usa `return` dentro de un ciclo. |
| Funciones duplicadas / código de respaldo | NO CUMPLE | Cada función tiene una sola definición. No se entrega código de respaldo, versiones alternativas ni código comentado. |
| Listas homogéneas (filas del ranking) | NO CUMPLE | Cada registro del ranking es una tupla `(kda, codigo_jugador, nickname, codigo_equipo)`; el ranking es una lista de tuplas. |
| Modularización y responsabilidades | CUMPLE PARCIAL | `input()` y `print()` solo están en `main.py`. `operaciones.py`, `validaciones.py`, `reportes.py` y `archivos.py` reciben datos por parámetro y devuelven resultados o lanzan excepciones (punto 15). |
| Estado visible en el menú | CUMPLE PARCIAL | El encabezado y las opciones del menú cambian según el estado: inscripción abierta (con equipos registrados / 8), inscripción cerrada o torneo finalizado con su campeón (punto 13). |
| Nombre / nickname válido | CUMPLE PARCIAL | El nombre se normaliza con `strip()` y `lower()` antes de comparar y se guarda normalizado en memoria y en el CSV (punto 8). |
| Casos de prueba formales | NO CUMPLE | Se definen 23 pruebas unitarias, clasificadas en casos válidos, inválidos y límite (punto 14). |
 
### 2.2 Devolución del alcance de la etapa 2
 
| Observación | Dónde se resuelve |
|---|---|
| 1. Equipos de los partidos pendientes en `partidos.csv` | Punto 6.2: los partidos 1 a 4 se guardan con sus equipos desde que se genera el cuadro; solo los partidos 5, 6 y 7 quedan sin participantes hasta conocer a los ganadores. |
| 2. Consistencia entre CSV | Punto 6.3: tabla de combinaciones de archivos permitidas e inconsistentes, y controles de coherencia del contenido. |
| 3. Combinación `id_partido` + `codigo_jugador` duplicada | Puntos 6.4 y 7: se controla con un conjunto de tuplas al cargar un partido y al leer `estadisticas.csv`. |
| 4. Alerta A2 | Punto 10: la alerta se genera siempre que las bajas de un equipo sean distintas de las muertes del rival, por exceso o por defecto. |
| 5. Búsqueda recursiva sobre el diccionario | Punto 12: la búsqueda por nickname recibe `list(jugadores.values())`; la búsqueda por código es acceso directo al diccionario. La función sigue la estructura de la clase 13. |
| 6. Claves de `config["cuadro"]` | Punto 5: las claves se convierten a entero al cargar la configuración. |
| 7. Consistencia entre `equipos.csv` y `jugadores.csv` | Punto 6.5: los jugadores se escriben primero y el equipo después; si falla cualquiera de las dos escrituras, se deshace y no queda nada del equipo. |
| 8. Pruebas de archivos | Punto 14: seis pruebas de archivos y consistencia (`tests/test_archivos.py`). |
 
## 3. Cambios de estructuras respecto de la etapa 1
 
Cada estructura reemplazada resuelve una limitación concreta de la etapa 1.
 
| Elemento | Etapa 1 | Etapa 2 | Limitación que resuelve |
|---|---|---|---|
| Configuración | Constantes a nivel de módulo en `datos.py` | `configuracion.json` → diccionario `config` creado en `main()` | Eran variables globales y cambiar un umbral exigía modificar el código |
| Equipos | Lista de tuplas `(codigo_equipo, nombre_equipo)` | Diccionario `{codigo_equipo: registro}` | Buscar un equipo obligaba a recorrer la lista |
| Jugadores | Lista de tuplas `(codigo_jugador, nickname, codigo_equipo)` | Diccionario `{codigo_jugador: registro}` | Igual que equipos; además la posición en la lista era la que la relacionaba con la matriz |
| Partidos | 7 listas paralelas homogéneas (`partidos_id`, `partidos_fase`, ...) relacionadas por el índice `i` | Diccionario `{id_partido: registro}`, cada partido con sus campos por nombre | Los datos de un partido estaban repartidos en 7 listas; un error de índice mezclaba partidos |
| Estadísticas | `matriz_stats` 40 × 3 acumulada + lista paralela `partidos_por_jugador` | `estadisticas.csv`: una fila por jugador y partido; acumulados calculados en un diccionario por `codigo_jugador` | La matriz dependía del índice, perdía el detalle por partido y no se podía guardar con sentido |
| Nombres de columnas | Tupla `nombres_estadisticas` | Claves del diccionario (`"bajas"`, `"muertes"`, `"asistencias"`) | El dato se identifica por nombre, no por número de columna |
| Ranking | Filas `[kda, codigo, nickname, codigo_equipo]` (lista heterogénea) | Tuplas `(kda, codigo_jugador, nickname, codigo_equipo)` | Un registro fijo con tipos distintos se representa con una tupla |
| Validación de nombres | Comprobaciones manuales | Expresión regular + normalización | Regla del punto 5 de la etapa 1 en un patrón y una búsqueda |
| Errores | `operaciones.py` mostraba mensajes con `print` | Las validaciones lanzan `ValueError` con `raise`; `main.py` lo captura y muestra el mensaje | Separa la lógica de la interacción y permite probar las validaciones |
| Datos al salir | Se perdían | Se guardan en CSV y se reanudan | Requisito de persistencia |
| Acceso | Libre | Login con usuario y clave, con rol | Requisito obligatorio de la etapa |
| Informes | Solo en pantalla | Pantalla + archivos `.txt` | Reportes legibles fuera del programa |
 
## 4. Login de usuario
 
El programa no muestra el menú hasta que se ingresa un usuario y una clave que coincidan con una fila de `usuarios.csv`.
 
| Campo | Formato | Ejemplo |
|---|---|---|
| usuario | Expresión regular (punto 8) | `organizador` |
| clave | Expresión regular (punto 8) | `torneo2026` |
| rol | `organizador` o `espectador` | `organizador` |
 
- Se permiten **3 intentos**. El ciclo es `while intentos < 3 and not autenticado`; si termina sin autenticar, el programa informa y finaliza.
- Primero se valida el formato del usuario y la clave; recién después se compara contra el archivo. Así un formato inválido se informa como tal y no como "clave incorrecta".
- El usuario se normaliza a minúsculas antes de comparar; la clave se compara tal cual.
- `usuarios.csv` es **obligatorio**: si falta o no tiene filas válidas, el programa informa el error y termina. No se crea un usuario por defecto, porque eso abriría el sistema a cualquiera.
- **Roles:** el organizador accede a todo el menú. El espectador solo accede a consultas y reportes (punto 13).
- Las claves se guardan en texto plano por ser un trabajo académico.
 
## 5. Configuración (configuracion.json)
 
Los parámetros que en la etapa 1 estaban en `datos.py` se leen de `configuracion.json` al iniciar (se lee el texto y se convierte con `json.loads`, como en la clase 11) y se guardan en el diccionario `config`, que se crea dentro de `main()` y se pasa por parámetro a quien lo necesite.
 
```json
{
  "nombre_torneo": "Copa Programación I",
  "cantidad_equipos": 8,
  "jugadores_por_equipo": 5,
  "fases": ["Cuartos de Final", "Semifinal", "Final"],
  "cuadro": {"5": [1, 2], "6": [3, 4], "7": [5, 6]},
  "rondas_para_ganar": 13,
  "umbral_kda": 2.0,
  "umbral_clutch": 3.0,
  "umbral_kda_bajo": 0.5,
  "archivos": {
    "usuarios": "datos/usuarios.csv",
    "equipos": "datos/equipos.csv",
    "jugadores": "datos/jugadores.csv",
    "partidos": "datos/partidos.csv",
    "estadisticas": "datos/estadisticas.csv",
    "reporte_filtrado": "reportes/reporte_filtrado.txt",
    "reporte_general": "reportes/reporte_general.txt",
    "alertas": "reportes/alertas.txt"
  }
}
```
 
- **`cuadro`** expresa la progresión de los puntos 8 y 15 de la etapa 1: el partido 5 (Semifinal 1) recibe a los ganadores de 1 y 2, el 6 (Semifinal 2) a los de 3 y 4, y el 7 (Final) a los de 5 y 6.
- **Claves de `cuadro` como enteros:** en JSON las claves de un objeto siempre son texto (`"5"`, `"6"`, `"7"`), mientras que los `id_partido` del programa son enteros. Por eso, al cargar la configuración, la función `convertir_cuadro` arma un diccionario nuevo con las claves convertidas con `int()` y cada par de partidos convertido a tupla: `{5: (1, 2), 6: (3, 4), 7: (5, 6)}`. Desde ese momento el programa consulta siempre `config["cuadro"][5]`, con entero. Si una clave no se puede convertir o un valor no es un par de enteros, se lanza `ValueError` y el programa termina.
- **`rondas_para_ganar`** es el 13 de la regla del marcador (punto 13 de la etapa 1).
- **`fases`** llega como lista y se convierte a tupla con `tuple()`.
- **`umbral_kda_bajo`** es nuevo y alimenta la alerta de bajo rendimiento (punto 10).
- **Validación al cargar:** deben estar todas las claves, con el tipo correcto (enteros, números, lista de 3 fases, cuadro con las claves 5, 6 y 7).
- **Si falta o es inválido**, el programa informa qué clave o qué error encontró y termina. Nunca se reemplaza en silencio por valores por defecto.
- La única ruta escrita en el código es la de `configuracion.json`, como variable local de `main()`.
 
## 6. Archivos y persistencia
 
### 6.1 Archivos del sistema
 
El torneo se guarda en cinco CSV y se reconstruye completo al iniciar; los reportes salen en tres archivos de texto.
 
| Archivo | Propósito | Encabezado | Cuándo se escribe |
|---|---|---|---|
| `configuracion.json` | Parámetros del torneo | — | Nunca (solo lectura, obligatorio) |
| `usuarios.csv` | Login | `usuario;clave;rol` | Nunca (solo lectura, obligatorio) |
| `equipos.csv` | Equipos inscriptos | `codigo_equipo;nombre_equipo` | Al cerrar el alta de un equipo (punto 6.5) |
| `jugadores.csv` | Jugadores inscriptos | `codigo_jugador;nickname;codigo_equipo` | Junto con su equipo, antes que el equipo (punto 6.5) |
| `partidos.csv` | Estado del cuadro | `id_partido;fase;fecha;equipo_a;equipo_b;rondas_a;rondas_b;jugado` | Al generar el cuadro y al cargar cada resultado (se reescribe completo) |
| `estadisticas.csv` | Historial: una fila por jugador y partido | `id_partido;codigo_jugador;bajas;muertes;asistencias` | Al cargar un partido, 10 filas (punto 6.5) |
| `reporte_filtrado.txt` | Último reporte filtrado | — | Cada vez que se pide (modo `wt`) |
| `reporte_general.txt` | Informe general | — | Cada vez que se pide (modo `wt`) |
| `alertas.txt` | Alertas e incidencias de lectura | — | Al iniciar y al pedir reportes (modo `wt`) |
 
Ejemplo de `estadisticas.csv`:
 
```
id_partido;codigo_jugador;bajas;muertes;asistencias
2;J01;24;15;6
2;J02;18;17;4
```
 
### 6.2 Partidos guardados en partidos.csv
 
Al generar el cuadro se escriben las 7 filas de una vez. El sorteo queda guardado desde ese momento.
 
| Partidos | `equipo_a` / `equipo_b` | `rondas_a` / `rondas_b` | `fecha` | `jugado` |
|---|---|---|---|---|
| 1 a 4 (cuartos), pendientes | Los equipos del sorteo, **siempre completos** desde que se genera el cuadro | `-1` | vacía | `no` |
| 5 a 7 (semifinales y final), sin participantes todavía | `""` hasta que se conoce el ganador del partido que alimenta ese lugar | `-1` | vacía | `no` |
| Cualquiera, jugado | Los dos equipos | Marcador cargado | Fecha del partido | `si` |
 
Ejemplo de `partidos.csv` recién generado el cuadro:
 
```
id_partido;fase;fecha;equipo_a;equipo_b;rondas_a;rondas_b;jugado
1;Cuartos de Final;;E3;E7;-1;-1;no
2;Cuartos de Final;;E1;E5;-1;-1;no
3;Cuartos de Final;;E8;E2;-1;-1;no
4;Cuartos de Final;;E6;E4;-1;-1;no
5;Semifinal;;;;-1;-1;no
6;Semifinal;;;;-1;-1;no
7;Final;;;;-1;-1;no
```
 
Se mantiene la convención de la etapa 1 para lo que todavía no se conoce: equipo `""`, rondas `-1`, `jugado` en `False` en memoria (`no` en el archivo).
 
### 6.3 Consistencia entre archivos al iniciar
 
Antes de cargar el torneo se comprueba qué archivos existen (abriéndolos con `try/except FileNotFoundError`). Un CSV faltante solo se crea automáticamente cuando su ausencia es coherente con un estado posible del torneo: por ejemplo, si existen `partidos.csv` y `estadisticas.csv` pero falta `equipos.csv`, el torneo no se puede reconstruir y el programa no continúa.
 
| `equipos.csv` | `jugadores.csv` | `partidos.csv` | `estadisticas.csv` | Situación | Acción |
|---|---|---|---|---|---|
| No | No | No | No | Torneo nuevo | Se crean los cuatro con su encabezado |
| Sí | Sí | No | No | Inscripción en curso, cuadro sin generar | Se crean `partidos.csv` y `estadisticas.csv` con encabezado |
| Sí | Sí | Sí | No | Cuadro generado | Si ningún partido está jugado, se crea `estadisticas.csv`; si hay alguno jugado, es inconsistente |
| Sí | Sí | Sí | Sí | Torneo en curso o finalizado | Se carga y se verifica la coherencia del contenido |
| Cualquier otra combinación | | | | Inconsistente | Mensaje con el archivo faltante y fin del programa |
 
Ejemplos de combinaciones inconsistentes: falta `equipos.csv` o `jugadores.csv` y existe el otro; falta `partidos.csv` y existe `estadisticas.csv`; falta cualquiera de los dos primeros y existen partidos.
 
La decisión la toma una función pura, `verificar_combinacion_archivos`, que recibe qué archivos existen y si hay partidos jugados, y devuelve la situación. Así se puede probar sin archivos reales (prueba 22).
 
**Coherencia del contenido.** Aunque estén los archivos correctos, el programa no continúa si el contenido no permite reconstruir el torneo:
 
- Cada jugador referencia un equipo existente y cada equipo tiene exactamente 5 jugadores.
- Si `partidos.csv` tiene filas: hay exactamente 8 equipos y 7 partidos; los partidos 1 a 4 tienen dos equipos existentes y distintos, y cada equipo aparece en un solo cuarto.
- En los partidos 5 a 7, cada equipo es `""` o el ganador del partido que alimenta ese lugar según `config["cuadro"]`.
- Cada fila de `estadisticas.csv` corresponde a un partido existente y marcado como jugado, y a un jugador existente que pertenece a uno de los dos equipos de ese partido.
 
### 6.4 Filas inválidas y duplicadas
 
Un problema puntual en una fila no impide continuar: se descarta la fila, se registra la incidencia (archivo, número de línea, motivo) y el resto se carga normalmente.
 
- **Fila con formato inválido:** cantidad de campos distinta, un número que no convierte o un dato que no cumple su regex.
- **Combinación `id_partido` + `codigo_jugador` repetida en `estadisticas.csv`:** al leer el archivo se usa el conjunto `combinaciones_cargadas`, que guarda tuplas `(id_partido, codigo_jugador)`. Si la tupla ya está en el conjunto, la fila se descarta y se registra como incidencia. Así las estadísticas de un jugador nunca se acumulan dos veces en el mismo partido. Si al descartarla el partido queda sin sus 10 filas, además se genera la alerta A3.
- La misma regla se aplica al cargar un partido desde el menú: un jugador no puede cargarse dos veces en la planilla de un partido (punto 10).
 
### 6.5 Escritura consistente
 
Cada operación que modifica dos archivos se escribe en un orden fijo, y si la segunda escritura falla se deshace la primera. El estado en memoria se actualiza recién cuando las dos escrituras terminaron bien.
 
**Alta de un equipo:**
 
1. Se validan en memoria el nombre del equipo y sus 5 jugadores. Si algo falla, no se escribe nada.
2. Se agregan los 5 jugadores a `jugadores.csv` (modo `at`, una sola escritura con las 5 líneas).
3. Se agrega el equipo a `equipos.csv` (modo `at`).
4. Si falla el paso 2 o el 3 (`OSError`), se reescribe `jugadores.csv` completo desde la memoria (modo `wt`), que todavía no tiene a esos 5 jugadores. Así no quedan ni el equipo ni sus jugadores.
 
Como el equipo se escribe al final, nunca queda un equipo en `equipos.csv` sin sus jugadores. Y si se modificaran los archivos a mano, el control de coherencia del punto 6.3 lo detecta al iniciar.
 
**Carga de un partido:**
 
1. Se validan en memoria el marcador, la fecha y las 10 filas de estadísticas.
2. Se agregan las 10 filas a `estadisticas.csv` (modo `at`).
3. Se reescribe `partidos.csv` completo (modo `wt`) con el partido marcado como jugado y el ganador ubicado en el partido siguiente.
4. Si falla el paso 3, se reescribe `estadisticas.csv` desde la memoria, sin las 10 filas nuevas.
 
### 6.6 Reglas generales de persistencia
 
- Todos los archivos se abren con `with open(ruta, modo, encoding="utf-8")`, en modo `rt` (leer), `wt` (escribir desde cero) o `at` (agregar al final).
- **No se usa el módulo `csv`**, igual que en la clase 10. Para escribir, cada registro se arma concatenando los campos con `;` y agregando `"\n"`. Para leer, se recorre el archivo con `for linea in arch`, se hace `linea.rstrip("\n").split(";")` y con esos campos se arma el diccionario de registro a mano.
- La primera línea es el encabezado: se lee aparte y se compara con el esperado. Separador fijo `;`, mismo encabezado y mismo orden de campos siempre. Ningún nombre válido puede contener `;`, porque la regex lo impide.
- **Reanudación:** al iniciar, si `partidos.csv` tiene filas, el cuadro ya fue sorteado y la inscripción queda cerrada. El sorteo se conserva entre ejecuciones.
- **Carga en memoria:** la clase 10 recomienda no cargar todo un archivo en memoria. Acá se cargan completos porque los lineamientos piden leer el historial al iniciar y el volumen es mínimo: como máximo 8 equipos, 40 jugadores, 7 partidos y 70 filas de estadísticas.
 
## 7. Diccionarios y conjuntos
 
Cada fila de CSV se convierte en un diccionario; los totales se agrupan en diccionarios acumuladores; los conjuntos controlan valores únicos.
 
Diccionarios de registro (cada fila leída del CSV, con sus valores ya convertidos):
 
```python
equipo  = {"codigo_equipo": "E1", "nombre_equipo": "furia_cs"}
jugador = {"codigo_jugador": "J01", "nickname": "kscerato", "codigo_equipo": "E1"}
partido = {"id_partido": 2, "fase": "Cuartos de Final", "fecha": "10/10/2026",
           "equipo_a": "E1", "equipo_b": "E5", "rondas_a": 13, "rondas_b": 9, "jugado": True}
estadistica = {"id_partido": 2, "codigo_jugador": "J01", "bajas": 24, "muertes": 15, "asistencias": 6}
```
 
Colecciones indexadas por clave:
 
| Estructura | Clave | Valor |
|---|---|---|
| `usuarios` | usuario | `{"clave": ..., "rol": ...}` |
| `equipos` | `codigo_equipo` | registro de equipo |
| `jugadores` | `codigo_jugador` | registro de jugador |
| `partidos` | `id_partido` (entero, 1 a 7) | registro de partido |
| `estadisticas` | — | lista de registros de estadística (todos del mismo tipo: lista homogénea) |
 
Diccionarios acumuladores (se recalculan a partir de `estadisticas`, no se guardan):
 
| Acumulador | Clave | Valor | Uso |
|---|---|---|---|
| `stats_por_jugador` | `codigo_jugador` | `{"bajas", "muertes", "asistencias", "partidos"}` sumados | KDA, ranking, MVP, clutch (reemplaza a `matriz_stats` y `partidos_por_jugador`) |
| `bajas_por_equipo` | `codigo_equipo` | total de bajas | Equipo más letal |
| `partidos_por_fase` | fase | cantidad jugados / total | Resumen general |
 
Diccionario de configuración: `config`, cargado desde JSON (punto 5).
 
Conjuntos:
 
| Conjunto | Contenido | Para qué |
|---|---|---|
| `nicknames_registrados` | nicknames normalizados | Detectar duplicados al inscribir, sin recorrer la lista |
| `combinaciones_cargadas` | tuplas `(id_partido, codigo_jugador)` | Impedir que un jugador tenga dos filas en el mismo partido (punto 6.4) |
| `jugadores_con_partidos` | códigos que tienen al menos una fila en `estadisticas` | Filtrar para MVP y promedio ("al menos un partido jugado") |
| `equipos_eliminados` | perdedores de partidos jugados | Resumen general y validación de carga |
| `equipos_con_victoria` | ganadores de partidos jugados | Resumen de únicos |
| `jugadores_clutch` | KDA ≥ `umbral_clutch` | Destacarlos en el informe |
 
Los códigos de equipo (E1, E2, ...) y de jugador (J01, J02, ...) se generan secuencialmente, como en la etapa 1, por lo que no pueden repetirse por el flujo previsto; al leer los CSV se controla igualmente que no haya códigos repetidos.
 
El estado se agrupa en un diccionario `torneo` creado dentro de `main()` (`config`, `equipos`, `jugadores`, `partidos`, `estadisticas`, `usuario_actual`) y se pasa a cada función. No hay variables globales.
 
## 8. Expresiones regulares y validaciones
 
Se validan seis formatos con `re.match` y las anclas `^` y `$`, para que el patrón cubra el dato completo; la regex comprueba la estructura y, cuando corresponde, una segunda comprobación verifica que el valor exista o tenga sentido según la configuración. Solo se usan elementos vistos en la clase: clases de caracteres, rangos, cuantificadores `{m,n}`, anclas, `re.match` y `re.search`.
 
| Dato | Expresión regular | Segunda comprobación | Mensaje si falla |
|---|---|---|---|
| Código de equipo (al leer CSV) | `^E[0-9]{1,2}$` | Número entre 1 y `cantidad_equipos`; no repetido | "El código de equipo debe tener el formato E1 a E8" |
| Código de jugador (al leer CSV y al buscar) | `^J[0-9]{2}$` | Número entre 01 y `cantidad_equipos × jugadores_por_equipo`; no repetido | "El código de jugador debe tener el formato J01 a J40" |
| Nombre de equipo / nickname | `^[a-z0-9_]{3,20}$` | `re.search("[a-z]", nombre)` exige al menos una letra; no repetido (conjunto `nicknames_registrados`) | "Debe tener entre 3 y 20 caracteres: letras, números o guion bajo, con al menos una letra" |
| Fecha del partido | `^[0-9]{2}/[0-9]{2}/[0-9]{4}$` | Fecha real: mes entre 1 y 12 y día dentro de los días de ese mes (febrero con 29 en año bisiesto); rechaza 31/02/2026 | "La fecha debe tener el formato DD/MM/AAAA y ser una fecha válida" |
| Usuario (login) | `^[a-z][a-z0-9_]{3,15}$` | Existe en `usuarios` | "El usuario debe empezar con letra y tener entre 4 y 16 caracteres" |
| Clave (login) | `^[A-Za-z0-9]{6,20}$` | `re.search("[A-Za-z]", clave)` y `re.search("[0-9]", clave)`; coincide con la del usuario | "La clave debe tener entre 6 y 20 letras o números, con al menos una letra y un número" |
 
- **Regla de nombre válido (punto 5 de la etapa 1):** antes de validar se normaliza con `strip()` y `lower()`. Luego `^[a-z0-9_]{3,20}$` cubre longitud y caracteres permitidos (sin espacios ni símbolos), y `re.search("[a-z]", nombre)` exige al menos una letra, lo que descarta nombres vacíos, solo de números o solo de guiones bajos. **El valor que se guarda en memoria y en el CSV es el normalizado**: "Sniper", " sniper " y "SNIPER" son el mismo nombre.
- **Fecha real:** la función `validar_fecha` separa día, mes y año con `split("/")`, los convierte con `int()` y compara el día contra los días del mes. Para febrero, el año es bisiesto si es divisible por 4 y no por 100, o si es divisible por 400. Se resuelve con lo visto en clase, sin módulos externos.
- **Marcador (punto 13 de la etapa 1):** ambos valores enteros no negativos; exactamente uno es igual a `rondas_para_ganar` (13) y el otro está entre 0 y 12. Quedan rechazados el empate 13-13, los partidos no terminados (12-10) y los valores mayores a 13.
- **Datos numéricos** (rondas, bajas, muertes, asistencias): se convierten con `int()` dentro de `try/except ValueError`, y después se controlan las reglas (marcador, valores no negativos, reglas del punto 10).
- **Código de jugador en `estadisticas.csv`:** la función `leer_estadisticas(ruta)` solo recibe la ruta, no `config`, por lo que al leer cada fila controla únicamente el formato con `^J[0-9]{2}$` (`validar_formato_codigo_jugador`). Una fila que no lo cumple se descarta como incidencia (punto 6.4). Que el jugador exista y pertenezca a uno de los equipos del partido se controla después, con los jugadores ya cargados, en la coherencia del contenido (punto 6.3); si no se cumple, el programa informa el problema y termina. En `jugadores.csv` y al buscar por código, en cambio, `validar_codigo_jugador(codigo, config)` también comprueba el rango.
- **Forma de las funciones de validación:** reciben el dato (y `config` si lo necesitan), devuelven el valor normalizado y lanzan `ValueError` con el mensaje del formato esperado. No usan `input` ni `print`, para poder probarlas con pytest. Los patrones se definen dentro de cada función, no como variables de módulo.
 
## 9. Manejo de excepciones
 
Las validaciones lanzan `ValueError`; el acceso a archivos captura los errores de lectura y escritura; `main.py` captura todo lo anterior, muestra el mensaje y permite seguir operando cuando el error no impide continuar.
 
| Situación | Excepción | Dónde se captura | Comportamiento |
|---|---|---|---|
| Falta `configuracion.json` o `usuarios.csv` | `FileNotFoundError` | `main()` | Mensaje con la ruta esperada y fin del programa |
| JSON mal escrito | `ValueError` (lo lanza `json.loads`) | `main()` | Mensaje indicando que el archivo no tiene formato JSON válido; fin del programa |
| Falta una clave, tipo incorrecto o clave de `cuadro` no convertible | `KeyError` / `TypeError` / `ValueError`, relanzados con `raise ValueError(...)` | `validaciones.validar_configuracion` → `main()` | Mensaje con la clave; fin del programa |
| Falta un CSV de datos | `FileNotFoundError` | `archivos.py` | Se decide según la tabla del punto 6.3: se crea con encabezado o se informa la inconsistencia y se termina |
| Combinación de archivos o contenido inconsistente | `ValueError` | `main()` | Mensaje con el problema encontrado; fin del programa |
| Encabezado de CSV distinto del esperado | `ValueError` | `archivos.py` → `main()` | Mensaje y fin: no se adivina el orden de columnas |
| Fila con formato inválido o duplicada | `ValueError` | `archivos.py` (por fila) | Se descarta la fila, se registra la incidencia y se sigue con las demás |
| No se puede abrir o escribir un archivo (sin permisos, ruta inexistente) | `OSError` | `archivos.py` → `main()` | Se deshace la escritura anterior (punto 6.5) y se informa; el dato no se agrega al estado en memoria |
| Dato ingresado inválido (regex, marcador, duplicado, reglas del punto 10) | `ValueError` lanzado con `raise` | `main.py` | Mensaje con el formato esperado; se vuelve a pedir o se vuelve al menú |
| Número no numérico | `ValueError` de `int()` | `main.py` | Igual que el caso anterior |
| Búsqueda sin resultado | — (la función devuelve `None`) | `main.py` | "No se encontró el jugador / equipo" |
 
No se usan `except` vacíos ni `except Exception` genéricos: cada bloque captura las excepciones que espera. Se mantienen todas las validaciones obligatorias del punto 27 de la etapa 1: todos los errores muestran un mensaje comprensible y permiten continuar operando.
 
## 10. Reglas del dominio y condiciones críticas
 
Se mantienen todas las reglas de la etapa 1 y se agregan otras que solo tienen sentido ahora que existe un historial por partido.
 
Se mantienen sin cambios (numeración de la etapa 1): validación de equipo (4), nombre válido (5, ahora con regex y guardado normalizado), cierre de inscripción (6), sorteo con `random.shuffle` (7), progresión del cuadro (8 y 15, ahora desde `config["cuadro"]`), ganador automático (12), marcador a 13 rondas (13), carga única de partido (14), fórmula de KDA con el caso de 0 muertes (16), MVP con empate (17), equipo más letal (18), promedio de bajas (19), conteo con `umbral_kda` (20), jugador clutch con `umbral_clutch` (21), búsqueda (22), comprensión, slicing y lambda (23) y control de estado (26).
 
Reglas nuevas al cargar un partido:
 
1. **Muertes posibles.** Un jugador muere como máximo una vez por ronda: `muertes ≤ rondas_a + rondas_b`.
2. **Planilla completa y sin repetidos.** Se cargan exactamente 10 filas: los 5 jugadores de cada equipo del cruce, sin repetir ninguno (conjunto `combinaciones_cargadas`) ni incluir jugadores de otro equipo.
3. **Bajas y muertes cruzadas.** Las bajas totales de un equipo deben coincidir con las muertes totales del rival en ese partido. Si son distintas, por exceso o por defecto, la carga se rechaza.
4. **Fechas en orden.** La fecha de una semifinal o de la final no puede ser anterior a la de los partidos que la alimentan.
 
Condiciones críticas (alertas), detectadas recorriendo el historial completo al iniciar y al generar reportes:
 
| Código | Condición | Por qué es crítica |
|---|---|---|
| A1 | Jugador con más muertes que rondas en un partido | Dato imposible: el archivo fue editado a mano o cargado mal |
| A2 | En un partido, las bajas totales de un equipo son **distintas** de las muertes totales del rival (mayores o menores) | Las bajas de un equipo son las muertes del otro: si no coinciden, por exceso o por defecto, las cuentas no cierran |
| A3 | Partido marcado como jugado sin sus 10 filas de estadísticas | Historial incompleto: el KDA de esos jugadores queda mal |
| A4 | Jugador con al menos un partido y KDA acumulado menor que `umbral_kda_bajo` | Bajo rendimiento, contracara del jugador clutch |
| A5 | Filas descartadas al leer cualquier CSV (formato inválido o combinación duplicada) | Incidencia de lectura (archivo, línea y motivo) |
 
A1, A2 y A3 no deberían aparecer si los datos se cargaron por el programa, porque las reglas 1 a 3 lo impiden; existen para detectar archivos modificados por fuera.
 
## 11. Reportes
 
Los 6 informes finales de la etapa 1 (punto 25) se conservan en pantalla y se agregan cuatro reportes que además se escriben en archivos de texto.
 
| Reporte | Contenido | Archivo |
|---|---|---|
| Filtrado por equipo | Jugadores del equipo con bajas, muertes, asistencias, KDA y partidos jugados; resultado de cada partido del equipo | `reporte_filtrado.txt` |
| Filtrado por fase | Partidos de la fase elegida: cruce, fecha, marcador y ganador, o "pendiente" | `reporte_filtrado.txt` |
| Filtrado por fecha | Partidos jugados en una fecha (validada con regex) y el mejor KDA de cada uno | `reporte_filtrado.txt` |
| General | Los 6 informes de la etapa 1: cuadro, ranking, Top 3, MVP, equipo más letal y resumen (partidos jugados, equipos eliminados, promedio de bajas, jugadores con KDA > umbral, clutch) | `reporte_general.txt` |
| Alertas | Condiciones A1 a A5 del punto 10, agrupadas por código, con el detalle de cada caso | `alertas.txt` |
| Resumen de únicos | Cantidad y listado: jugadores distintos que jugaron, equipos con al menos una victoria, equipos eliminados, jugadores clutch (conjuntos del punto 7) | Dentro de `reporte_general.txt` |
 
- Cada archivo empieza con el nombre del torneo, el tipo de reporte y el filtro aplicado.
- Si el filtro no tiene resultados (por ejemplo, una fecha sin partidos) se informa así, en pantalla y en el archivo; no es un error.
- El cálculo de cada reporte está en `operaciones.py` y devuelve datos; `reportes.py` los convierte en líneas de texto; `archivos.py` los escribe; `main.py` los muestra. Así el cálculo se puede probar sin archivos ni pantalla.
 
## 12. Recursividad
 
La búsqueda de jugador por nickname (punto 22 de la etapa 1, opción 6 del menú) se implementa en forma recursiva. Cumple el punto 11 de los lineamientos: resuelve una operación real del proyecto, sobre una opción de menú y una colección pequeña, y es una búsqueda, uno de los usos recomendados.
 
**Sobre qué estructura trabaja.** La estructura principal `jugadores` es un diccionario por código. La función recursiva recibe una lista, que se arma con `list(jugadores.values())`:
 
- **Búsqueda por código:** acceso directo al diccionario, `jugadores[codigo]` (previa comprobación con `codigo in jugadores`). No usa recursión.
- **Búsqueda por nickname:** `buscar_jugador_recursivo(list(jugadores.values()), nickname)`. El nickname ingresado se normaliza con `strip()` y `lower()` antes de llamar, igual que al guardarlo.
 
**Construcción, según la clase 13.** La función sigue la estructura del ejemplo `sumaElementosRecursivoIndice(lista, i=0)`, "Recorrer una lista con índices": un parámetro `i` con valor por defecto 0 que indica qué elemento analizar, casos base que no se llaman a sí mismos y un caso recursivo que se llama con `i + 1`.
 
Versión iterativa (punto de partida). Como en cada ejemplo de la clase, primero se plantea con un ciclo. Sigue el modelo de `ordenadaAscendenteIterativa`: el `while` termina por su condición, sin `break` ni `return` dentro del ciclo.
 
```python
def buscar_jugador_iterativo(lista_jugadores, nickname):
    '''Retorna el registro del jugador con ese nickname, o None si no está. Iterativa.'''
    i = 0
    while i < len(lista_jugadores) and lista_jugadores[i]["nickname"] != nickname:
        i += 1
    if i == len(lista_jugadores):
        return None
    else:
        return lista_jugadores[i]
```
 
Versión recursiva (la que usa el programa):
 
```python
def buscar_jugador_recursivo(lista_jugadores, nickname, i=0):
    '''Retorna el registro del jugador con ese nickname, o None si no está. Recursiva.'''
    if i == len(lista_jugadores):
        return None
    elif lista_jugadores[i]["nickname"] == nickname:
        return lista_jugadores[i]
    else:
        return buscar_jugador_recursivo(lista_jugadores, nickname, i + 1)
```
 
| Pieza | Condición | Qué retorna |
|---|---|---|
| Caso base 1: se recorrió toda la lista | `i == len(lista_jugadores)` | `None` (no se encontró) |
| Caso base 2: se encontró | El jugador de la posición `i` tiene ese nickname | El registro del jugador |
| Caso recursivo | El jugador de la posición `i` no coincide | La búsqueda en el resto de la lista: `buscar_jugador_recursivo(lista_jugadores, nickname, i + 1)` |
 
Traza con una lista de 3 jugadores y un nickname que está en la posición 2:
 
```
buscar_jugador_recursivo(lista, "kscerato", 0)  → no coincide → llama con i = 1
buscar_jugador_recursivo(lista, "kscerato", 1)  → no coincide → llama con i = 2
buscar_jugador_recursivo(lista, "kscerato", 2)  → coincide → retorna el registro (caso base 2)
```
 
Con un nickname que no está, la cuarta llamada recibe `i = 3`, que es igual a `len(lista)`, y retorna `None` (caso base 1).
 
- **Qué ocurre en cada llamada:** cada llamada compara un solo jugador, el de la posición `i`, y si no coincide se llama de nuevo con `i + 1`, es decir, con un problema más pequeño: queda un jugador menos por revisar.
- **Por qué termina (condición de seguridad):** `i` empieza en 0 y crece de a 1 en cada llamada, así que siempre alcanza `len(lista_jugadores)`, el caso base 1. Con una lista vacía termina en la primera llamada. Nunca se produce `RecursionError` (`maximum recursion depth exceeded`), que aparece cuando el caso base no se alcanza.
- **Por qué se eligió recursiva:** la clase aclara que ninguna versión es mejor que la otra. Acá la búsqueda se expresa naturalmente como "este jugador o el resto de la lista", y la colección es pequeña (como máximo 40 jugadores, 40 llamadas). Cumple el uso responsable que piden los lineamientos: es la única función recursiva y el resto del programa sigue usando ciclos.
- **Prueba unitaria:** la prueba 15 verifica que encuentre un nickname existente y que retorne `None` con uno inexistente.
 
## 13. Menú principal y control de estado
 
El menú de la etapa 1 (punto 24) se conserva y suma dos opciones de reportes; cada opción se habilita según el rol del usuario y el estado del torneo.
 
| Opción | Organizador | Espectador | Condición de estado |
|---|---|---|---|
| 1. Registrar equipo (con sus 5 jugadores) | Sí | No | Inscripción abierta y menos de 8 equipos |
| 2. Listar equipos y jugadores | Sí | Sí | — |
| 3. Generar cuadro de cuartos de final (sorteo) | Sí | No | 8 equipos registrados y cuadro no generado |
| 4. Consultar cuadro del torneo | Sí | Sí | — |
| 5. Cargar resultado y estadísticas de un partido | Sí | No | Cuadro generado; partido con ambos equipos definidos y no jugado |
| 6. Buscar jugador / equipo | Sí | Sí | — |
| 7. Consultar rankings (general y Top 3) | Sí | Sí | Al menos un partido jugado |
| 8. Consultar estadísticas e informes (MVP, equipo más letal, resumen, únicos) | Sí | Sí | Al menos un partido jugado |
| 9. Reporte filtrado (equipo / fase / fecha) → `.txt` | Sí | Sí | Cuadro generado |
| 10. Reporte general y alertas → `.txt` | Sí | Sí | — |
| 0. Salir | Sí | Sí | — |
 
- **Estado reconstruido al iniciar:** inscripción abierta si `partidos.csv` no tiene filas; torneo en curso si hay cuadro y la final no está jugada; torneo finalizado si el partido 7 está jugado.
- **Estado visible en el texto del menú** (observación de la etapa 1): el encabezado muestra el usuario, su rol y el estado, por ejemplo "Inscripción abierta: 5/8 equipos", "Inscripción cerrada — Torneo en curso" o "Torneo finalizado — Campeón: furia_cs". Las opciones no habilitadas se muestran marcadas como "(no disponible)" junto con el motivo, por ejemplo "1. Registrar equipo (no disponible: inscripción cerrada)".
- Una opción no habilitada no ejecuta nada: muestra el motivo y vuelve al menú. Se mantienen todas las restricciones del punto 26 de la etapa 1.
- El menú se repite con `while opcion != "0"`, sin `break`.
- Al salir no hace falta guardar: cada cambio ya se escribió en el momento en que se confirmó.
 
## 14. Pruebas unitarias
 
Se definen 23 pruebas unitarias automatizadas con pytest, que cubren los 7 casos mínimos del punto 10 de los lineamientos y las observaciones de la devolución. Además, responden a la observación de la etapa 1 sobre casos de prueba formales: cada prueba indica si es un caso válido, inválido o límite. Siguen lo visto en la clase 12:
 
- **Dos tipos de archivo:** el código que se prueba (`validaciones.py`, `operaciones.py`, `archivos.py`) y los archivos de pruebas, que importan las funciones con `from validaciones import validar_nombre`.
- **Nombres:** pytest reconoce archivos con prefijo `test_` y funciones con prefijo `test_`. Hay tres archivos: `tests/test_validaciones.py`, `tests/test_operaciones.py` y `tests/test_archivos.py`.
- **Comprobación con `assert`:** cada prueba llama a una función con datos conocidos y verifica con `assert` que el valor obtenido sea el esperado, con un mensaje que explica la expectativa.
- **Sin `input` ni `print`:** las pruebas no piden datos ni dependen de lo que se muestra por pantalla, como exigen los lineamientos. Por eso las funciones probadas reciben todo por parámetro y devuelven un resultado.
- **Datos de prueba propios:** cada prueba arma sus diccionarios chicos escritos a mano, así no depende de los archivos de demostración.
 
### 14.1 Validaciones y reglas (tests/test_validaciones.py)
 
| # | Tipo | Caso exigido / observación | Prueba | Función probada | Entrada | Resultado esperado |
|---|---|---|---|---|---|---|
| 1 | Válido | Validación correcta | `test_nombre_valido_se_normaliza` | `validar_nombre` | `"  KSCerato "` | `"kscerato"` |
| 2 | Inválido | Validación incorrecta con excepción | `test_nombre_sin_letras_lanza_error` | `validar_nombre` | `"___"` | Se lanza `ValueError` |
| 3 | Inválido | Validación incorrecta con excepción | `test_fecha_inexistente_lanza_error` | `validar_fecha` | `"31/02/2026"` | Se lanza `ValueError` |
| 4 | Inválido | Validación incorrecta con excepción | `test_empate_lanza_error` | `validar_marcador` | `13, 13` | Se lanza `ValueError` |
| 5 | Límite | Valor exactamente igual al límite | `test_marcador_13_a_12_es_valido` | `validar_marcador` | `13, 12, 13` | Se acepta, sin excepción |
| 6 | Válido | Devolución etapa 2, punto 6 | `test_cuadro_con_claves_enteras` | `convertir_cuadro` | `{"5": [1, 2], "6": [3, 4], "7": [5, 6]}` | `{5: (1, 2), 6: (3, 4), 7: (5, 6)}` |
 
### 14.2 Cálculos y reglas del negocio (tests/test_operaciones.py)
 
| # | Tipo | Caso exigido / observación | Prueba | Función probada | Entrada | Resultado esperado |
|---|---|---|---|---|---|---|
| 7 | Válido | Cálculo simple con resultado conocido | `test_calcular_kda` | `calcular_kda` | bajas 20, muertes 10, asistencias 5 | `2.5` |
| 8 | Límite | Caso de 0 muertes | `test_kda_sin_muertes` | `calcular_kda` | bajas 10, muertes 0, asistencias 4 | `14` |
| 9 | Válido | Cálculo simple con resultado conocido | `test_determinar_ganador` | `determinar_ganador` | partido E1 13 – E5 9 | `"E1"` |
| 10 | Válido | Acumulación por clave | `test_acumular_stats_por_jugador` | `acumular_stats_por_jugador` | 3 registros de 2 jugadores | Diccionario con las sumas por código de jugador |
| 11 | Válido | Acumulación por clave | `test_bajas_por_equipo` | `bajas_por_equipo` | Registros de 2 equipos | Diccionario con el total de bajas por código de equipo |
| 12 | Válido | Devolución etapa 2, punto 1 | `test_cuadro_guarda_equipos_de_cuartos` | `generar_partidos` | 8 códigos de equipo ya sorteados | Partidos 1 a 4 con sus dos equipos; partidos 5 a 7 con `""` |
| 13 | Inválido | Detección de condición crítica | `test_detecta_muertes_imposibles` | `detectar_alertas` | Jugador con 30 muertes en un partido 13 – 9 (22 rondas) | La lista de alertas incluye A1 |
| 14 | Inválido | Condición crítica; devolución etapa 2, punto 4 | `test_alerta_a2_por_defecto` | `detectar_alertas` | Un equipo con 40 bajas y el rival con 42 muertes | La lista de alertas incluye A2 |
| 15 | Válido | Función recursiva | `test_busqueda_recursiva` | `buscar_jugador_recursivo` | Lista de 3 jugadores; un nickname que existe y otro que no | El registro del jugador; `None` |
| 16 | Límite | Valor exactamente igual al límite | `test_kda_igual_al_umbral_es_clutch` | `es_clutch` | KDA 3.0, umbral 3.0 | `True` |
| 17 | Límite | Colección vacía | `test_historial_vacio` | `obtener_mvp` y `promedio_bajas` | Historial vacío | `[]` y `0` |
 
### 14.3 Archivos y consistencia (tests/test_archivos.py)
 
Estas pruebas usan la carpeta `tests/archivos_prueba/`, que forma parte del repositorio. Cada prueba prepara su archivo escribiéndolo con modo `wt` al empezar, así se puede ejecutar todas las veces que se quiera con el mismo resultado.
 
| # | Tipo | Caso exigido / observación | Prueba | Función probada | Entrada | Resultado esperado |
|---|---|---|---|---|---|---|
| 18 | Inválido | Archivo inexistente | `test_leer_archivo_inexistente_lanza_error` | `leer_estadisticas` | Ruta `tests/archivos_prueba/no_existe.csv` (nunca se crea) | Se lanza `FileNotFoundError` |
| 19 | Válido | Persistencia: escribir y recuperar | `test_guardar_y_leer_estadisticas` | `guardar_estadisticas` y `leer_estadisticas` | 2 registros | Se leen los mismos 2 registros, con los números como enteros |
| 20 | Inválido | Fila incorrecta sin perder las válidas | `test_fila_invalida_se_descarta` | `leer_estadisticas` | Archivo con 2 filas válidas y una con `"diez"` en bajas | 2 registros y 1 incidencia |
| 21 | Inválido | Devolución etapa 2, punto 3 | `test_combinacion_duplicada_se_descarta` | `leer_estadisticas` | Archivo con dos filas `1;J01;...` | 1 registro y 1 incidencia |
| 22 | Inválido / válido | Devolución etapa 2, punto 2 | `test_combinaciones_de_archivos` | `verificar_combinacion_archivos` | Faltan equipos y existen partidos y estadísticas; y no existe ningún archivo | `"inconsistente"`; `"torneo_nuevo"` |
| 23 | Inválido | Devolución etapa 2, punto 7 | `test_alta_equipo_con_falla_no_deja_el_equipo` | `registrar_equipo_en_archivos` | `equipos.csv` de prueba solo con encabezado y ruta de jugadores en una carpeta inexistente | Se lanza `OSError` y `equipos.csv` sigue solo con el encabezado |
 
Ejemplo de un cálculo simple (`tests/test_operaciones.py`):
 
```python
from operaciones import calcular_kda
 
def test_calcular_kda():
    assert calcular_kda(20, 10, 5) == 2.5, "Con 20 bajas, 10 muertes y 5 asistencias el KDA debería ser 2.5"
```
 
Pruebas que esperan una excepción (casos 2, 3, 4, 18 y 23). Se combinan `try/except` (clase 5) con `assert` (clase 12): si la función lanza la excepción esperada, la bandera queda en `True` y la prueba pasa; si no la lanza, el `assert` falla.
 
```python
from validaciones import validar_nombre
 
def test_nombre_sin_letras_lanza_error():
    hubo_error = False
    try:
        validar_nombre("___")
    except ValueError:
        hubo_error = True
    assert hubo_error, "Un nombre sin letras debería lanzar ValueError"
```
 
Ejemplo de prueba de archivos (`tests/test_archivos.py`):
 
```python
from archivos import leer_estadisticas
 
def test_combinacion_duplicada_se_descarta():
    ruta = "tests/archivos_prueba/estadisticas_duplicada.csv"
    with open(ruta, "wt", encoding="utf-8") as arch:
        arch.write("id_partido;codigo_jugador;bajas;muertes;asistencias\n")
        arch.write("1;J01;24;15;6\n")
        arch.write("1;J01;24;15;6\n")
    registros, incidencias = leer_estadisticas(ruta)
    assert len(registros) == 1, "La combinación repetida no debería cargarse dos veces"
    assert len(incidencias) == 1, "La fila repetida debería registrarse como incidencia"
```
 
Ejecución. Se instala la librería una vez con `pip install pytest`. Luego, se ejecuta `python -m pytest -v`: la clase 12 recomienda esta forma para evitar problemas de PATH, y `-v` muestra el resultado de cada prueba.
 
```
python -m pytest -v
 
tests/test_archivos.py::test_leer_archivo_inexistente_lanza_error PASSED
tests/test_archivos.py::test_guardar_y_leer_estadisticas PASSED
...
tests/test_validaciones.py::test_cuadro_con_claves_enteras PASSED
# Resultado esperado de referencia:
# 23 passed
```
 
Evidencia para la entrega. Los lineamientos piden "Resultados de pruebas: evidencia de ejecución y explicación de los casos cubiertos". Se entrega la salida completa de `python -m pytest -v` junto con las tablas anteriores, que explican qué caso cubre cada prueba. Si una prueba falla, pytest muestra qué esperaba y qué obtuvo (por ejemplo, `assert 7 == 5`): se lee el fallo, se corrige el código y se vuelve a ejecutar hasta obtener `23 passed`.
 
## 15. Datos de demostración
 
Se entregan cargados para poder probar todo sin tipear:
 
- `usuarios.csv`: un organizador y un espectador.
- 8 equipos y 40 jugadores válidos, con nombres ya normalizados.
- Cuadro sorteado con los 4 cuartos y la Semifinal 1 jugados, en al menos dos fechas distintas: alcanza para probar filtros por equipo, fase y fecha, y deja la Semifinal 2 y la Final para cargar en vivo.
- Al menos un jugador clutch (KDA ≥ 3.0) y uno de bajo rendimiento (KDA < 0.5).
- Una copia aparte, `datos_alertas/`, con filas alteradas a mano para disparar A1, A2 (por exceso y por defecto), A3 y A5 (incluida una combinación duplicada), sin ensuciar los datos principales. Se usa cambiando las rutas en una copia de `configuracion.json`.
 
---
## Estructuras de datos — resumen final
 
| Estructura | Contenido | Tipo | Origen |
|---|---|---|---|
| `config` | Parámetros del torneo y rutas; `cuadro` con claves enteras | Diccionario | `configuracion.json` |
| `usuarios` | `{usuario: {clave, rol}}` | Diccionario de diccionarios | `usuarios.csv` |
| `equipos` | `{codigo_equipo: registro}` × 8 | Diccionario de diccionarios | `equipos.csv` |
| `jugadores` | `{codigo_jugador: registro}` × 40 | Diccionario de diccionarios | `jugadores.csv` |
| `partidos` | `{id_partido: registro}` × 7 | Diccionario de diccionarios | `partidos.csv` |
| `estadisticas` | Una fila por jugador y partido | Lista homogénea de diccionarios | `estadisticas.csv` |
| `stats_por_jugador` | Sumas por `codigo_jugador` | Diccionario acumulador | Calculado |
| `bajas_por_equipo` | Total por `codigo_equipo` | Diccionario acumulador | Calculado |
| `partidos_por_fase` | Jugados / total por fase | Diccionario acumulador | Calculado |
| `nicknames_registrados`, `jugadores_con_partidos`, `equipos_eliminados`, `equipos_con_victoria`, `jugadores_clutch` | Valores únicos | Conjuntos | Calculados |
| `combinaciones_cargadas` | `(id_partido, codigo_jugador)` | Conjunto de tuplas | Calculado |
| ranking | `(kda, codigo_jugador, nickname, codigo_equipo)` | Lista de tuplas | Calculado |
| `fases` | `("Cuartos de Final", "Semifinal", "Final")` | Tupla fija | `config["fases"]` |
| `torneo` | Agrupa todo lo anterior para pasarlo por parámetro | Diccionario | Creado en `main()` |
 
## Módulos
 
```
proyecto_etapa2/
├── main.py            # main(), login, menú, estado del torneo; único módulo con input() y print()
├── operaciones.py     # sorteo, carga de partidos, progresión, KDA, acumuladores,
│                      # MVP, más letal, rankings, búsquedas (incl. recursiva), alertas
├── validaciones.py    # regex, marcador, reglas de equipo y de partido, validación de config
├── reportes.py        # arma las líneas de texto de cada reporte a partir de los datos
├── archivos.py        # lectura/escritura de JSON, CSV y TXT; consistencia entre archivos
├── configuracion.json
├── datos/
│   ├── usuarios.csv
│   ├── equipos.csv
│   ├── jugadores.csv
│   ├── partidos.csv
│   └── estadisticas.csv
├── datos_alertas/     # copia con filas alteradas para probar alertas
├── reportes/
│   ├── reporte_filtrado.txt
│   ├── reporte_general.txt
│   └── alertas.txt
├── tests/
│   ├── archivos_prueba/       # archivos que preparan las pruebas 18 a 23
│   ├── test_validaciones.py   # pruebas 1 a 6
│   ├── test_operaciones.py    # pruebas 7 a 17
│   └── test_archivos.py       # pruebas 18 a 23
└── README.md
```
 
- `main` usa a todos; `operaciones` usa `validaciones`; `reportes` y `archivos` no dependen de `main`. Ningún módulo de lógica importa `main`.
- `datos.py` desaparece porque su contenido pasa a `configuracion.json`.
- Cada función tiene una única definición; el código entregado no incluye versiones de respaldo ni código comentado.
 
## Fuera de alcance (Etapa 2)
 
- Modificar o dar de baja equipos y jugadores ya registrados.
- Partido por el tercer puesto, prórrogas y desempate del MVP.
- Corrección de un resultado de partido ya cargado.
- Alta, baja o modificación de usuarios desde el programa (se editan en `usuarios.csv`).
- Cifrado de claves.
 