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


###### FUNCIÓN TEMPORAL PARA SIMULAR LECTURA DEL CSV ######

def cargar_nuevos_prueba():
    # Proceso(id, tamaño, tiempo_arribo, tiempo_irrupcion)

    p1 = Proceso(1, 100, 0, 5)
    p2 = Proceso(2, 250, 2, 3)
    p3 = Proceso(3, 50, 4, 2)

    lista_procesos = [p1, p2, p3]

    # NUEVOS ordenado por Tiempo de Arribo
    lista_procesos.sort(key=lambda p: p.ta)

    return lista_procesos


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

    # Indica cuánta memoria libre está dispersa
    # fuera del mayor bloque contiguo.
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

    # La partición encontrada pasa a estar ocupada
    particion.tam = tam
    particion.estado = "OCUPADA"
    particion.id_proceso = id_proceso
    particion.actualizar_limite()

    # Si sobra memoria, se crea un nuevo hueco libre
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


###### FUNCIONES TODAVÍA PENDIENTES ######

def calcular_metricas():
    pass


def imprimir_reportes_flags():
    print("\n" + "=" * 72)
    print(f" EVENTO DEL SISTEMA | Tiempo: {reloj}")
    print("=" * 72)

    if evento_arribo:
        print(">> ARRIBO DE PROCESO")

    if evento_fin:
        print(">> FINALIZACIÓN DE PROCESO")

    # CPU
    print("\nCPU")

    if ejecucion is not None:
        print(
            f"P{ejecucion.id} | "
            f"Estado: EJECUCION | "
            f"TI restante: {ejecucion.ti_restante}"
        )
    else:
        print("OCIOSA")

    # Cola de listos
    print("\nLISTOS")

    if listos:
        for proceso in listos:
            print(
                f"P{proceso.id} | "
                f"TI restante: {proceso.ti_restante}"
            )
    else:
        print("Vacía")

    # Cola de listos suspendidos
    print("\nLISTOS / SUSPENDIDOS")

    if listos_suspendidos:
        for proceso in listos_suspendidos:
            print(
                f"P{proceso.id} | "
                f"Tamaño: {proceso.tam} KB"
            )
    else:
        print("Vacía")

    # Memoria
    imprimir_memoria()

    print("=" * 72)

    input("\nPresione ENTER para continuar...")


def imprimir_reportes_finales():
    pass


###### VARIABLES GLOBALES ######

reloj = 0
activos = 0

evento_arribo = False
evento_fin = False


###### MEMORIA ######

# 0 - 99 KB -> Sistema Operativo
# 100 - 549 KB -> Procesos de usuario

memoria = [
    Particion(
        id=1,
        base=100,
        tam=450,
        estado="LIBRE"
    )
]


###### COLAS / ESTADOS DEL SISTEMA ######

nuevos = cargar_nuevos_prueba()

n_total = len(nuevos)

listos = []
listos_suspendidos = []
terminados = []

# Una sola CPU
ejecucion = None


###### MOSTRAR PROCESOS CARGADOS ######

print("====================================")
print("PROCESOS CARGADOS EN NUEVOS")
print("====================================")

print(f"Cantidad de procesos: {n_total}")

for p in nuevos:

    print(
        f"ID: {p.id} | "
        f"Tamaño: {p.tam} KB | "
        f"TA: {p.ta} | "
        f"TI: {p.ti} | "
        f"Estado: {p.estado}"
    )

print("====================================")


###### BUCLE PRINCIPAL ######

while len(terminados) < n_total:

    print(f"\n----- RELOJ: {reloj} -----")


    # ==========================================================
    # 1. VERIFICAR SI EL PROCESO EN EJECUCIÓN TERMINÓ
    # ==========================================================

    if (
        ejecucion is not None
        and ejecucion.ti_restante == 0
    ):

        print(f"P{ejecucion.id} terminó.")

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

                print(
                    f"P{proc_recuperado.id} pasa de "
                    f"LISTO_SUSPENDIDO a LISTO."
                )


    # ==========================================================
    # 3. DETECTAR EVENTOS DE ARRIBO
    # ==========================================================

    for proceso in nuevos:

        if proceso.ta == reloj:

            evento_arribo = True

            print(
                f"Arribó P{proceso.id} "
                f"(TA={proceso.ta}, "
                f"TI={proceso.ti}, "
                f"Tamaño={proceso.tam} KB)"
            )


    # ==========================================================
    # 4. ADMITIR PROCESOS NUEVOS
    # ==========================================================

    while (
        activos < 5
        and nuevos
        and nuevos[0].ta <= reloj
    ):

        proc_admitido = nuevos.pop(0)

        # ------------------------------------------------------
        # ENTRA EN MEMORIA
        # ------------------------------------------------------

        if entra_best_fit(proc_admitido.tam):

            proc_admitido.estado = "LISTO"

            asignar_memoria(
                proc_admitido.id,
                proc_admitido.tam
            )

            listos.append(proc_admitido)

            print(
                f"P{proc_admitido.id} fue admitido "
                f"y pasa a LISTO."
            )

        # ------------------------------------------------------
        # NO ENTRA EN MEMORIA
        # ------------------------------------------------------

        else:

            proc_admitido.estado = (
                "LISTO_SUSPENDIDO"
            )

            listos_suspendidos.append(
                proc_admitido
            )

            print(
                f"P{proc_admitido.id} fue admitido "
                f"pero pasa a LISTO_SUSPENDIDO."
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


    # ----------------------------------------------------------
    # CPU LIBRE
    # ----------------------------------------------------------

    if ejecucion is None:

        if proc_menor_ti is not None:

            listos.remove(proc_menor_ti)

            proc_menor_ti.estado = "EJECUCION"

            ejecucion = proc_menor_ti

            print(
                f"CPU asignada a P{ejecucion.id} "
                f"(TI restante: "
                f"{ejecucion.ti_restante})"
            )

        else:

            print("CPU OCIOSA")


    # ----------------------------------------------------------
    # CPU OCUPADA
    # ----------------------------------------------------------

    else:

        # SRTF:
        # menor TI restante
        # desempate: menor TA
        # segundo desempate: menor ID

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

            print(
                f"EXPROPIACIÓN: "
                f"P{proc_menor_ti.id} reemplaza a "
                f"P{ejecucion.id}"
            )

            # El proceso expropiado vuelve a LISTO
            ejecucion.estado = "LISTO"
            listos.append(ejecucion)

            # El proceso seleccionado toma la CPU
            listos.remove(proc_menor_ti)

            proc_menor_ti.estado = "EJECUCION"

            ejecucion = proc_menor_ti


    # ==========================================================
    # 6. EJECUTAR UNA UNIDAD DE CPU
    # ==========================================================

    if ejecucion is not None:

        print(
            f"Ejecutando P{ejecucion.id} | "
            f"TI restante antes: "
            f"{ejecucion.ti_restante}"
        )

        ejecucion.ti_restante -= 1

        print(
            f"TI restante después: "
            f"{ejecucion.ti_restante}"
        )


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

print("\n====================================")
print("SIMULACIÓN FINALIZADA")
print("====================================")