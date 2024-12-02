import pandas as pd  # Importa la librería pandas para manejo de datos en formato DataFrame
import networkx as nx  # Importa la librería NetworkX para la manipulación de grafos y redes
import matplotlib.pyplot as plt  # Importa matplotlib para la visualización de gráficos
import heapq  # Importa heapq para usar una cola de prioridad en la búsqueda de rutas

# Cargar los archivos CSV con los datos de estaciones y rutas
estaciones_df = pd.read_csv('./estaciones_transmilenio.csv')
rutas_df = pd.read_csv('./rutas_transmileniov2.csv')

# Crear un grafo dirigido donde se almacenarán las estaciones como nodos y las rutas como aristas
G = nx.DiGraph()

# Agregar nodos al grafo, con la troncal de cada estación
for _, row in estaciones_df.iterrows():
    G.add_node(row['Estación'], troncal=row['Troncal'])

# Agregar aristas al grafo, basadas en las rutas entre estaciones
for _, row in rutas_df.iterrows():
    G.add_edge(
        row['Estación Origen'], row['Estación Destino'],
        ruta=row['Ruta'], tipo=row['Tipo de Recorrido']
    )

# Función para buscar todas las rutas mínimas en términos de transbordos
def buscar_todas_las_rutas_minimas(origen, destino):
    padres = {origen: None}
    distancias = {origen: 0}  # Distancia en términos de estaciones
    rutas = {origen: None}    # Ruta que se está usando en cada nodo
    cola = [(0, origen)]  # Cola de prioridad (distancia, estación)
    todas_las_rutas = []  # Lista de rutas encontradas

    while cola:
        (distancia, nodo) = heapq.heappop(cola)
        
        if nodo == destino:
            # Cuando se llega al destino, reconstruir la ruta y agregarla a las soluciones
            ruta = []
            while nodo:
                ruta.append(nodo)
                nodo = padres.get(nodo, None)
            ruta.reverse()
            todas_las_rutas.append(ruta)
            continue  # Aún pueden haber otras rutas con el mismo número de transbordos
        
        for vecino in G.neighbors(nodo):
            tramo = G[nodo][vecino]
            peso = 1  # Cada arista cuenta como una estación
            if rutas[nodo] != tramo['ruta']:  # Si se cambia de ruta, se incrementa el transbordo
                peso = 2  # Penalizamos el cambio de ruta
            nueva_distancia = distancia + peso
            if vecino not in distancias or nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                padres[vecino] = nodo
                rutas[vecino] = tramo['ruta']
                heapq.heappush(cola, (nueva_distancia, vecino))
            elif nueva_distancia == distancias[vecino]:  # Si la distancia es igual, agregamos la ruta
                padres[vecino] = nodo
                rutas[vecino] = tramo['ruta']
                heapq.heappush(cola, (nueva_distancia, vecino))

    return todas_las_rutas

# Función para calcular el número de transbordos en una ruta
def calcular_transbordos(ruta):
    rutas_usadas = []
    transbordos = 0
    for i in range(len(ruta) - 1):
        tramo = G[ruta[i]][ruta[i + 1]]
        if tramo['ruta'] not in rutas_usadas:
            if rutas_usadas:  # Si ya hay rutas registradas, significa que hubo un transbordo
                transbordos += 1
            rutas_usadas.append(tramo['ruta'])
    return transbordos

# Función para mostrar y graficar el camino más corto
def mostrar_y_graficar_camino(origen, destino):
    # Verificar si las estaciones existen en el grafo
    if origen not in G.nodes or destino not in G.nodes:
        print("Una o ambas estaciones no existen en el sistema.")
        return

    # Buscar todas las rutas mínimas
    todas_las_rutas = buscar_todas_las_rutas_minimas(origen, destino)
    if not todas_las_rutas:
        print(f"No se puede llegar desde {origen} hasta {destino}.")
        return

    # Seleccionar la ruta con el menor número de transbordos
    mejor_ruta = min(todas_las_rutas, key=lambda ruta: calcular_transbordos(ruta))
    transbordos = calcular_transbordos(mejor_ruta)

    # Mostrar información sobre el camino
    print("\nCamino más corto (mínimas estaciones) y con menos transbordos:")
    print(" -> ".join(mejor_ruta))
    print(f"\nNúmero de estaciones visitadas: {len(mejor_ruta)}")
    print(f"Transbordos realizados: {transbordos}")

    print("\nTramos:")
    tramos = []
    for i in range(len(mejor_ruta) - 1):
        tramo = G[mejor_ruta[i]][mejor_ruta[i + 1]]
        tramos.append((mejor_ruta[i], mejor_ruta[i + 1]))
        print(f"Tramo: {tramo['ruta']} ({tramo['tipo']}) de {mejor_ruta[i]} a {mejor_ruta[i + 1]}")

    # Colores para los nodos según su troncal
    troncal_colors = {
        'A': 'darkblue', 'B': 'lightgreen', 'C': 'yellow', 'D': 'purple',
        'E': 'brown', 'F': 'red', 'G': 'lightblue', 'H': 'orange', 
        'J': 'pink', 'K': 'grey', 'L': 'magenta'
    }

    node_fill_colors = []  # Colores de relleno para los nodos
    node_edge_colors = []  # Colores de borde para los nodos
    edge_colors = []       # Colores de los arcos

    # Asignar colores a los nodos y aristas
    for nodo in G.nodes:
        if nodo in mejor_ruta:
            troncal = G.nodes[nodo]['troncal']
            node_fill_colors.append('green')  # Nodo en la ruta óptima (relleno verde)
            node_edge_colors.append(troncal_colors.get(troncal, 'grey'))  # Bordes con el color de la troncal
        else:
            troncal = G.nodes[nodo]['troncal']
            node_fill_colors.append('white')  # Nodo no en la ruta óptima (relleno blanco)
            node_edge_colors.append(troncal_colors.get(troncal, 'grey'))  # Bordes con el color de la troncal
        
        for u, v, data in G.edges(nodo, data=True):
            edge_colors.append('black')  # Arcos en negro por defecto

    # Graficar el grafo completo
    plt.figure(figsize=(12, 12))  # Tamaño de la figura
    pos = nx.kamada_kawai_layout(G)  # Layout para organizar los nodos

    # Dibujar todos los nodos y aristas con los colores asignados
    nx.draw(
        G, pos, with_labels=True, node_size=700, node_color=node_fill_colors,
        font_size=8, font_color="black", font_weight="bold", edge_color=edge_colors,
        width=2, edgecolors=node_edge_colors  # Color de bordes de los nodos
    )

    # Dibujar el camino sugerido en verde y rojo
    nx.draw_networkx_edges(G, pos, edgelist=tramos, edge_color="red", width=2)  # Arcos de la ruta óptima en rojo
    nx.draw_networkx_nodes(G, pos, nodelist=mejor_ruta, node_color="green", node_size=800, edgecolors="green")

    # Etiquetas de las rutas en los arcos
    edge_labels = nx.get_edge_attributes(G, 'ruta')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    plt.title("Camino sugerido en el Sistema TransMilenio")  # Título del gráfico
    plt.show()  # Mostrar el gráfico

# Solicitar estaciones de origen y destino al usuario
print("Introduce las estaciones para buscar el camino más corto.")
origen = input("Introduce la estación de origen: ")
destino = input("Introduce la estación de destino: ")

# Mostrar y graficar el camino
mostrar_y_graficar_camino(origen, destino)
