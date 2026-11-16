import csv  # Importa el módulo estándar para leer y procesar archivos en formato CSV.
import os  # Importa el módulo para interactuar con el sistema operativo (ej. limpiar la pantalla).
import unicodedata  # Importa utilidades Unicode para normalizar texto y eliminar acentos/tildes.

from colorama import Fore, Style, init  # Importa herramientas para dar color y estilo al texto en la consola.


# Activa colores en consola y los reinicia automáticamente.
init(autoreset=True)  # Inicializa colorama haciendo que el color vuelva al valor por defecto tras cada print.


import sys  # Importa el módulo del sistema para gestionar la salida y terminación del programa.


def salir():  # Define una función auxiliar para pausar la ejecución y cerrar el programa ante un error.
    input("\nPresione ENTER para cerrar el programa...")  # Detiene el flujo hasta que el usuario presione la tecla ENTER.
    sys.exit(1)  # Finaliza la ejecución del script devolviendo el código de salida 1 (indica error).


###### CLASES ######


# Representa un proceso del sistema.
class Proceso:  # Define la estructura de datos y atributos que tendrá cada proceso simulado.

    def __init__(self, id, tam, ta, ti):  # Método constructor que inicializa un proceso con sus datos básicos.
        self.id = id  # Guarda el identificador numérico único del proceso.
        self.tam = tam  # Guarda el tamaño del proceso en kilobytes (KB).
        self.ta = ta  # Guarda el Tiempo de Arribo (instante en que llega al sistema).
        self.ti = ti  # Guarda el Tiempo de Irrupción total (tiempo de CPU que necesita para terminar).
        self.ti_restante = ti  # Inicializa el tiempo restante de CPU igual al tiempo de irrupción total.
        self.estado = "NUEVO"  # Establece el estado inicial del proceso como "NUEVO".

        # Métricas
        self.t_listo = None  # instante en que entra por 1ra vez a LISTO
        self.tiempo_fin = None  # Almacenará el instante de reloj en que el proceso finaliza su ejecución.
        self.tiempo_retorno = None  # Almacenará el tiempo total transcurrido desde que entra a listo hasta que termina.
        self.tiempo_espera = None  # Almacenará el tiempo que el proceso pasó esperando en cola sin usar CPU.


# Representa una partición de memoria.
class Particion:  # Define un bloque contiguo de memoria principal (libre u ocupado por un proceso).

    def __init__(  # Método constructor para crear una nueva partición de memoria.
        self,
        id,  # Número identificador de la partición.
        base,  # Dirección de memoria inicial donde comienza la partición.
        tam,  # Tamaño de la partición en KB.
        estado="LIBRE",  # Estado inicial de la partición ("LIBRE" por defecto u "OCUPADA").
        id_proceso=None  # ID del proceso que ocupa la partición (None si está libre).
    ):
        self.id = id  # Asigna el identificador a la partición.
        self.base = base  # Asigna la dirección base (inicio) de la partición.
        self.tam = tam  # Asigna el tamaño en KB de la partición.
        self.limite = base + tam - 1  # Calcula la dirección final exacta de la partición.
        self.estado = estado  # Asigna el estado ("LIBRE" u "OCUPADA").
        self.id_proceso = id_proceso  # Asigna el ID del proceso propietario (si corresponde).

    def actualizar_limite(self):  # Método para recalcular la dirección final cuando cambia el tamaño de la partición.
        self.limite = self.base + self.tam - 1  # Actualiza el límite superior sumando base + tamaño - 1.


###### FUNCIONES AUXILIARES DEL CSV ######


# Normaliza nombres de columnas.
def normalizar_nombre_columna(nombre):  # Limpia los encabezados del CSV para evitar errores por mayúsculas o tildes.

    nombre = nombre.strip().lower()  # Elimina espacios en los extremos y convierte todo el texto a minúsculas.

    nombre = unicodedata.normalize(  # Descompone caracteres acentuados en su letra base y su marca de acento.
        "NFKD",
        nombre
    )

    nombre = "".join(  # Reconstruye la cadena filtrando y descartando las marcas de acento (tildes/diéresis).
        caracter
        for caracter in nombre
        if not unicodedata.combining(caracter)
    )

    nombre = nombre.replace("_", " ")  # Reemplaza guiones bajos por espacios en blanco.

    return " ".join(  # Elimina espacios múltiples consecutivos dejando un solo espacio entre palabras.
        nombre.split()
    )


# Permite IDs como:
# 1
# P1
# p1
def normalizar_id(valor):  # Convierte el identificador del proceso leído del CSV en un número entero puro.

    valor = valor.strip()  # Quita espacios en blanco al principio y al final del valor.

    if valor.lower().startswith("p"):  # Verifica si el identificador comienza con la letra 'p' o 'P'.
        valor = valor[1:]  # Recorta el primer carácter ('p') dejando solo la parte numérica.

    return int(valor)  # Convierte la cadena resultante a un tipo de dato entero y lo retorna.


###### LECTURA DEL CSV ######


def cargar_procesos_csv(ruta_archivo):  # Lee el archivo CSV, valida su estructura y crea los objetos Proceso.

    procesos = []  # Crea una lista vacía donde se almacenarán los procesos cargados.

    try:  # Inicia un bloque para capturar errores de lectura de archivos (ej. archivo inexistente).

        with open(  # Abre el archivo CSV en modo lectura con codificación UTF-8 (ignorando BOM si existe).
            ruta_archivo,
            mode="r",
            encoding="utf-8-sig"
        ) as archivo:

            lector = csv.DictReader(  # Crea un lector que interpreta cada fila del CSV como un diccionario.
                archivo
            )

            if lector.fieldnames is None:  # Comprueba si el archivo no tiene encabezados (está completamente vacío).

                print(  # Muestra un mensaje de error en pantalla.
                    "\nERROR: El archivo CSV está vacío."
                )

                salir()  # Llama a la función de salida para detener el programa.


            alias_columnas = {  # Diccionario que define los nombres aceptados para cada columna requerida.

                "id": {  # Variantes válidas para la columna de identificador de proceso.
                    "id",
                    "proceso",
                    "id proceso",
                    "id de proceso"
                },

                "tam": {  # Variantes válidas para la columna de tamaño de memoria.
                    "tam",
                    "tamano",
                    "tamano k",
                    "tamano kb",
                    "tamano (k)",
                    "tamano (kb)",
                    "tamano del proceso"
                },

                "ta": {  # Variantes válidas para la columna de Tiempo de Arribo.
                    "ta",
                    "tiempo de arribo",
                    "tiempo arribo"
                },

                "ti": {  # Variantes válidas para la columna de Tiempo de Irrupción.
                    "ti",
                    "tiempo de irrupcion",
                    "tiempo irrupcion"
                }
            }


            columnas_mapeadas = {}  # Diccionario para relacionar el nombre interno con el encabezado real del CSV.

            for columna_original in lector.fieldnames:  # Recorre cada encabezado presente en el archivo CSV.

                columna_normalizada = (  # Normaliza el encabezado actual (minúsculas, sin tildes ni espacios extra).
                    normalizar_nombre_columna(
                        columna_original
                    )
                )

                for (  # Itera sobre los nombres internos y sus conjuntos de alias permitidos.
                    columna_interna,
                    nombres_permitidos
                ) in alias_columnas.items():

                    if (  # Verifica si el encabezado normalizado coincide con alguno de los alias válidos.
                        columna_normalizada
                        in nombres_permitidos
                    ):

                        columnas_mapeadas[  # Guarda la relación entre el nombre interno y el encabezado original.
                            columna_interna
                        ] = columna_original


            columnas_esperadas = {  # Conjunto con las 4 columnas obligatorias que debe tener el CSV.
                "id",
                "tam",
                "ta",
                "ti"
            }


            if (  # Comprueba si faltó reconocer alguna de las 4 columnas obligatorias.
                set(columnas_mapeadas.keys())
                != columnas_esperadas
            ):

                print(  # Informa que las columnas del archivo no coinciden con las esperadas.
                    "\nERROR: Las columnas del CSV "
                    "no son reconocidas."
                )

                print(  # Indica qué columnas son necesarias.
                    "El archivo debe contener las "
                    "columnas correspondientes a:"
                )

                print(  # Lista los nombres esperados para orientación del usuario.
                    "Proceso/ID, Tamaño, TA y TI."
                )

                salir()  # Detiene el programa por error de formato.


            for numero_fila, fila in enumerate(  # Recorre cada fila de datos del CSV numerándolas desde la fila 2.
                lector,
                start=2
            ):

                for columna_original in (  # Verifica cada una de las 4 columnas mapeadas en la fila actual.
                    columnas_mapeadas.values()
                ):

                    valor = fila.get(  # Obtiene el dato contenido en esa celda.
                        columna_original
                    )

                    if (  # Comprueba si la celda está vacía o contiene solo espacios en blanco.
                        valor is None
                        or valor.strip() == ""
                    ):

                        print(  # Muestra la fila y columna exacta donde falta un dato.
                            f"\nERROR: Campo vacío "
                            f"en la fila {numero_fila}, "
                            f"columna "
                            f"'{columna_original}'."
                        )

                        salir()  # Detiene la ejecución ante datos incompletos.


                try:  # Intenta convertir los valores de texto de la fila a enteros y crear el proceso.

                    proceso = Proceso(  # Instancia un nuevo objeto Proceso con los datos extraídos.

                        id=normalizar_id(  # Normaliza y convierte el ID a entero.
                            fila[
                                columnas_mapeadas[
                                    "id"
                                ]
                            ]
                        ),

                        tam=int(  # Convierte el tamaño a entero.
                            fila[
                                columnas_mapeadas[
                                    "tam"
                                ]
                            ]
                        ),

                        ta=int(  # Convierte el Tiempo de Arribo a entero.
                            fila[
                                columnas_mapeadas[
                                    "ta"
                                ]
                            ]
                        ),

                        ti=int(  # Convierte el Tiempo de Irrupción a entero.
                            fila[
                                columnas_mapeadas[
                                    "ti"
                                ]
                            ]
                        )
                    )

                    procesos.append(  # Agrega el proceso creado a la lista de procesos.
                        proceso
                    )


                except ValueError:  # Captura el error si algún campo numérico contiene letras o decimales inválidos.

                    print(  # Informa en qué fila ocurrió el error de conversión de tipo.
                        f"\nERROR: Datos inválidos "
                        f"en la fila {numero_fila}."
                    )

                    print(  # Aclara el formato permitido para el ID.
                        "El ID puede escribirse "
                        "como 1 o P1."
                    )

                    print(  # Aclara que el resto de los campos deben ser enteros.
                        "Tamaño, TA y TI deben "
                        "ser números enteros."
                    )

                    salir()  # Termina el programa.


    except FileNotFoundError:  # Captura el error si la ruta ingresada no corresponde a ningún archivo existente.

        print(  # Muestra mensaje de archivo no encontrado.
            "\nERROR: No se encontró el archivo:"
        )

        print(  # Imprime la ruta que falló.
            ruta_archivo
        )

        salir()  # Termina el programa.


    except PermissionError:  # Captura el error si el archivo está abierto/bloqueado o sin permisos de lectura.

        print(  # Muestra mensaje de error de permisos.
            "\nERROR: No se puede acceder "
            "al archivo:"
        )

        print(  # Imprime la ruta del archivo inaccesible.
            ruta_archivo
        )

        salir()  # Termina el programa.


    if not procesos:  # Verifica si el archivo tenía encabezados pero ninguna fila de procesos.

        print(  # Informa que no hay procesos para simular.
            "\nERROR: El archivo no contiene procesos."
        )

        salir()  # Termina el programa.


    procesos.sort(  # Ordena la lista de procesos cronológicamente por Tiempo de Arribo (y por ID en caso de empate).
        key=lambda p: (
            p.ta,
            p.id
        )
    )

    return procesos  # Devuelve la lista de procesos cargados y ordenados.


###### VALIDACIONES ######


def validar_procesos(procesos):  # Verifica que los procesos cumplan con las reglas de negocio y límites del simulador.

    errores = []  # Lista que acumulará todos los mensajes de error encontrados.

    if len(procesos) > 10:  # Comprueba que no se supere el límite máximo de 10 procesos.

        errores.append(  # Registra el error de exceso de procesos.
            "La cantidad de procesos supera "
            "el máximo permitido de 10."
        )


    ids = set()  # Conjunto auxiliar para detectar IDs duplicados.


    for proceso in procesos:  # Recorre cada proceso para validar sus atributos individualmente.

        if proceso.id in ids:  # Comprueba si el ID ya fue registrado anteriormente.

            errores.append(  # Registra el error de ID repetido.
                f"El ID P{proceso.id} está repetido."
            )

        else:  # Si el ID es nuevo:

            ids.add(  # Lo agrega al conjunto de IDs vistos.
                proceso.id
            )


        if proceso.id <= 0:  # Valida que el ID sea un número positivo mayor a 0.

            errores.append(  # Registra el error si el ID es 0 o negativo.
                f"El ID P{proceso.id} "
                f"debe ser mayor a 0."
            )


        if proceso.tam <= 0:  # Valida que el tamaño del proceso sea mayor a 0 KB.

            errores.append(  # Registra el error de tamaño nulo o negativo.
                f"P{proceso.id}: "
                f"el tamaño debe ser "
                f"mayor a 0 KB."
            )


        if proceso.tam > 450:  # Valida que el proceso quepa en la memoria de usuario disponible (450 KB).

            errores.append(  # Registra el error si excede los 450 KB.
                f"P{proceso.id}: tamaño de "
                f"{proceso.tam} KB. "
                f"Supera los 450 KB disponibles "
                f"para procesos."
            )


        if proceso.ta < 0:  # Valida que el Tiempo de Arribo no sea un número negativo.

            errores.append(  # Registra el error de tiempo de arribo negativo.
                f"P{proceso.id}: "
                f"el tiempo de arribo "
                f"no puede ser negativo."
            )


        if proceso.ti <= 0:  # Valida que el Tiempo de Irrupción sea mayor a 0.

            errores.append(  # Registra el error si el tiempo de CPU requerido es 0 o negativo.
                f"P{proceso.id}: "
                f"el tiempo de irrupción "
                f"debe ser mayor a 0."
            )


    return errores  # Devuelve la lista de errores (estará vacía si todo es válido).


###### FUNCIONES DE MEMORIA ######


def obtener_estado_memoria_libre():  # Calcula métricas actuales sobre los espacios libres y la fragmentación externa.

    huecos = [  # Crea una lista con los tamaños de todas las particiones que están en estado "LIBRE".
        particion.tam
        for particion in memoria
        if particion.estado == "LIBRE"
    ]


    memoria_libre = sum(  # Suma el tamaño de todos los huecos para obtener la memoria libre total.
        huecos
    )


    cantidad_huecos = len(  # Cuenta cuántas particiones libres separadas existen.
        huecos
    )


    mayor_hueco = (  # Obtiene el tamaño del hueco libre más grande (o 0 si no hay ninguno libre).
        max(huecos)
        if huecos
        else 0
    )


    fragmentacion_externa = (  # Calcula la fragmentación externa: memoria libre total menos el hueco más grande.
        memoria_libre
        - mayor_hueco
    )


    return (  # Retorna los 4 indicadores calculados en una tupla.
        memoria_libre,
        cantidad_huecos,
        mayor_hueco,
        fragmentacion_externa
    )


def liberar_memoria(id_proceso):  # Marca como libre la partición que estaba ocupada por el proceso especificado.

    for particion in memoria:  # Recorre todas las particiones de la memoria.

        if (  # Busca la partición ocupada cuyo ID de proceso coincida con el que terminó.
            particion.estado == "OCUPADA"
            and particion.id_proceso
            == id_proceso
        ):

            particion.estado = "LIBRE"  # Cambia el estado de la partición a "LIBRE".
            particion.id_proceso = None  # Desvincula el ID del proceso de la partición.

            return True  # Indica que la liberación fue exitosa.

    return False  # Indica que no se encontró ningún bloque ocupado por ese proceso.


def fusionar_huecos():  # Compacta particiones libres adyacentes en un único bloque libre más grande (coalescencia).

    memoria.sort(  # Ordena las particiones según su dirección física inicial (base).
        key=lambda p: p.base
    )

    i = 0  # Inicializa el índice para recorrer la lista de particiones.

    while i < len(memoria) - 1:  # Recorre hasta el penúltimo elemento comparando pares consecutivos.

        actual = memoria[i]  # Obtiene la partición en la posición actual.

        siguiente = memoria[  # Obtiene la partición inmediatamente contigua.
            i + 1
        ]


        if (  # Verifica si ambas particiones están libres y son físicamente contiguas en memoria.
            actual.estado == "LIBRE"
            and siguiente.estado == "LIBRE"
            and actual.limite + 1
            == siguiente.base
        ):

            actual.tam += (  # Suma el tamaño de la partición siguiente a la partición actual.
                siguiente.tam
            )

            actual.actualizar_limite()  # Recalcula la dirección límite de la partición ampliada.

            memoria.pop(  # Elimina de la lista la partición siguiente que ya fue absorbida.
                i + 1
            )

        else:  # Si no se pudieron fusionar:

            i += 1  # Avanza al siguiente índice para seguir revisando.


    renumerar_particiones()  # Reasigna los IDs correlativos de las particiones tras las fusiones.


def buscar_best_fit(tam):  # Implementa el algoritmo Best-Fit: busca el hueco libre más pequeño donde quepa el proceso.

    candidatos = []  # Lista para guardar todas las particiones libres con tamaño suficiente.

    for particion in memoria:  # Recorre las particiones existentes en memoria.

        if (  # Comprueba si la partición está libre y su tamaño es mayor o igual al requerido.
            particion.estado == "LIBRE"
            and particion.tam >= tam
        ):

            candidatos.append(  # Añade la partición a la lista de candidatas.
                particion
            )


    if not candidatos:  # Si ninguna partición libre tiene espacio suficiente:

        return None  # Retorna None indicando que no hay lugar disponible.


    return min(  # Selecciona y devuelve la partición candidata con el menor tamaño (mejor ajuste).
        candidatos,
        key=lambda p: p.tam
    )


def entra_best_fit(tam):  # Función booleana rápida para saber si un proceso de cierto tamaño cabe en memoria.

    return (  # Devuelve True si buscar_best_fit encuentra una partición válida, o False en caso contrario.
        buscar_best_fit(tam)
        is not None
    )


def asignar_memoria(  # Asigna un bloque de memoria a un proceso usando Best-Fit y divide la partición si sobra espacio.
    id_proceso,
    tam
):

    particion = buscar_best_fit(  # Busca la mejor partición libre disponible para el tamaño solicitado.
        tam
    )


    if particion is None:  # Si no se encontró espacio disponible:

        return False  # Retorna False indicando fallo en la asignación.


    sobrante = (  # Calcula cuántos KB quedan sin usar dentro de la partición elegida.
        particion.tam
        - tam
    )


    base_original = (  # Guarda la dirección base donde empezaba la partición original.
        particion.base
    )


    particion.tam = tam  # Ajusta el tamaño de la partición al tamaño exacto del proceso (particiones variables).
    particion.estado = "OCUPADA"  # Marca la partición como ocupada.
    particion.id_proceso = (  # Asocia el ID del proceso a esta partición.
        id_proceso
    )

    particion.actualizar_limite()  # Actualiza el límite superior de la partición ocupada.


    if sobrante > 0:  # Si sobró espacio libre en la partición original:

        nueva_particion = Particion(  # Crea una nueva partición libre con el espacio sobrante.
            id=0,  # ID temporal (se renumerará enseguida).
            base=base_original + tam,  # Comienza inmediatamente después del fin de la partición asignada.
            tam=sobrante,  # Su tamaño es el espacio restante.
            estado="LIBRE"  # Queda disponible para futuros procesos.
        )

        memoria.append(  # Añade la nueva partición libre a la lista de memoria.
            nueva_particion
        )


    memoria.sort(  # Ordena todas las particiones por su dirección de inicio (base).
        key=lambda p: p.base
    )


    renumerar_particiones()  # Actualiza los números de ID de todas las particiones en orden secuencial.


    return True  # Retorna True confirmando que la memoria fue asignada con éxito.


def renumerar_particiones():  # Asigna identificadores numéricos consecutivos (1, 2, 3...) a las particiones.

    for i, particion in enumerate(  # Recorre las particiones enumerándolas a partir de 1.
        memoria,
        start=1
    ):

        particion.id = i  # Actualiza el atributo id de cada partición.


def recuperar_suspendidos():  # Intenta mover procesos de LISTOS/SUSPENDIDOS a LISTOS cuando se libera memoria.

    i = 0  # Índice para recorrer la cola de procesos suspendidos.

    while i < len(  # Itera mientras queden procesos por revisar en listos_suspendidos.
        listos_suspendidos
    ):

        proceso = (  # Obtiene el proceso suspendido en la posición actual.
            listos_suspendidos[i]
        )


        if entra_best_fit(  # Verifica si el proceso ahora cabe en algún hueco libre de memoria.
            proceso.tam
        ):

            listos_suspendidos.pop(  # Saca al proceso de la cola de suspendidos.
                i
            )

            proceso.estado = "LISTO"  # Cambia su estado a "LISTO".
            proceso.t_listo = reloj  # Registra el instante en que ingresa por primera vez a memoria/listo.

            asignar_memoria(  # Le asigna su partición correspondiente en memoria principal.
                proceso.id,
                proceso.tam
            )

            listos.append(  # Lo incorpora a la cola de procesos listos para ejecutar en CPU.
                proceso
            )

        else:  # Si todavía no hay espacio suficiente para este proceso:

            i += 1  # Avanza al siguiente proceso suspendido sin incrementar i cuando se extrae uno.


###### REPORTES ######


def imprimir_memoria():  # Muestra en consola la tabla detallada de particiones y el resumen de fragmentación.

    print(  # Imprime el título de la sección.
        "\nMEMORIA"
    )

    print(  # Imprime una línea separadora de 86 guiones.
        "-" * 86
    )

    print(  # Imprime los encabezados de columna alineados con ancho fijo.
        f"{'ID':<5}"
        f"{'Inicio':<10}"
        f"{'Fin':<10}"
        f"{'Tamaño':<12}"
        f"{'Estado':<12}"
        f"{'Proceso':<10}"
        f"{'Fragmentación':<14}"
    )

    print(  # Imprime otra línea separadora.
        "-" * 86
    )


    for particion in memoria:  # Recorre cada partición en memoria para imprimir su fila correspondiente.

        proceso = (  # Formatea el nombre del proceso (ej. "P1") o "-" si la partición está libre.
            f"P{particion.id_proceso}"
            if particion.id_proceso
            is not None
            else "-"
        )

        print(  # Imprime los datos de la partición (la fragmentación interna es siempre 0 KB en particiones variables).
            f"{particion.id:<5}"
            f"{particion.base:<10}"
            f"{particion.limite:<10}"
            f"{str(particion.tam) + ' KB':<12}"
            f"{particion.estado:<12}"
            f"{proceso:<10}"
            f"{('0 KB' if particion.estado == 'OCUPADA' else '-'):<14}"
        )


    print(  # Imprime línea de cierre de la tabla.
        "-" * 86
    )


    (  # Obtiene las estadísticas actuales de memoria libre y fragmentación externa.
        memoria_libre,
        cantidad_huecos,
        mayor_hueco,
        fragmentacion_externa

    ) = obtener_estado_memoria_libre()


    print(  # Imprime el resumen de memoria libre, cantidad de huecos, mayor hueco y fragmentación externa.
        f"Libre: {memoria_libre} KB | "
        f"Huecos: {cantidad_huecos} | "
        f"Mayor hueco: "
        f"{mayor_hueco} KB | "
        f"Frag. externa: "
        f"{fragmentacion_externa} KB"
    )


def imprimir_reportes_flags():  # Muestra el estado completo del sistema cada vez que ocurre un arribo o fin de proceso.

    # Encabezado del evento en color cian.
    print(  # Imprime barra superior decorativa en color cian brillante.
        "\n"
        + Fore.CYAN
        + Style.BRIGHT
        + "=" * 72
    )

    print(  # Imprime el título del evento junto con el instante actual del reloj.
        Fore.CYAN
        + Style.BRIGHT
        + f" EVENTO DEL SISTEMA | "
        f"Tiempo: {reloj}"
    )

    print(  # Imprime barra inferior decorativa en color cian brillante.
        Fore.CYAN
        + Style.BRIGHT
        + "=" * 72
    )


    # Arribo en verde.
    if evento_arribo:  # Si en este instante arribó al menos un proceso:

        print(  # Muestra aviso destacado en verde.
            Fore.GREEN
            + Style.BRIGHT
            + ">> ARRIBO DE PROCESO"
        )


    # Finalización en rojo.
    if evento_fin:  # Si en este instante finalizó un proceso:

        print(  # Muestra aviso destacado en rojo.
            Fore.RED
            + Style.BRIGHT
            + ">> FINALIZACIÓN DE PROCESO"
        )


    print(  # Imprime el subtítulo de la sección CPU.
        "\nCPU"
    )


    if ejecucion is not None:  # Si hay un proceso ejecutándose actualmente en la CPU:

        print(  # Muestra su ID, estado y tiempo de irrupción restante.
            f"P{ejecucion.id} | "
            f"Estado: EJECUCION | "
            f"TI restante: "
            f"{ejecucion.ti_restante}"
        )

    else:  # Si no hay ningún proceso en CPU:

        print(  # Indica que el procesador está desocupado.
            "OCIOSA"
        )


    print(  # Imprime el subtítulo de la cola de procesos LISTOS.
        "\nLISTOS"
    )


    if listos:  # Si hay procesos esperando en la cola de listos:

        for proceso in listos:  # Recorre e imprime cada proceso listo y su tiempo restante.

            print(
                f"P{proceso.id} | "
                f"TI restante: "
                f"{proceso.ti_restante}"
            )

    else:  # Si la cola está vacía:

        print(  # Indica que no hay procesos en cola de listos.
            "Vacía"
        )


    print(  # Imprime el subtítulo de la cola de procesos LISTOS / SUSPENDIDOS.
        "\nLISTOS / SUSPENDIDOS"
    )


    if listos_suspendidos:  # Si hay procesos esperando memoria en estado suspendido:

        for proceso in (  # Recorre e imprime cada proceso suspendido junto con su tamaño.
            listos_suspendidos
        ):

            print(
                f"P{proceso.id} | "
                f"Tamaño: "
                f"{proceso.tam} KB"
            )

    else:  # Si no hay procesos suspendidos:

        print(  # Indica que la cola está vacía.
            "Vacía"
        )


    imprimir_memoria()  # Llama a la función que dibuja la tabla del estado actual de la memoria.


    print(  # Imprime línea de cierre del reporte de evento en color cian.
        Fore.CYAN
        + Style.BRIGHT
        + "=" * 72
    )


    input(  # Pausa la simulación para que el usuario pueda analizar el estado paso a paso.
        "\nPresione ENTER "
        "para continuar..."
    )


###### MÉTRICAS ######


def calcular_metricas():  # Calcula los tiempos de retorno y de espera de todos los procesos al finalizar la simulación.

    for proceso in terminados:  # Recorre cada proceso que completó su ejecución.

        proceso.tiempo_retorno = (  # Calcula el tiempo de retorno (Tiempo Fin - Tiempo de ingreso a Listo).
            proceso.tiempo_fin
            - proceso.t_listo
        )

        proceso.tiempo_espera = (  # Calcula el tiempo de espera (Tiempo de Retorno - Tiempo de Irrupción).
            proceso.tiempo_retorno
            - proceso.ti
        )


def imprimir_reportes_finales():  # Genera la tabla resumen final con las métricas individuales y promedios globales.

    if not terminados:  # Si por alguna razón no hay procesos terminados, sale de la función.

        return


    print(  # Imprime encabezado de métricas finales.
        "\n" + "=" * 72
    )

    print(
        " MÉTRICAS FINALES"
    )

    print(
        "=" * 72
    )


    print(  # Imprime los encabezados de la tabla de métricas.
        f"{'Proceso':<12}"
        f"{'TA':<8}"
        f"{'TI':<8}"
        f"{'TF':<8}"
        f"{'Retorno':<12}"
        f"{'Espera':<12}"
    )


    print(  # Imprime línea separadora.
        "-" * 86
    )


    procesos_ordenados = sorted(  # Ordena los procesos terminados ascendentemente según su ID.
        terminados,
        key=lambda p: p.id
    )


    for proceso in (  # Imprime una fila por cada proceso con sus métricas calculadas.
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


    print(  # Imprime línea separadora.
        "-" * 86
    )


    promedio_retorno = sum(  # Calcula el promedio del tiempo de retorno entre todos los procesos.
        p.tiempo_retorno
        for p in terminados
    ) / len(terminados)


    promedio_espera = sum(  # Calcula el promedio del tiempo de espera entre todos los procesos.
        p.tiempo_espera
        for p in terminados
    ) / len(terminados)


    tiempo_total = max(  # Obtiene el instante en que terminó el último proceso (duración total de la simulación).
        p.tiempo_fin
        for p in terminados
    )


    throughput = (  # Calcula el rendimiento (throughput): procesos completados por unidad de tiempo.
        len(terminados)
        / tiempo_total
        if tiempo_total > 0
        else 0
    )


    print(  # Imprime el promedio de tiempo de retorno con 2 decimales.
        "Promedio tiempo de retorno: "
        f"{promedio_retorno:.2f}"
    )


    print(  # Imprime el promedio de tiempo de espera con 2 decimales.
        "Promedio tiempo de espera: "
        f"{promedio_espera:.2f}"
    )


    print(  # Imprime el throughput con 2 decimales.
        "Throughput: "
        f"{throughput:.2f} "
        "procesos/unidad de tiempo"
    )


    print(  # Imprime línea de cierre.
        "=" * 72
    )


###### INTERFAZ DE CONSOLA ######


def mostrar_inicio():  # Muestra la portada ASCII del simulador y los integrantes del grupo.

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


    input(  # Espera a que el usuario presione ENTER para avanzar a la carga del archivo.
        "        Presione ENTER "
        "para cargar el archivo CSV..."
    )


    os.system(  # Limpia la consola usando 'cls' en Windows ('nt') o 'clear' en Linux/Mac.
        "cls"
        if os.name == "nt"
        else "clear"
    )


def seleccionar_archivo_csv():  # Solicita al usuario la ruta del archivo CSV y limpia posibles comillas.

    print(  # Imprime encabezado de carga de archivo.
        "\n" + "=" * 72
    )

    print(
        " CARGA DE ARCHIVO CSV"
    )

    print(
        "=" * 72
    )


    print(  # Pide al usuario que escriba la ruta.
        "\nIngrese la ruta del "
        "archivo CSV a utilizar."
    )


    archivo = input(  # Lee la entrada del usuario y quita espacios en los extremos.
        "\nRuta del archivo CSV: "
    ).strip()


    while archivo == "":  # Repite la solicitud mientras el usuario ingrese una cadena vacía.

        print(
            "\nERROR: Debe ingresar "
            "una ruta o nombre de archivo."
        )

        archivo = input(
            "Ruta del archivo CSV: "
        ).strip()


    # Elimina comillas si la ruta
    # fue copiada desde Windows.
    archivo = archivo.strip('"')  # Quita comillas dobles si el usuario pegó la ruta con "Copiar como ruta".
    archivo = archivo.strip("'")  # Quita comillas simples en caso de que existan.


    return archivo  # Devuelve la ruta limpia del archivo CSV.


###### VARIABLES GLOBALES ######


reloj = 0  # Contador global que representa el tiempo actual de la simulación (inicia en t = 0).

activos = 0  # Contador de procesos admitidos actualmente en el sistema (grado de multiprogramación, máximo 5).


evento_arribo = False  # Bandera booleana que indica si llegó un proceso en el instante de reloj actual.

evento_fin = False  # Bandera booleana que indica si finalizó un proceso en el instante de reloj actual.


###### MEMORIA ######


# 0 - 99 KB:
# Sistema Operativo.
#
# 100 - 549 KB:
# 450 KB para procesos de usuario.

memoria = [  # Lista que representa la memoria principal; inicia con una única partición libre de 450 KB.

    Particion(
        id=1,  # Identificador de la partición inicial.
        base=100,  # Comienza en el KB 100 (los primeros 100 KB están reservados para el SO).
        tam=450,  # Tamaño total disponible para procesos de usuario (450 KB).
        estado="LIBRE"  # Inicialmente toda la memoria de usuario está libre.
    )

]


###### PANTALLA DE INICIO ######


mostrar_inicio()  # Ejecuta la pantalla de bienvenida.


###### CARGA Y VALIDACIÓN DE PROCESOS ######


ARCHIVO_PROCESOS = (  # Pide la ruta del archivo CSV al usuario.
    seleccionar_archivo_csv()
)


nuevos = cargar_procesos_csv(  # Lee y carga los procesos del CSV en la cola de procesos 'nuevos'.
    ARCHIVO_PROCESOS
)


errores = validar_procesos(  # Ejecuta las validaciones sobre los procesos cargados.
    nuevos
)


if errores:  # Si se detectó algún error en los datos de entrada:

    print(  # Imprime encabezado de error.
        "\n" + "=" * 72
    )

    print(
        " ERROR EN LOS DATOS DE ENTRADA"
    )

    print(
        "=" * 72
    )


    for error in errores:  # Muestra cada uno de los errores encontrados.

        print(
            f"- {error}"
        )


    print(  # Cierra el cuadro de error.
        "=" * 72
    )


    salir()  # Detiene el programa antes de iniciar la simulación.


###### COLAS DEL SISTEMA ######


n_total = len(  # Guarda la cantidad total de procesos que deben ejecutarse para saber cuándo termina la simulación.
    nuevos
)


listos = []  # Cola de procesos que están en memoria principal listos para usar la CPU.

listos_suspendidos = []  # Cola de procesos admitidos que esperan en disco (suspendidos) por falta de memoria.

terminados = []  # Lista donde se van almacenando los procesos que ya finalizaron su ejecución.


ejecucion = None  # Referencia al proceso que está usando la CPU actualmente (None si la CPU está ociosa).


###### PROCESOS CARGADOS ######


print(  # Muestra una tabla previa con todos los procesos leídos del CSV antes de arrancar.
    "\n" + "=" * 72
)

print(
    " PROCESOS CARGADOS DESDE CSV"
)

print(
    "=" * 72
)


print(  # Imprime encabezados de la tabla previa.
    f"{'ID':<8}"
    f"{'Tamaño':<12}"
    f"{'TA':<8}"
    f"{'TI':<8}"
    f"{'Estado':<15}"
)


print(  # Línea separadora.
    "-" * 72
)


for proceso in nuevos:  # Imprime los datos de cada proceso cargado.

    print(
        f"{'P' + str(proceso.id):<8}"
        f"{str(proceso.tam) + ' KB':<12}"
        f"{proceso.ta:<8}"
        f"{proceso.ti:<8}"
        f"{proceso.estado:<15}"
    )


print(  # Línea de cierre de la tabla.
    "=" * 72
)


print(  # Confirma la ruta del archivo cargado.
    "\nArchivo cargado correctamente:"
)

print(
    ARCHIVO_PROCESOS
)


input(  # Espera confirmación del usuario para comenzar el ciclo de reloj.
    "\nPresione ENTER "
    "para iniciar la simulación..."
)


###### BUCLE PRINCIPAL ######


while len(terminados) < n_total:  # El ciclo continúa avanzando unidad por unidad hasta que terminen todos los procesos.


    # ==========================================================
    # 1. VERIFICAR SI EL PROCESO EN EJECUCIÓN TERMINÓ
    # ==========================================================

    if (  # Comprueba si hay un proceso en CPU cuyo tiempo de irrupción restante llegó a 0.
        ejecucion is not None
        and ejecucion.ti_restante == 0
    ):

        ejecucion.tiempo_fin = (  # Registra el instante de reloj actual como tiempo de finalización.
            reloj
        )

        ejecucion.estado = (  # Cambia el estado del proceso a "TERMINADO".
            "TERMINADO"
        )

        terminados.append(  # Mueve el proceso a la lista de terminados.
            ejecucion
        )

        activos -= 1  # Decrementa el contador de procesos activos en el sistema (libera un cupo de multiprogramación).


        liberar_memoria(  # Libera la partición de memoria que ocupaba el proceso finalizado.
            ejecucion.id
        )

        fusionar_huecos()  # Une particiones libres contiguas si se formaron huecos adyacentes.


        evento_fin = True  # Activa la bandera para mostrar el reporte de finalización en este instante.

        ejecucion = None  # Deja la CPU libre.


        # ======================================================
        # 2. RECUPERAR LISTOS / SUSPENDIDOS
        # ======================================================

        recuperar_suspendidos()  # Intenta ingresar a memoria procesos que estaban en LISTOS/SUSPENDIDOS.


    # ==========================================================
    # 3. DETECTAR ARRIBOS
    # ==========================================================

    for proceso in nuevos:  # Revisa si algún proceso de la lista de nuevos tiene Tiempo de Arribo igual al reloj actual.

        if proceso.ta == reloj:  # Si coincide con el tiempo actual:

            evento_arribo = True  # Activa la bandera de arribo para mostrar reporte en pantalla.


    # ==========================================================
    # 4. ADMITIR PROCESOS NUEVOS
    # ==========================================================

    while (  # Admite procesos siempre que haya menos de 5 activos (multiprogramación) y ya hayan arribado.
        activos < 5
        and nuevos
        and nuevos[0].ta <= reloj
    ):

        proc_admitido = (  # Extrae el primer proceso de la cola de nuevos.
            nuevos.pop(0)
        )


        if entra_best_fit(  # Evalúa si existe una partición libre en memoria donde quepa el proceso.
            proc_admitido.tam
        ):

            proc_admitido.estado = (  # Si entra, su estado pasa a "LISTO".
                "LISTO"
            )

            proc_admitido.t_listo = reloj  # Marca el instante en que entra a listo (referencia para tiempo de retorno).

            asignar_memoria(  # Le asigna memoria mediante Best-Fit.
                proc_admitido.id,
                proc_admitido.tam
            )

            listos.append(  # Agrega el proceso a la cola de listos.
                proc_admitido
            )


        else:  # Si hay cupo de multiprogramación (< 5), pero no hay hueco suficiente en memoria:

            proc_admitido.estado = (  # El proceso pasa al estado "LISTO_SUSPENDIDO".
                "LISTO_SUSPENDIDO"
            )

            listos_suspendidos.append(  # Se envía a la cola de listos/suspendidos.
                proc_admitido
            )


        activos += 1  # Incrementa el contador de procesos activos (cuenta tanto listos como suspendidos).


    # ==========================================================
    # 5. PLANIFICACIÓN SRTF
    # ==========================================================

    proc_menor_ti = (  # Busca en la cola de listos el proceso con menor TI restante (desempata por TA y luego por ID).

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

    if ejecucion is None:  # Si la CPU está desocupada:


        if (  # Y existe al menos un proceso en la cola de listos:
            proc_menor_ti
            is not None
        ):

            listos.remove(  # Extrae ese proceso de la cola de listos.
                proc_menor_ti
            )

            proc_menor_ti.estado = (  # Cambia su estado a "EJECUCION".
                "EJECUCION"
            )

            ejecucion = (  # Lo asigna a la CPU.
                proc_menor_ti
            )


    # ==========================================================
    # CPU OCUPADA
    # ==========================================================

    else:  # Si la CPU ya tiene un proceso ejecutándose (política expropiativa SRTF):


        if (  # Compara si el candidato listo tiene estrictamente menor TI restante que el proceso en CPU.
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


            ejecucion.estado = (  # Expropia al proceso actual: lo devuelve al estado "LISTO".
                "LISTO"
            )

            listos.append(  # Reingresa el proceso expropiado a la cola de listos.
                ejecucion
            )


            listos.remove(  # Saca al nuevo proceso más corto de la cola de listos.
                proc_menor_ti
            )


            proc_menor_ti.estado = (  # Cambia su estado a "EJECUCION".
                "EJECUCION"
            )


            ejecucion = (  # Asigna el nuevo proceso a la CPU.
                proc_menor_ti
            )


    # ==========================================================
    # 7. MOSTRAR REPORTE SI HUBO EVENTO
    # ==========================================================

    if (  # Si en este ciclo ocurrió un arribo o una finalización de proceso:
        evento_arribo
        or evento_fin
    ):

        imprimir_reportes_flags()  # Imprime el reporte completo del estado del sistema y memoria.


        evento_arribo = False  # Reinicia la bandera de arribo para el próximo ciclo.

        evento_fin = False  # Reinicia la bandera de finalización para el próximo ciclo.


    # ==========================================================
    # 6. EJECUTAR UNA UNIDAD DE CPU
    # ==========================================================

    if ejecucion is not None:  # Si hay un proceso en la CPU:

        ejecucion.ti_restante -= 1  # Consume 1 unidad de tiempo de su tiempo de irrupción restante.


    # ==========================================================
    # 8. AVANZAR RELOJ
    # ==========================================================

    reloj += 1  # Incrementa el reloj global del sistema en 1 unidad de tiempo.


###### FIN DE LA SIMULACIÓN ######


calcular_metricas()  # Calcula tiempos de retorno y espera de todos los procesos finalizados.


imprimir_reportes_finales()  # Muestra la tabla de métricas finales y promedios.


print(  # Imprime cartel verde de finalización exitosa.
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


input(  # Pausa final antes de cerrar la ventana de la consola.
    "\nPresione ENTER para finalizar "
    "y cerrar el programa..."
)