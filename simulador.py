import csv


###### CLASES ######

class Proceso:
    def __init__(self, id, tam, ta, ti):
        self.id = id
        self.tam = tam
        self.ta = ta
        self.ti = ti
        self.ti_restante = ti
        self.estado = "NUEVO"


class Particion:
    def __init__(self, id, base, tam, estado="LIBRE", id_proceso=None):
        self.id = id
        self.base = base
        self.tam = tam
        self.limite = base + tam - 1
        self.estado = estado
        self.id_proceso = id_proceso

    def actualizar_limite(self):
        self.limite = self.base + self.tam - 1


###### LECTURA DEL CSV ######

def cargar_procesos_csv(ruta_archivo):
    procesos = []

    try:
        with open(ruta_archivo, mode="r", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)

            columnas_esperadas = {"id", "tam", "ta", "ti"}

            if lector.fieldnames is None:
                print("\nERROR: El archivo CSV está vacío.")
                raise SystemExit

            columnas_archivo = set(lector.fieldnames)

            if columnas_archivo != columnas_esperadas:
                print("\nERROR: Las columnas del CSV no son correctas.")
                print("Se esperan las columnas: id,tam,ta,ti")
                raise SystemExit

            for numero_fila, fila in enumerate(lector, start=2):

                try:
                    proceso = Proceso(
                        id=int(fila["id"]),
                        tam=int(fila["tam"]),
                        ta=int(fila["ta"]),
                        ti=int(fila["ti"])
                    )

                    procesos.append(proceso)

                except (ValueError, TypeError):
                    print(
                        f"\nERROR: Datos inválidos en la fila {numero_fila}."
                    )
                    print(
                        "Todos los valores deben ser números enteros."
                    )
                    raise SystemExit

    except FileNotFoundError:
        print(
            f"\nERROR: No se encontró el archivo '{ruta_archivo}'."
        )
        raise SystemExit

    except PermissionError:
        print(
            f"\nERROR: No se puede acceder al archivo '{ruta_archivo}'."
        )
        raise SystemExit

    if not procesos:
        print("\nERROR: El archivo no contiene procesos.")
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
            "La cantidad de procesos supera el máximo permitido de 10."
        )

    ids = set()

    for proceso in procesos:

        if proceso.id in ids:
            errores.append(
                f"El ID {proceso.id} está repetido."
            )
        else:
            ids.add(proceso.id)

        if proceso.id <= 0:
            errores.append(
                f"El ID {proceso.id} debe ser mayor a 0."
            )

        if proceso.tam <= 0:
            errores.append(
                f"P{proceso.id}: el tamaño debe ser mayor a 0 KB."
            )

        if proceso.tam > 450:
            errores.append(
                f"P{proceso.id}: tamaño de {proceso.tam} KB. "
                f"Supera los 450 KB disponibles para procesos."
            )

        if proceso.ta < 0:
            errores.append(
                f"P{proceso.id}: el tiempo de arribo no puede ser negativo."
            )

        if proceso.ti <= 0:
            errores.append(
                f"P{proceso.id}: el tiempo de irrupción debe ser mayor a 0."
            )

    return errores


###### FUNCIONES DE MEMORIA ######

def obtener_estado_memoria_libre():
    huecos = [
        particion.tam
        for particion in memoria
        if particion.estado == "LIBRE"
    ]

    memoria_libre = sum(huecos)
    cantidad_huecos = len(huecos)
    mayor_hueco = max(huecos) if huecos else 0

    fragmentacion_externa = memoria_libre - mayor_hueco

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
            and particion.id_proceso == id_proceso
        ):
            particion.estado = "LIBRE"
            particion.id_proceso = None

            return True

    return False


def fusionar_huecos():
    memoria.sort(key=lambda p: p.base)

    i = 0

    while i < len(memoria) - 1:

        actual = memoria[i]
        siguiente = memoria[i + 1]

        if (
            actual.estado == "LIBRE"
            and siguiente.estado == "LIBRE"
            and actual.limite + 1 == siguiente.base
        ):

            actual.tam += siguiente.tam
            actual.actualizar_limite()

            memoria.pop(i + 1)

        else:
            i += 1

    renumerar_particiones()


def imprimir_memoria():
    print("\nMEMORIA")
    print("-" * 72)

    print(
        f"{'ID':<5}"
        f"{'Inicio':<10}"
        f"{'Fin':<10}"
        f"{'Tamaño':<12}"
        f"{'Estado':<12}"
        f"{'Proceso':<10}"
    )

    print("-" * 72)

    for particion in memoria:

        proceso = (
            f"P{particion.id_proceso}"
            if particion.id_proceso is not None
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

    print("-" * 72)

    (
        memoria_libre,
        cantidad_huecos,
        mayor_hueco,
        fragmentacion_externa
    ) = obtener_estado_memoria_libre()

    print(
        f"Libre: {memoria_libre} KB | "
        f"Huecos: {cantidad_huecos} | "
        f"Mayor hueco: {mayor_hueco} KB | "
        f"Frag. externa: {fragmentacion_externa} KB"
    )


def buscar_best_fit(tam):
    candidatos = []

    for particion in memoria:

        if (
            particion.estado == "LIBRE"
            and particion.tam >= tam
        ):
            candidatos.append(particion)

    if not candidatos:
        return None

    return min(
        candidatos,
        key=lambda p: p.tam
    )


def entra_best_fit(tam):
    return buscar_best_fit(tam) is not None


def asignar_memoria(id_proceso, tam):
    particion = buscar_best_fit(tam)

    if particion is None:
        return False

    sobrante = particion.tam - tam
    base_original = particion.base

    particion.tam = tam
    particion.estado = "OCUPADA"
    particion.id_proceso = id_proceso
    particion.actualizar_limite()

    if sobrante > 0:

        nueva_base = base_original + tam

        nueva_particion = Particion(
            id=0,
            base=nueva_base,
            tam=sobrante,
            estado="LIBRE"
        )

        memoria.append(nueva_particion)

    memoria.sort(key=lambda p: p.base)

    renumerar_particiones()

    return True


def renumerar_particiones():
    for i, particion in enumerate(memoria, start=1):
        particion.id = i


###### REPORTES ######

def imprimir_reportes_flags():
    print("\n" + "=" * 72)
    print(f" EVENTO DEL SISTEMA | Tiempo: {reloj}")
    print("=" * 72)

    if evento_arribo:
        print(">> ARRIBO DE PROCESO")

    if evento_fin:
        print(">> FINALIZACIÓN DE PROCESO")

    print("\nCPU")

    if ejecucion is not None:
        print(
            f"P{ejecucion.id} | "
            f"Estado: EJECUCION | "
            f"TI restante: {ejecucion.ti_restante}"
        )
    else:
        print("OCIOSA")

    print("\nLISTOS")

    if listos:
        for proceso in listos:
            print(
                f"P{proceso.id} | "
                f"TI restante: {proceso.ti_restante}"
            )
    else:
        print("Vacía")

    print("\nLISTOS / SUSPENDIDOS")

    if listos_suspendidos:
        for proceso in listos_suspendidos:
            print(
                f"P{proceso.id} | "
                f"Tamaño: {proceso.tam} KB"
            )
    else:
        print("Vacía")

    imprimir_memoria()

    print("=" * 72)

    input("\nPresione ENTER para continuar...")


def calcular_metricas():
    pass


def imprimir_reportes_finales():
    pass


###### VARIABLES GLOBALES ######

reloj = 0
activos = 0

evento_arribo = False
evento_fin = False


###### MEMORIA ######

memoria = [
    Particion(
        id=1,
        base=100,
        tam=450,
        estado="LIBRE"
    )
]


###### CARGAR PROCESOS DESDE CSV ######

ARCHIVO_PROCESOS = "procesos.csv"

nuevos = cargar_procesos_csv(
    ARCHIVO_PROCESOS
)


###### VALIDAR DATOS ######

errores = validar_procesos(nuevos)

if errores:

    print("\n" + "=" * 72)
    print(" ERROR EN LOS DATOS DE ENTRADA")
    print("=" * 72)

    for error in errores:
        print(f"- {error}")

    print("=" * 72)

    raise SystemExit


###### COLAS DEL SISTEMA ######

n_total = len(nuevos)

listos = []
listos_suspendidos = []
terminados = []

ejecucion = None


###### PROCESOS CARGADOS ######

print("\n" + "=" * 72)
print(" PROCESOS CARGADOS DESDE CSV")
print("=" * 72)

print(
    f"{'ID':<8}"
    f"{'Tamaño':<12}"
    f"{'TA':<8}"
    f"{'TI':<8}"
    f"{'Estado':<15}"
)

print("-" * 72)

for proceso in nuevos:

    print(
        f"{proceso.id:<8}"
        f"{str(proceso.tam) + ' KB':<12}"
        f"{proceso.ta:<8}"
        f"{proceso.ti:<8}"
        f"{proceso.estado:<15}"
    )

print("=" * 72)


###### BUCLE PRINCIPAL ######

while len(terminados) < n_total:


    # ==========================================================
    # 1. VERIFICAR SI EL PROCESO EN EJECUCIÓN TERMINÓ
    # ==========================================================

    if (
        ejecucion is not None
        and ejecucion.ti_restante == 0
    ):

        ejecucion.estado = "TERMINADO"

        terminados.append(ejecucion)

        activos -= 1

        liberar_memoria(ejecucion.id)
        fusionar_huecos()

        evento_fin = True
        ejecucion = None


        # ======================================================
        # 2. REVISAR LISTOS / SUSPENDIDOS
        # ======================================================

        if listos_suspendidos:

            if entra_best_fit(
                listos_suspendidos[0].tam
            ):

                proc_recuperado = (
                    listos_suspendidos.pop(0)
                )

                proc_recuperado.estado = "LISTO"

                asignar_memoria(
                    proc_recuperado.id,
                    proc_recuperado.tam
                )

                listos.append(proc_recuperado)


    # ==========================================================
    # 3. DETECTAR EVENTOS DE ARRIBO
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

        proc_admitido = nuevos.pop(0)


        if entra_best_fit(proc_admitido.tam):

            proc_admitido.estado = "LISTO"

            asignar_memoria(
                proc_admitido.id,
                proc_admitido.tam
            )

            listos.append(proc_admitido)


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

        if proc_menor_ti is not None:

            listos.remove(proc_menor_ti)

            proc_menor_ti.estado = "EJECUCION"

            ejecucion = proc_menor_ti


    # ==========================================================
    # CPU OCUPADA
    # ==========================================================

    else:

        if (
            proc_menor_ti is not None
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

            ejecucion.estado = "LISTO"

            listos.append(ejecucion)

            listos.remove(proc_menor_ti)

            proc_menor_ti.estado = "EJECUCION"

            ejecucion = proc_menor_ti


    # ==========================================================
    # 6. EJECUTAR UNA UNIDAD DE CPU
    # ==========================================================

    if ejecucion is not None:
        ejecucion.ti_restante -= 1


    # ==========================================================
    # 7. REPORTES POR EVENTO
    # ==========================================================

    if evento_arribo or evento_fin:

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


print("\n" + "=" * 72)
print(" SIMULACIÓN FINALIZADA")
print("=" * 72)