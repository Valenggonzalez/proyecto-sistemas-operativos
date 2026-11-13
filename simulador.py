import csv
import os
import unicodedata

from colorama import Fore, Style, init


# Activa colores en consola y los reinicia automáticamente.
init(autoreset=True)


###### CLASES ######


# Representa un proceso del sistema.
class Proceso:

    def __init__(self, id, tam, ta, ti):
        self.id = id
        self.tam = tam
        self.ta = ta
        self.ti = ti
        self.ti_restante = ti
        self.estado = "NUEVO"

        # Métricas
        self.tiempo_fin = None
        self.tiempo_retorno = None
        self.tiempo_espera = None


# Representa una partición de memoria.
class Particion:

    def __init__(
        self,
        id,
        base,
        tam,
        estado="LIBRE",
        id_proceso=None
    ):
        self.id = id
        self.base = base
        self.tam = tam
        self.limite = base + tam - 1
        self.estado = estado
        self.id_proceso = id_proceso

    def actualizar_limite(self):
        self.limite = self.base + self.tam - 1


###### FUNCIONES AUXILIARES DEL CSV ######


# Normaliza nombres de columnas.
def normalizar_nombre_columna(nombre):

    nombre = nombre.strip().lower()

    nombre = unicodedata.normalize(
        "NFKD",
        nombre
    )

    nombre = "".join(
        caracter
        for caracter in nombre
        if not unicodedata.combining(caracter)
    )

    nombre = nombre.replace("_", " ")

    return " ".join(
        nombre.split()
    )


# Permite IDs como:
# 1
# P1
# p1
def normalizar_id(valor):

    valor = valor.strip()

    if valor.lower().startswith("p"):
        valor = valor[1:]

    return int(valor)


###### LECTURA DEL CSV ######


def cargar_procesos_csv(ruta_archivo):

    procesos = []

    try:

        with open(
            ruta_archivo,
            mode="r",
            encoding="utf-8-sig"
        ) as archivo:

            lector = csv.DictReader(
                archivo
            )

            if lector.fieldnames is None:

                print(
                    "\nERROR: El archivo CSV está vacío."
                )

                raise SystemExit


            alias_columnas = {

                "id": {
                    "id",
                    "proceso",
                    "id proceso",
                    "id de proceso"
                },

                "tam": {
                    "tam",
                    "tamano",
                    "tamano k",
                    "tamano kb",
                    "tamano (k)",
                    "tamano (kb)",
                    "tamano del proceso"
                },

                "ta": {
                    "ta",
                    "tiempo de arribo",
                    "tiempo arribo"
                },

                "ti": {
                    "ti",
                    "tiempo de irrupcion",
                    "tiempo irrupcion"
                }
            }


            columnas_mapeadas = {}

            for columna_original in lector.fieldnames:

                columna_normalizada = (
                    normalizar_nombre_columna(
                        columna_original
                    )
                )

                for (
                    columna_interna,
                    nombres_permitidos
                ) in alias_columnas.items():

                    if (
                        columna_normalizada
                        in nombres_permitidos
                    ):

                        columnas_mapeadas[
                            columna_interna
                        ] = columna_original


            columnas_esperadas = {
                "id",
                "tam",
                "ta",
                "ti"
            }


            if (
                set(columnas_mapeadas.keys())
                != columnas_esperadas
            ):

                print(
                    "\nERROR: Las columnas del CSV "
                    "no son reconocidas."
                )

                print(
                    "El archivo debe contener las "
                    "columnas correspondientes a:"
                )

                print(
                    "Proceso/ID, Tamaño, TA y TI."
                )

                raise SystemExit


            for numero_fila, fila in enumerate(
                lector,
                start=2
            ):

                for columna_original in (
                    columnas_mapeadas.values()
                ):

                    valor = fila.get(
                        columna_original
                    )

                    if (
                        valor is None
                        or valor.strip() == ""
                    ):

                        print(
                            f"\nERROR: Campo vacío "
                            f"en la fila {numero_fila}, "
                            f"columna "
                            f"'{columna_original}'."
                        )

                        raise SystemExit


                try:

                    proceso = Proceso(

                        id=normalizar_id(
                            fila[
                                columnas_mapeadas[
                                    "id"
                                ]
                            ]
                        ),

                        tam=int(
                            fila[
                                columnas_mapeadas[
                                    "tam"
                                ]
                            ]
                        ),

                        ta=int(
                            fila[
                                columnas_mapeadas[
                                    "ta"
                                ]
                            ]
                        ),

                        ti=int(
                            fila[
                                columnas_mapeadas[
                                    "ti"
                                ]
                            ]
                        )
                    )

                    procesos.append(
                        proceso
                    )


                except ValueError:

                    print(
                        f"\nERROR: Datos inválidos "
                        f"en la fila {numero_fila}."
                    )

                    print(
                        "El ID puede escribirse "
                        "como 1 o P1."
                    )

                    print(
                        "Tamaño, TA y TI deben "
                        "ser números enteros."
                    )

                    raise SystemExit


    except FileNotFoundError:

        print(
            "\nERROR: No se encontró el archivo:"
        )

        print(
            ruta_archivo
        )

        raise SystemExit


    except PermissionError:

        print(
            "\nERROR: No se puede acceder "
            "al archivo:"
        )

        print(
            ruta_archivo
        )

        raise SystemExit


    if not procesos:

        print(
            "\nERROR: El archivo no contiene procesos."
        )

        raise SystemExit


    procesos.sort(
        key=lambda p: (
            p.ta,
            p.id
        )
    )

    return procesos


###### VALIDACIONES ######


def validar_procesos(procesos):

    errores = []

    if len(procesos) > 10:

        errores.append(
            "La cantidad de procesos supera "
            "el máximo permitido de 10."
        )


    ids = set()


    for proceso in procesos:

        if proceso.id in ids:

            errores.append(
                f"El ID P{proceso.id} está repetido."
            )

        else:

            ids.add(
                proceso.id
            )


        if proceso.id <= 0:

            errores.append(
                f"El ID P{proceso.id} "
                f"debe ser mayor a 0."
            )


        if proceso.tam <= 0:

            errores.append(
                f"P{proceso.id}: "
                f"el tamaño debe ser "
                f"mayor a 0 KB."
            )


        if proceso.tam > 450:

            errores.append(
                f"P{proceso.id}: tamaño de "
                f"{proceso.tam} KB. "
                f"Supera los 450 KB disponibles "
                f"para procesos."
            )


        if proceso.ta < 0:

            errores.append(
                f"P{proceso.id}: "
                f"el tiempo de arribo "
                f"no puede ser negativo."
            )


        if proceso.ti <= 0:

            errores.append(
                f"P{proceso.id}: "
                f"el tiempo de irrupción "
                f"debe ser mayor a 0."
            )


    return errores


###### FUNCIONES DE MEMORIA ######


def obtener_estado_memoria_libre():

    huecos = [
        particion.tam
        for particion in memoria
        if particion.estado == "LIBRE"
    ]


    memoria_libre = sum(
        huecos
    )


    cantidad_huecos = len(
        huecos
    )


    mayor_hueco = (
        max(huecos)
        if huecos
        else 0
    )


    fragmentacion_externa = (
        memoria_libre
        - mayor_hueco
    )


    return (
        memoria_libre,
        cantidad_huecos,
        mayor_hueco,
        fragmentacion_externa
    )


def liberar_memoria(id_proceso):

    for particion in memoria:

        if (
            particion.estado == "OCUPADA"
            and particion.id_proceso
            == id_proceso
        ):

            particion.estado = "LIBRE"
            particion.id_proceso = None

            return True

    return False


def fusionar_huecos():

    memoria.sort(
        key=lambda p: p.base
    )

    i = 0

    while i < len(memoria) - 1:

        actual = memoria[i]

        siguiente = memoria[
            i + 1
        ]


        if (
            actual.estado == "LIBRE"
            and siguiente.estado == "LIBRE"
            and actual.limite + 1
            == siguiente.base
        ):

            actual.tam += (
                siguiente.tam
            )

            actual.actualizar_limite()

            memoria.pop(
                i + 1
            )

        else:

            i += 1


    renumerar_particiones()


def buscar_best_fit(tam):

    candidatos = []

    for particion in memoria:

        if (
            particion.estado == "LIBRE"
            and particion.tam >= tam
        ):

            candidatos.append(
                particion
            )


    if not candidatos:

        return None


    return min(
        candidatos,
        key=lambda p: p.tam
    )


def entra_best_fit(tam):

    return (
        buscar_best_fit(tam)
        is not None
    )


def asignar_memoria(
    id_proceso,
    tam
):

    particion = buscar_best_fit(
        tam
    )


    if particion is None:

        return False


    sobrante = (
        particion.tam
        - tam
    )


    base_original = (
        particion.base
    )


    particion.tam = tam
    particion.estado = "OCUPADA"
    particion.id_proceso = (
        id_proceso
    )

    particion.actualizar_limite()


    if sobrante > 0:

        nueva_particion = Particion(
            id=0,
            base=base_original + tam,
            tam=sobrante,
            estado="LIBRE"
        )

        memoria.append(
            nueva_particion
        )


    memoria.sort(
        key=lambda p: p.base
    )


    renumerar_particiones()


    return True


def renumerar_particiones():

    for i, particion in enumerate(
        memoria,
        start=1
    ):

        particion.id = i


def recuperar_suspendidos():

    i = 0

    while i < len(
        listos_suspendidos
    ):

        proceso = (
            listos_suspendidos[i]
        )


        if entra_best_fit(
            proceso.tam
        ):

            listos_suspendidos.pop(
                i
            )

            proceso.estado = "LISTO"

            asignar_memoria(
                proceso.id,
                proceso.tam
            )

            listos.append(
                proceso
            )

        else:

            i += 1


###### REPORTES ######


def imprimir_memoria():

    print(
        "\nMEMORIA"
    )

    print(
        "-" * 72
    )

    print(
        f"{'ID':<5}"
        f"{'Inicio':<10}"
        f"{'Fin':<10}"
        f"{'Tamaño':<12}"
        f"{'Estado':<12}"
        f"{'Proceso':<10}"
    )

    print(
        "-" * 72
    )


    for particion in memoria:

        proceso = (
            f"P{particion.id_proceso}"
            if particion.id_proceso
            is not None
            else "-"
        )

        print(
            f"{particion.id:<5}"
            f"{particion.base:<10}"
            f"{particion.limite:<10}"
            f"{str(particion.tam) + ' KB':<12}"
            f"{particion.estado:<12}"
            f"{proceso:<10}"
        )


    print(
        "-" * 72
    )


    (
        memoria_libre,
        cantidad_huecos,
        mayor_hueco,
        fragmentacion_externa

    ) = obtener_estado_memoria_libre()


    print(
        f"Libre: {memoria_libre} KB | "
        f"Huecos: {cantidad_huecos} | "
        f"Mayor hueco: "
        f"{mayor_hueco} KB | "
        f"Frag. externa: "
        f"{fragmentacion_externa} KB"
    )


def imprimir_reportes_flags():

    # Encabezado del evento en color cian.
    print(
        "\n"
        + Fore.CYAN
        + Style.BRIGHT
        + "=" * 72
    )

    print(
        Fore.CYAN
        + Style.BRIGHT
        + f" EVENTO DEL SISTEMA | "
        f"Tiempo: {reloj}"
    )

    print(
        Fore.CYAN
        + Style.BRIGHT
        + "=" * 72
    )


    # Arribo en verde.
    if evento_arribo:

        print(
            Fore.GREEN
            + Style.BRIGHT
            + ">> ARRIBO DE PROCESO"
        )


    # Finalización en rojo.
    if evento_fin:

        print(
            Fore.RED
            + Style.BRIGHT
            + ">> FINALIZACIÓN DE PROCESO"
        )


    print(
        "\nCPU"
    )


    if ejecucion is not None:

        print(
            f"P{ejecucion.id} | "
            f"Estado: EJECUCION | "
            f"TI restante: "
            f"{ejecucion.ti_restante}"
        )

    else:

        print(
            "OCIOSA"
        )


    print(
        "\nLISTOS"
    )


    if listos:

        for proceso in listos:

            print(
                f"P{proceso.id} | "
                f"TI restante: "
                f"{proceso.ti_restante}"
            )

    else:

        print(
            "Vacía"
        )


    print(
        "\nLISTOS / SUSPENDIDOS"
    )


    if listos_suspendidos:

        for proceso in (
            listos_suspendidos
        ):

            print(
                f"P{proceso.id} | "
                f"Tamaño: "
                f"{proceso.tam} KB"
            )

    else:

        print(
            "Vacía"
        )


    imprimir_memoria()


    print(
        Fore.CYAN
        + Style.BRIGHT
        + "=" * 72
    )


    input(
        "\nPresione ENTER "
        "para continuar..."
    )


###### MÉTRICAS ######


def calcular_metricas():

    for proceso in terminados:

        proceso.tiempo_retorno = (
            proceso.tiempo_fin
            - proceso.ta
        )

        proceso.tiempo_espera = (
            proceso.tiempo_retorno
            - proceso.ti
        )


def imprimir_reportes_finales():

    if not terminados:

        return


    print(
        "\n" + "=" * 72
    )

    print(
        " MÉTRICAS FINALES"
    )

    print(
        "=" * 72
    )


    print(
        f"{'Proceso':<12}"
        f"{'TA':<8}"
        f"{'TI':<8}"
        f"{'TF':<8}"
        f"{'Retorno':<12}"
        f"{'Espera':<12}"
    )


    print(
        "-" * 72
    )


    procesos_ordenados = sorted(
        terminados,
        key=lambda p: p.id
    )


    for proceso in (
        procesos_ordenados
    ):

        print(
            f"{'P' + str(proceso.id):<12}"
            f"{proceso.ta:<8}"
            f"{proceso.ti:<8}"
            f"{proceso.tiempo_fin:<8}"
            f"{proceso.tiempo_retorno:<12}"
            f"{proceso.tiempo_espera:<12}"
        )


    print(
        "-" * 72
    )


    promedio_retorno = sum(
        p.tiempo_retorno
        for p in terminados
    ) / len(terminados)


    promedio_espera = sum(
        p.tiempo_espera
        for p in terminados
    ) / len(terminados)


    tiempo_total = max(
        p.tiempo_fin
        for p in terminados
    )


    throughput = (
        len(terminados)
        / tiempo_total
        if tiempo_total > 0
        else 0
    )


    print(
        "Promedio tiempo de retorno: "
        f"{promedio_retorno:.2f}"
    )


    print(
        "Promedio tiempo de espera: "
        f"{promedio_espera:.2f}"
    )


    print(
        "Throughput: "
        f"{throughput:.2f} "
        "procesos/unidad de tiempo"
    )


    print(
        "=" * 72
    )


###### INTERFAZ DE CONSOLA ######


def mostrar_inicio():

    print(r"""
========================================================================

   _____ _                 _           _
  / ____(_)               | |         | |
 | (___  _ _ __ ___  _   _| | __ _  __| | ___  _ __
  \___ \| | '_ ` _ \| | | | |/ _` |/ _` |/ _ \| '__|
  ____) | | | | | | | |_| | | (_| | (_| | (_) | |
 |_____/|_|_| |_| |_|\__,_|_|\__,_|\__,_|\___/|_|

               PLANIFICACIÓN Y MEMORIA 2026

========================================================================

                         GRUPO N° 4

Integrantes:

  - Elías, Máximo Rafael
  - Estigarribia, Julián Gines
  - Gonzalez, Valentina
  - Inglant, Facundo Agustín
  - Monzón, Lourdes Antonella
  - Nuñez, Lutaro José
  - Quiróz, Ariel Luis

========================================================================
""")


    input(
        "        Presione ENTER "
        "para cargar el archivo CSV..."
    )


    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


def seleccionar_archivo_csv():

    print(
        "\n" + "=" * 72
    )

    print(
        " CARGA DE ARCHIVO CSV"
    )

    print(
        "=" * 72
    )


    print(
        "\nIngrese la ruta del "
        "archivo CSV a utilizar."
    )


    archivo = input(
        "\nRuta del archivo CSV: "
    ).strip()


    while archivo == "":

        print(
            "\nERROR: Debe ingresar "
            "una ruta o nombre de archivo."
        )

        archivo = input(
            "Ruta del archivo CSV: "
        ).strip()


    # Elimina comillas si la ruta
    # fue copiada desde Windows.
    archivo = archivo.strip('"')
    archivo = archivo.strip("'")


    return archivo


###### VARIABLES GLOBALES ######


reloj = 0

activos = 0


evento_arribo = False

evento_fin = False


###### MEMORIA ######


# 0 - 99 KB:
# Sistema Operativo.
#
# 100 - 549 KB:
# 450 KB para procesos de usuario.

memoria = [

    Particion(
        id=1,
        base=100,
        tam=450,
        estado="LIBRE"
    )

]


###### PANTALLA DE INICIO ######


mostrar_inicio()


###### CARGA Y VALIDACIÓN DE PROCESOS ######


ARCHIVO_PROCESOS = (
    seleccionar_archivo_csv()
)


nuevos = cargar_procesos_csv(
    ARCHIVO_PROCESOS
)


errores = validar_procesos(
    nuevos
)


if errores:

    print(
        "\n" + "=" * 72
    )

    print(
        " ERROR EN LOS DATOS DE ENTRADA"
    )

    print(
        "=" * 72
    )


    for error in errores:

        print(
            f"- {error}"
        )


    print(
        "=" * 72
    )


    raise SystemExit


###### COLAS DEL SISTEMA ######


n_total = len(
    nuevos
)


listos = []

listos_suspendidos = []

terminados = []


ejecucion = None


###### PROCESOS CARGADOS ######


print(
    "\n" + "=" * 72
)

print(
    " PROCESOS CARGADOS DESDE CSV"
)

print(
    "=" * 72
)


print(
    f"{'ID':<8}"
    f"{'Tamaño':<12}"
    f"{'TA':<8}"
    f"{'TI':<8}"
    f"{'Estado':<15}"
)


print(
    "-" * 72
)


for proceso in nuevos:

    print(
        f"{'P' + str(proceso.id):<8}"
        f"{str(proceso.tam) + ' KB':<12}"
        f"{proceso.ta:<8}"
        f"{proceso.ti:<8}"
        f"{proceso.estado:<15}"
    )


print(
    "=" * 72
)


print(
    "\nArchivo cargado correctamente:"
)

print(
    ARCHIVO_PROCESOS
)


input(
    "\nPresione ENTER "
    "para iniciar la simulación..."
)


###### BUCLE PRINCIPAL ######


while len(terminados) < n_total:


    # ==========================================================
    # 1. VERIFICAR SI EL PROCESO EN EJECUCIÓN TERMINÓ
    # ==========================================================

    if (
        ejecucion is not None
        and ejecucion.ti_restante == 0
    ):

        ejecucion.tiempo_fin = (
            reloj
        )

        ejecucion.estado = (
            "TERMINADO"
        )

        terminados.append(
            ejecucion
        )

        activos -= 1


        liberar_memoria(
            ejecucion.id
        )

        fusionar_huecos()


        evento_fin = True

        ejecucion = None


        # ======================================================
        # 2. RECUPERAR LISTOS / SUSPENDIDOS
        # ======================================================

        recuperar_suspendidos()


    # ==========================================================
    # 3. DETECTAR ARRIBOS
    # ==========================================================

    for proceso in nuevos:

        if proceso.ta == reloj:

            evento_arribo = True


    # ==========================================================
    # 4. ADMITIR PROCESOS NUEVOS
    # ==========================================================

    while (
        activos < 5
        and nuevos
        and nuevos[0].ta <= reloj
    ):

        proc_admitido = (
            nuevos.pop(0)
        )


        if entra_best_fit(
            proc_admitido.tam
        ):

            proc_admitido.estado = (
                "LISTO"
            )

            asignar_memoria(
                proc_admitido.id,
                proc_admitido.tam
            )

            listos.append(
                proc_admitido
            )


        else:

            proc_admitido.estado = (
                "LISTO_SUSPENDIDO"
            )

            listos_suspendidos.append(
                proc_admitido
            )


        activos += 1


    # ==========================================================
    # 5. PLANIFICACIÓN SRTF
    # ==========================================================

    proc_menor_ti = (

        min(
            listos,
            key=lambda p: (
                p.ti_restante,
                p.ta,
                p.id
            )
        )

        if listos

        else None
    )


    # ==========================================================
    # CPU LIBRE
    # ==========================================================

    if ejecucion is None:


        if (
            proc_menor_ti
            is not None
        ):

            listos.remove(
                proc_menor_ti
            )

            proc_menor_ti.estado = (
                "EJECUCION"
            )

            ejecucion = (
                proc_menor_ti
            )


    # ==========================================================
    # CPU OCUPADA
    # ==========================================================

    else:


        if (
            proc_menor_ti
            is not None
            and (
                proc_menor_ti.ti_restante,
                proc_menor_ti.ta,
                proc_menor_ti.id
            )
            <
            (
                ejecucion.ti_restante,
                ejecucion.ta,
                ejecucion.id
            )
        ):


            ejecucion.estado = (
                "LISTO"
            )

            listos.append(
                ejecucion
            )


            listos.remove(
                proc_menor_ti
            )


            proc_menor_ti.estado = (
                "EJECUCION"
            )


            ejecucion = (
                proc_menor_ti
            )


    # ==========================================================
    # 6. EJECUTAR UNA UNIDAD DE CPU
    # ==========================================================

    if ejecucion is not None:

        ejecucion.ti_restante -= 1


    # ==========================================================
    # 7. MOSTRAR REPORTE SI HUBO EVENTO
    # ==========================================================

    if (
        evento_arribo
        or evento_fin
    ):

        imprimir_reportes_flags()


        evento_arribo = False

        evento_fin = False


    # ==========================================================
    # 8. AVANZAR RELOJ
    # ==========================================================

    reloj += 1


###### FIN DE LA SIMULACIÓN ######


calcular_metricas()


imprimir_reportes_finales()


print(
    "\n" + Fore.GREEN
    + Style.BRIGHT
    + "=" * 72
)

print(
    Fore.GREEN
    + Style.BRIGHT
    + " SIMULACIÓN FINALIZADA"
)

print(
    Fore.GREEN
    + Style.BRIGHT
    + "=" * 72
)


input(
    "\nPresione ENTER para finalizar "
    "y cerrar el programa..."
)