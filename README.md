# Simulador de Planificación de Procesos y Asignación de Memoria

Proyecto desarrollado para la materia **Sistemas Operativos** (UTN FRRe, 2026) por el **Grupo N° 4**.

El objetivo es simular un sistema operativo con planificación de procesos a corto plazo y administración de memoria mediante **particiones variables (MVT)**, sobre un único procesador. Permite observar la evolución de los procesos, su ubicación en memoria y las métricas finales de la simulación.

---

## Características principales

- Lectura de procesos desde un archivo CSV elegido por el usuario.
- Máximo de 10 procesos por simulación.
- Estados manejados: `NUEVO`, `LISTO`, `LISTO_SUSPENDIDO`, `EJECUCION` y `TERMINADO`.
- Grado máximo de multiprogramación: **5 procesos** entre Ejecución, Listos y Listos/Suspendidos.
- Planificación de CPU mediante **SRTF (Shortest Remaining Time First)**.
- Administración de memoria con **particiones variables (MVT)** y política **Best-Fit**.
- Liberación de memoria y fusión de huecos contiguos.
- Visualización de la tabla de particiones y de la fragmentación externa.
- Reportes ante cada evento de arribo y de finalización de un proceso.
- Cálculo de métricas finales.
- Validación de los datos de entrada.

---

## Colas y CPU

El sistema maneja tres colas y un recurso:

| Elemento | Contenido |
|---|---|
| **Nuevos** | Procesos que solicitaron ingreso y todavía no fueron admitidos. |
| **Listos** | Procesos con memoria asignada, esperando la CPU. |
| **Listos/Suspendidos** | Procesos listos para ejecutar que todavía no consiguieron memoria. |
| **CPU** | Proceso en ejecución, o CPU ociosa. No es una cola. |

---

## Memoria

- **100 KB** reservados para el Sistema Operativo (direcciones 0 a 99).
- **450 KB** para procesos de usuario (direcciones 100 a 549).

La asignación usa **Best-Fit**: se elige el hueco libre más pequeño donde entre el proceso, y el sobrante queda como un nuevo hueco. Cuando un proceso termina, su partición se libera y se fusiona con los huecos libres adyacentes.

---

## Planificación SRTF

La CPU se asigna al proceso listo con menor tiempo de irrupción restante. Ante empates se desempata por:

1. Menor tiempo de irrupción restante.
2. Menor tiempo de arribo.
3. Menor ID.

Si aparece un proceso listo que gana con ese criterio al que está en CPU, se produce una **expropiación**: el proceso desalojado vuelve a la cola de `LISTO` y **conserva su memoria** (la expropiación no implica suspensión).

Si no hay procesos listos, la CPU queda ociosa y el reloj avanza sin descontar tiempo de irrupción.

---

## Admisión de procesos y política de Listos/Suspendidos

- Un proceso arriba cuando `TA <= reloj`. Varios procesos pueden llegar al mismo instante.
- Se admite si hay cupo (menos de 5 procesos activos). Si no hay cupo, **permanece en Nuevos** y se reconsidera cuando se libere un lugar, aunque ya haya pasado su instante de arribo.
- Si hay cupo pero no entra en memoria por Best-Fit, pasa a **Listos/Suspendidos**.
- Cuando un proceso termina y libera memoria, se **recorre toda la cola de Listos/Suspendidos en orden de llegada**: cada proceso que entra por Best-Fit pasa a Listos y los que no entran siguen esperando. Así se aprovecha mejor la memoria disponible; la contrapartida es que un proceso grande puede esperar más tiempo.
- Los suspendidos se reconsideran **antes** que los procesos de Nuevos, porque llegaron antes.

---

## Archivo de entrada

El simulador **solicita la ruta del archivo CSV** al iniciar (se puede pegar la ruta completa, con o sin comillas). El archivo debe contener, por cada proceso: identificador, tamaño, tiempo de arribo (TA) y tiempo de irrupción (TI).

Ejemplo:

```csv
Proceso,TA,TI,Tamaño (K)
P1,3,2,120
P2,10,4,130
P3,10,1,40
P4,14,2,60
P5,20,2,90
```

- Los identificadores pueden escribirse como `1` o como `P1`.
- El orden de las columnas es libre, siempre que los nombres permitan identificarlas. También se aceptan los encabezados `id`, `tam`, `ta`, `ti`.
- Tamaño, TA y TI deben ser números enteros.

---

## Validaciones

Antes de comenzar la simulación se verifica que los datos sean válidos:

- Archivo inexistente, sin permisos de acceso o vacío.
- Columnas no reconocidas.
- Campos vacíos.
- Valores no numéricos.
- IDs repetidos o menores o iguales a cero.
- Tamaños menores o iguales a cero.
- Procesos de más de 450 KB.
- Tiempo de arribo negativo.
- Tiempo de irrupción menor o igual a cero.
- Más de 10 procesos.

Si se encuentra algún error, el simulador informa el problema y detiene la ejecución, esperando un `ENTER` antes de cerrarse para que el mensaje pueda leerse.

---

## Reportes

Se muestra el estado del sistema cada vez que ocurre un **arribo** o la **finalización** de un proceso. El reporte refleja el estado en el instante del evento, antes de ejecutar la unidad de CPU de ese instante. Incluye:

- **Estado de la CPU:** proceso en ejecución y su TI restante, o CPU ociosa.
- **Cola de Listos** con el TI restante de cada proceso.
- **Cola de Listos/Suspendidos** con el tamaño de cada proceso.
- **Tabla de particiones:** ID, inicio, fin, tamaño, estado, proceso asignado y fragmentación.
- Memoria libre, cantidad de huecos, mayor hueco y fragmentación externa.

La simulación se pausa en cada reporte hasta que el usuario presiona `ENTER`, por lo que no hay corridas ininterrumpidas.

---

## Métricas finales

Los tiempos se miden tomando como referencia el **instante en que el proceso entra a la cola de Listos** (`T_listo`), no su arribo a Nuevos ni a Listos/Suspendidos:

```text
T_listo = instante en que el proceso entra por primera vez a Listos
          (directo desde Nuevos, o desde Listos/Suspendidos al conseguir memoria)

Tiempo de retorno = Tiempo de finalización - T_listo
Tiempo de espera  = Tiempo de retorno - Tiempo de irrupción
```

También se muestran:

- Promedio de tiempo de retorno.
- Promedio de tiempo de espera.
- **Throughput:** `Procesos terminados / Tiempo total de simulación`.

---

## Ejecución

### Desde el ejecutable

Ejecutar `simulador.exe` y seguir las instrucciones en pantalla (ver `HOWTO.txt`).

### Desde el código fuente

Requiere **Python 3** y la librería **colorama** (colores en consola):

```bash
pip install colorama
python simulador.py
```

El programa pedirá la ruta del archivo CSV con los procesos.

---

## Casos de prueba

Con los lotes de prueba de la cátedra:

- Los lotes 1 a 4 se simulan completos.
- El lote 5 es rechazado por la validación (un proceso de 451 KB supera los 450 KB disponibles).
- El lote 6 es rechazado por la validación (12 procesos, el máximo es 10).

---

## Estructura del proyecto

```text
proyecto-sistemas-operativos/
│
├── simulador.py
├── HOWTO.txt
├── procesos.csv
├── README.md
└── .gitignore
```

---

## Tecnologías utilizadas

- Python 3
- colorama
- CSV
- Git y GitHub

---

## Uso de IA

> *Completar según la normativa de UTN: indicar si se utilizó IA, de qué manera y cuál fue el rol del equipo en esa interacción.*

---

## Proyecto académico

Trabajo Práctico Integrador desarrollado para la materia **Sistemas Operativos**, enfocado en la simulación de planificación de procesos y administración de memoria.
