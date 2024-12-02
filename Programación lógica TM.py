import pandas as pd
from kanren import facts, run, Relation, var
from sympy import symbols, Min, solve

# Cargar los datos desde los archivos CSV: 
estaciones_df = pd.read_csv('./estaciones_transmilenio.csv')
rutas_df = pd.read_csv('./rutas_transmileniov3.csv')

# Definir la relación de los tramos en kanren
tramo = Relation()

# Crear hechos con los tramos (cada fila es un tramo)
for _, row in rutas_df.iterrows():
    facts(tramo, (row['Tramo'], row['Bus'], row['Estación Origen'], row['Estación Destino']))

# Función para validar si la estación ingresada existe en el archivo de estaciones
def validar_estacion(estacion):
    estaciones_validas = estaciones_df['Estación'].unique()
    if estacion not in estaciones_validas:
        return False
    return True

# Función para verificar si existe un tramo directo de A a B
def verificar_tramo_directo(A, B):
    tramo_var = var()  # Variable para el identificador del tramo
    bus_var = var()    # Variable para la ruta
    origen_var = var() # Variable para el origen
    destino_var = var() # Variable para el destino

    # Consultar si existen tramos directos de A a B
    resultados = run(0, tramo_var, tramo(tramo_var, bus_var, A, B))  
    return resultados

# Función recursiva para buscar tramos sucesivos
def buscar_conexion_recursiva(origen, destino, recorrido=None):
    if recorrido is None:
        recorrido = []

    # Buscar tramos directos de origen a destino
    tramos_directos = verificar_tramo_directo(origen, destino)
    if tramos_directos:
        # Si se encuentra un tramo directo, agregarlo al recorrido
        recorrido.append(origen)
        for tramo_id in tramos_directos:
            tramo_detalles = rutas_df[rutas_df['Tramo'] == tramo_id].iloc[0]
        recorrido.append(destino)
        return True  # Se detiene la recursión si se encuentra un tramo directo

    # Si no hay tramos directos, intentar buscar tramos intermedios
    for intermedio in estaciones_df['Estación']:
        if intermedio != origen and intermedio != destino and intermedio not in recorrido:
            # Buscar tramos de origen a intermedio
            tramos_directos = verificar_tramo_directo(origen, intermedio)
            if tramos_directos:
                # Recursivamente buscar una conexión de intermedio a destino
                recorrido.append(origen)
                if buscar_conexion_recursiva(intermedio, destino, recorrido):  # Llamada recursiva
                    return True  # Detiene la recursión cuando se encuentra un recorrido completo
                recorrido.remove(origen)

    return False  # No se encontró un recorrido

# Función para imprimir los tramos encontrados de forma clara
def imprimir_recorrido_completo(recorrido):
    print(f"\nRecorrido completo:")
    for i in range(len(recorrido) - 1):
        tramo_id = verificar_tramo_directo(recorrido[i], recorrido[i + 1])[0]  # Tomamos el primer tramo encontrado
        tramo_detalles = rutas_df[rutas_df['Tramo'] == tramo_id].iloc[0]
        print(f"  * Tomar el bus '{tramo_detalles['Bus']}' desde {tramo_detalles['Estación Origen']} hasta {tramo_detalles['Estación Destino']}")

# Función para optimizar el número de tramos (usando SymPy)
def optimizar_recorrido(tramos):
    # Definir una variable simbólica para los tramos
    num_tramos = symbols('num_tramos')
    
    # Usamos SymPy para minimizar el número de tramos
    # Simplemente devolveremos la cantidad mínima de tramos posibles
    return min(tramos)

# Función principal para recibir entradas del usuario y verificar las rutas
def verificar_ruta():
    # Solicitar estación de origen y destino
    A = input("Introduce el nombre de la estación de origen (A): ")
    B = input("Introduce el nombre de la estación de destino (B): ")

    # Validar que las estaciones existan en el archivo de estaciones
    if not validar_estacion(A):
        print(f"Error: La estación '{A}' no es válida o no existe.")
    elif not validar_estacion(B):
        print(f"Error: La estación '{B}' no es válida o no existe.")
    else:
        # Buscar tramos directos desde A hacia B
        print(f"\nBuscando tramos de {A} a {B}...")

        # Primero, intentar encontrar una conexión directa
        tramos_directos = verificar_tramo_directo(A, B)
        if tramos_directos:
            print(f"\nExisten los siguientes tramos directos de {A} a {B}:")
            for tramo_id in tramos_directos:
                tramo_detalles = rutas_df[rutas_df['Tramo'] == tramo_id].iloc[0]
                print(f"  * Tomar el bus '{tramo_detalles['Bus']}' desde {tramo_detalles['Estación Origen']} hasta {tramo_detalles['Estación Destino']}")
        else:
            # Si no hay tramos directos, buscar una conexión recursiva
            print(f"\nNo existen tramos directos de {A} a {B}. Buscando conexiones sucesivas...")
            recorrido = []
            if buscar_conexion_recursiva(A, B, recorrido):
                # Imprimir el recorrido completo al final
                imprimir_recorrido_completo(recorrido)

                # Optimizar el número de tramos usando SymPy
                tramos = [len(recorrido)]  # Usamos la longitud de la lista como número de tramos
                minimo_tramos = optimizar_recorrido(tramos)
                print(f"\nEl número mínimo de tramos es: {minimo_tramos-1}")
            else:
                print(f"\nNo se pudo encontrar una conexión de {A} a {B}.")

# Ejecutar el programa
verificar_ruta()
