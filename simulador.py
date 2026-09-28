###### CLASES ######
#Definción de clase proceso.
class Proceso: 
    def __init__(self, id, tam, ta, ti):
        self.id = id
        self.tam = tam
        self.ta = ta
        self.ti = ti
        self.ti_restante = ti
        self.estado = "PRE_NUEVO"

class Particion: #Temporal, idea general de la clase.
    def __init__(self, id, base, limite, tam, estado = "LIBRE"):
        self.id = id
        self.base = base
        self.limite = limite
        self.tam = tam
        self.estado = estado
        self.id_proceso = None

###### FUNCIÓN PARA SIMULAR LECTURA DE ARCHIVO SCV (HARDCODEADO!!) ######
def cargar_prenuevos_prueba():
    # Creamos 3 procesos de prueba: Proceso(id, tam, ta, ti)
    p1 = Proceso(1, 100, 0, 5)   # Llega en t=0, necesita 5 de CPU
    p2 = Proceso(2, 250, 2, 3)   # Llega en t=2, necesita 3 de CPU
    p3 = Proceso(3, 50, 4, 2)    # Llega en t=4, necesita 2 de CPU
    
    lista_procesos = [p1, p2, p3]
    
    # Los ordenamos por tiempo de arribo (ta)
    lista_procesos.sort(key=lambda p: p.ta)
    
    return lista_procesos

#Pasa por consola los procesos leídos, ya están en PRE_NUEVO y ordenados por tiempo de arribo.
prenuevos = cargar_prenuevos_prueba()
print(f"Cantidad de procesos cargados: {len(prenuevos)}")
for p in prenuevos:
    print(f"ID: {p.id} | TA: {p.ta} | TI: {p.ti} | Estado: {p.estado}")


####### OTRAS FUNCIONES ########
def liberar_memoria(id_proceso):
    # Desarrollado aparte.
    pass

def fusionar_huecos():
    # Desarrollado aparte.
    pass

def entra_best_fit(tam):
    # Devuelve True temporalmente para poder simular.
    return True

def asignar_memoria(id_proceso, tam):
    # Desarrollado aparte.
    pass

def calcular_metricas():
    # Desarrollado aparte.
    pass

def imprimir_reportes_flags():
    # Desarrollado aparte. Esta función imprime reportes de las banderas de evento_arribo y evento_fin
    pass

def imprimir_reportes_finales():
    # Desarrollado aparte. Esta función imprime reportes finales, cuando terminan todos los procesos.
    pass

###### DECLARACIÓN E INICIACIÓN DE VARIABLES GLOBALES ######
reloj = 0 #Cambié 't' por 'reloj' para que sea más legible.
activos = 0
evento_arribo = False
evento_fin = False

#Declaración de las listas que necesita el SO:
pre_nuevos = cargar_prenuevos_prueba() #Ya se cargan ordenados.
n_total = len(pre_nuevos) #la longitud de pre_nuevos es la cantidad de procesos a ejecutar.
nuevos = []
listos = []
suspendidos = []
terminados = []
ejecucion = None #Como es un solo programa a la vez, no tiene sentido que sea una lista, lo manejo como una variable que contiene un proceso si la CPU está ejecutando y None si está libre.

###### BUCLE DEL PROCESO PRINCIPAL ######
while len(terminados) < n_total: 
    #1. Verificar si el proceso en CPU terminó.
    if ejecucion is not None and ejecucion.ti_restante == 0:
        ejecucion.estado = "TERMINADO"
        terminados.append(ejecucion)
        activos -= 1
        liberar_memoria(ejecucion.id)
        fusionar_huecos()
        evento_fin = True
        ejecucion = None

        #2. Revisar la cola de suspendidos.
        if len(suspendidos) > 0 and entra_best_fit(suspendidos[0].tam):
            proc_recuperado = suspendidos.pop(0)
            proc_recuperado.estado = "LISTO"
            asignar_memoria(proc_recuperado.id, proc_recuperado.tam)
            listos.append(proc_recuperado)

    #3. Verificar el tiepo de arribo de pre_nuevos.
    #Lo cambio por un while porque puede haber dos procesos con el mismo TA, los proceso a todos en el intante del reloj correspondiente.
    while len(pre_nuevos) > 0 and pre_nuevos[0].ta == reloj:
        evento_arribo = True
        proc_arribado = pre_nuevos.pop(0)
        proc_arribado.estado = "NUEVO"
        nuevos.append(proc_arribado)

    #4. Pregunto por la cantidad de activos.
    #Si hay lugar en activos y existen procesos en NUEVO:
    while activos < 5 and len(nuevos) > 0:
        proc_admitido = nuevos.pop(0)
        #Si el proceso Nuevo entra en la memoria, se carga y pasa a LISTO:
        if entra_best_fit(proc_admitido.tam): 
            proc_admitido.estado = "LISTO"
            asignar_memoria(proc_admitido.id, proc_admitido.tam)
            listos.append(proc_admitido)
        #Si no entra en la memoria pasa a SUSPENDIDO:
        else:
            proc_admitido.estado = "SUSPENDIDO"
            suspendidos.append(proc_admitido)
        activos += 1

    #5. Pregunto por el estado de la CPU para asignar un nuevo proceso a ejecución:
        #Utiliza una función lambda para recorrer la lista y sustraer el proceso con menor TI restante. Se fija en el restante porque pudo haber pasado un proceso de suspendido a listo tras una expropiación. Además, en caso de que no haya más proceso listos, proc_menorTI vale None.

        proc_menorTI = min(listos, key = lambda p: p.ti_restante) if len(listos) > 0 else None
    #Si la CPU está libre:
    if ejecucion is None:

        #Y se encontró un proceso con menor TI:
        if proc_menorTI:
            #Ese proceso se quita de la lista de listos:
            listos.remove(proc_menorTI)
            proc_menorTI.estado = "EJECUCION"
            ejecucion = proc_menorTI
        #Si no hay procesos listos, la CPU permanece ociosa un batido del reloj.

    #Si la CPU está ocupada, 
    else:
        #primero tengo que preguntarme si el menor TI de los listos es más chico que el TI restante del proceso que está ejecutando:
        if proc_menorTI and proc_menorTI < ejecucion.ti_restante:
            #Si es así ocurre la expropiacion.
            #NOTA IMPORTANTE: Gemini me dijo que cuando a un proceso le quitan la CPU por expropiación, el proceso no sale de la memoria RAM (no se suspende); simplemente vuelve a la cola de LISTO a esperar su próximo turno en el procesador.
            #Si lo mandaras a SUSPENDIDO, tendrías que liberarle la memoria, escribirlo a disco y dejarlo afuera de la RAM sin necesidad, cuando en realidad ya está cargado y listo para continuar apenas se libere el procesador.

            #El ejecutado pasa a listo:
            ejecucion.estado = "LISTO"
            listos.append(ejecucion)

            #El candidato toma la CPU:
            listos.remove(proc_menorTI)
            proc_menorTI.estado = "EJECUCION"
            ejecucion = proc_menorTI

        #Si no hay listo con menor TI restante, no pasa nada, sigue con el actual.
    
    #El proceso ejecutándose resta un TI:
    ejecucion.ti_restante -= 1

    #6.Pregunto si ocurrió algun evento para imprimir las métricas correspondientes.
    if evento_arribo or evento_fin:
        imprimir_reportes_flags()
        evento_arribo = False
        evento_fin = False

    #7. El reloj avanza!!
    reloj += 1

#A esta altura ya terminó el bucle y todos los procesos.
calcular_metricas()
imprimir_reportes_finales()

#FIN!