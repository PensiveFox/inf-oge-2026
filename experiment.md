import networkx as nx
import matplotlib.pyplot as plt

# создаём ориентированный граф
G = nx.DiGraph()
edges = [
    ('A','B'), ('A','C'), 
    ('B','D'), ('B','E'), 
    ('C','F'), 
    ('D','H'), ('E','H'), 
    ('F','G'), ('G','H')
]
G.add_edges_from(edges)

# координаты для наглядного расположения вершин
pos = {
    'A': (0,0),
    'B': (1,1), 'C': (1,-1),
    'D': (2,2), 'E': (2,0),
    'F': (2,-2), 'G': (3,-2),
    'H': (4,0)
}

# находим все простые пути из A в H
paths = list(nx.all_simple_paths(G, source='A', target='H'))

# создаём кадры
for i, path in enumerate(paths):
    plt.figure(figsize=(6,4))
    # рисуем все рёбра бледно
    nx.draw(G, pos, with_labels=True, node_color='lightgray', edge_color='lightgray', node_size=1000)
    # подсвечиваем текущий путь
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='orange', node_size=1000)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2)
    
    plt.title(f'Путь {i+1}: {" -> ".join(path)}')
    plt.axis('off')
    plt.savefig(f'frame_{i+1}.png')
    plt.close()
