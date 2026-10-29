# Simulador de Planificación de Procesos y Asignación de Memoria

Proyecto desarrollado para la materia **Sistemas Operativos**.

El objetivo es simular el funcionamiento de un sistema operativo con planificación de procesos a corto plazo y administración de memoria mediante **particiones variables**.

El simulador trabaja con una única CPU y permite observar la evolución de los procesos, su asignación en memoria y las métricas finales obtenidas durante la ejecución.

---

## Características principales

- Lectura de procesos desde un archivo CSV.
- Máximo de 10 procesos por simulación.
- Estados manejados:
  - NUEVO
  - LISTO
  - LISTO_SUSPENDIDO
  - EJECUCION
  - TERMINADO
- Máximo de 5 procesos activos entre:
  - EJECUCION
  - LISTO
  - LISTO_SUSPENDIDO
- Planificación de CPU mediante **SRTF (Shortest Remaining Time First)**.
- Desempate SRTF por:
  1. Menor tiempo de irrupción restante.
  2. Menor tiempo de arribo.
  3. Menor ID.
- Administración de memoria mediante **particiones variables (MVT)**.
- Política de asignación **Best-Fit**.
- Liberación y fusión de huecos contiguos.
- Visualización de fragmentación externa.
- Reportes ante eventos de arribo y finalización.
- Cálculo de métricas finales.
- Validación de errores en los datos de entrada.

---

## Memoria

El simulador considera una memoria total distribuida de la siguiente manera:

- **100 KB** reservados para el Sistema Operativo.
- **450 KB** disponibles para los procesos de usuario.

La memoria de usuario comienza en la dirección `100` y finaliza en la dirección `549`.

La asignación se realiza mediante **Best-Fit**, seleccionando el hueco libre más pequeño donde pueda ingresar el proceso.

Cuando un proceso termina, su memoria es liberada y los huecos libres contiguos son fusionados.

---

## Planificación SRTF

El algoritmo utilizado para asignar la CPU es **Shortest Remaining Time First (SRTF)**.

Cuando aparece un proceso listo con menor tiempo de ejecución restante que el proceso actualmente en CPU, se produce una expropiación.

El proceso expropiado vuelve al estado `LISTO`, permaneciendo cargado en memoria.

---

## Archivo de entrada

Los procesos se cargan desde:

```text
procesos.csv
```

El archivo debe contener las siguientes columnas:

```csv
id,tam,ta,ti
```

Donde:

- `id`: identificador del proceso.
- `tam`: tamaño del proceso en KB.
- `ta`: tiempo de arribo.
- `ti`: tiempo de irrupción.

Ejemplo:

```csv
id,tam,ta,ti
1,200,0,8
2,150,1,5
3,100,2,2
4,180,3,4
5,80,4,1
```

---

## Validaciones

Antes de comenzar la simulación se verifica que los datos sean válidos.

Entre los controles realizados se encuentran:

- Archivo CSV inexistente.
- Archivo vacío.
- Columnas incorrectas.
- Campos vacíos.
- Valores no numéricos.
- IDs repetidos.
- IDs menores o iguales a cero.
- Tamaños menores o iguales a cero.
- Procesos mayores a 450 KB.
- Tiempo de arribo negativo.
- Tiempo de irrupción menor o igual a cero.
- Más de 10 procesos.

Si se encuentra algún error, el simulador informa el problema y detiene la ejecución.

---

## Reportes

Durante la simulación se muestra información cuando ocurre alguno de los siguientes eventos:

- Arribo de un proceso.
- Finalización de un proceso.

En cada evento se informa:

- Proceso actualmente en CPU.
- Cola de procesos listos.
- Procesos listos/suspendidos.
- Estado de las particiones de memoria.
- Memoria libre.
- Cantidad de huecos libres.
- Tamaño del mayor hueco.
- Fragmentación externa.

La simulación se pausa en cada evento hasta que el usuario presiona `ENTER`.

---

## Métricas finales

Al finalizar la simulación se calculan:

### Tiempo de retorno

```text
Tiempo de retorno = Tiempo de finalización - Tiempo de arribo
```

### Tiempo de espera

```text
Tiempo de espera = Tiempo de retorno - Tiempo de irrupción
```

También se muestran:

- Promedio de tiempo de retorno.
- Promedio de tiempo de espera.
- Throughput del sistema.

### Throughput

Representa la cantidad de procesos terminados por unidad de tiempo:

```text
Throughput = Procesos terminados / Tiempo total de simulación
```

---

## Ejecución

El proyecto requiere **Python 3**.

Para ejecutar el simulador:

```bash
python simulador.py
```

El archivo `procesos.csv` debe encontrarse en la misma carpeta que `simulador.py`.

---

## Estructura del proyecto

```text
proyecto-sistemas-operativos/
│
├── simulador.py
├── procesos.csv
├── README.md
└── .gitignore
```

---

## Tecnologías utilizadas

- Python
- CSV
- Git
- GitHub

---

## Proyecto académico

Trabajo Práctico Integrador desarrollado para la materia **Sistemas Operativos**, enfocado en la simulación de planificación de procesos y administración de memoria.