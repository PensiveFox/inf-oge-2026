import networkx as nx
import matplotlib.pyplot as plt

# Создаём ориентированный граф
G = nx.DiGraph()
edges = [
    ('A', 'B'), ('A', 'C'), 
    ('B', 'D'), ('B', 'E'), 
    ('C', 'F'), 
    ('D', 'H'), ('E', 'H'), 
    ('F', 'G'), ('G', 'H')
]
G.add_edges_from(edges)

# Координаты для наглядного расположения вершин
pos = {
    'A': (0, 0),
    'B': (1, 1), 'C': (1, -1),
    'D': (2, 2), 'E': (2, 0),
    'F': (2, -2), 'G': (3, -2),
    'H': (4, 0)
}

# Находим все простые пути из A в H
paths = list(nx.all_simple_paths(G, source='A', target='H'))

print(f"Найдено путей из A в H: {len(paths)}")
print("Пути:")
for i, path in enumerate(paths, 1):
    print(f"  {i}. {' -> '.join(path)}")

# Создаём кадры для каждого пути
for i, path in enumerate(paths, 1):
    plt.figure(figsize=(10, 6))
    
    # Определяем рёбра текущего пути
    path_edges = list(zip(path, path[1:]))
    path_edges_set = set(path_edges)
    
    # Рёбра не в пути (бледные)
    other_edges = [edge for edge in G.edges() if edge not in path_edges_set]
    
    # Узлы не в пути
    other_nodes = [node for node in G.nodes() if node not in path]
    
    # Рисуем узлы не в пути (серые)
    nx.draw_networkx_nodes(G, pos, nodelist=other_nodes, 
                          node_color='lightgray', node_size=1200, alpha=0.6)
    
    # Рисуем узлы в пути (оранжевые)
    nx.draw_networkx_nodes(G, pos, nodelist=path, 
                          node_color='orange', node_size=1200)
    
    # Рисуем бледные рёбра (не в пути)
    nx.draw_networkx_edges(G, pos, edgelist=other_edges, 
                          edge_color='lightgray', width=1.5, alpha=0.4,
                          arrows=True, arrowsize=15, arrowstyle='->')
    
    # Рисуем яркие рёбра (путь)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                          edge_color='red', width=3,
                          arrows=True, arrowsize=20, arrowstyle='->')
    
    # Подписи вершин
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold')
    
    plt.title(f'Путь {i}/{len(paths)}: {" → ".join(path)}', 
             fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    # Сохраняем кадр
    filename = f'frame_{i:02d}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Сохранён кадр: {filename}")
    plt.close()

print(f"\nВсего создано кадров: {len(paths)}")
print("Кадры сохранены как frame_01.png, frame_02.png, и т.д.")
