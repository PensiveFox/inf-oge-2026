import json
import networkx as nx
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Имя проекта (можно изменить или передать как аргумент)
project_name = input("Введите имя проекта (или Enter для автоматического): ").strip()
if not project_name:
    project_name = f"graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Создаём папку для выходных файлов
output_dir = f'output/{project_name}'
os.makedirs(output_dir, exist_ok=True)

print(f"📁 Папка для сохранения: {output_dir}")
print()

# Загружаем граф из JSON файла
json_file = input("Путь к JSON файлу (или Enter для 'json/graph-1.json'): ").strip()
if not json_file:
    json_file = 'json/graph-1.json'

with open(json_file, 'r', encoding='utf-8') as f:
    graph_data = json.load(f)

# Создаём ориентированный граф
G = nx.DiGraph()

# Добавляем рёбра из JSON
edges = [(edge['from'], edge['to']) for edge in graph_data['edges']]
G.add_edges_from(edges)

# Создаём словарь позиций из JSON - используем координаты напрямую
pos = {}

for node in graph_data['nodes']:
    label = node['label']
    x = node['x']
    y = -node['y']  # Только инвертируем Y для правильного отображения
    pos[label] = (x, y)

print("=" * 50)
print("Граф загружен из JSON")
print("=" * 50)
print(f"Вершины: {list(G.nodes())}")
print(f"Рёбра: {list(G.edges())}")
print()

# Находим все простые пути из A в H
start_node = 'A'
end_node = 'H'

if start_node not in G.nodes():
    print(f"❌ Вершина '{start_node}' не найдена в графе!")
    exit(1)

if end_node not in G.nodes():
    print(f"❌ Вершина '{end_node}' не найдена в графе!")
    exit(1)

paths = list(nx.all_simple_paths(G, source=start_node, target=end_node))

print(f"Найдено путей из {start_node} в {end_node}: {len(paths)}")
print()
print("Все пути:")
for i, path in enumerate(paths, 1):
    print(f"  {i}. {' → '.join(path)}")
print()

# Создаём кадры для каждого пути
for i, path in enumerate(paths, 1):
    plt.figure(figsize=(14, 8))
    
    # Определяем рёбра текущего пути
    path_edges = list(zip(path, path[1:]))
    path_edges_set = set(path_edges)
    
    # Рёбра не в пути (бледные)
    other_edges = [edge for edge in G.edges() if edge not in path_edges_set]
    
    # Узлы не в пути
    other_nodes = [node for node in G.nodes() if node not in path]
    
    # Рисуем узлы не в пути (серые)
    nx.draw_networkx_nodes(G, pos, nodelist=other_nodes, 
                          node_color='lightgray', node_size=1500, alpha=0.5)
    
    # Рисуем узлы в пути (оранжевые)
    nx.draw_networkx_nodes(G, pos, nodelist=path, 
                          node_color='orange', node_size=1500, edgecolors='#ff8c00', linewidths=3)
    
    # Рисуем бледные рёбра (не в пути)
    nx.draw_networkx_edges(G, pos, edgelist=other_edges, 
                          edge_color='lightgray', width=2, alpha=0.4,
                          arrows=True, arrowsize=15, arrowstyle='->')
    
    # Рисуем яркие рёбра (путь)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                          edge_color='red', width=4,
                          arrows=True, arrowsize=25, arrowstyle='->')
    
    # Подписи вершин
    nx.draw_networkx_labels(G, pos, font_size=16, font_weight='bold', font_color='#333')
    
    plt.title(f'Путь {i}/{len(paths)}: {" → ".join(path)}', 
             fontsize=18, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # Сохраняем кадр в папку проекта
    filename = f'path_{i:02d}.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✅ Сохранён кадр: {filepath}")
    plt.close()

print()
# Сохраняем информацию о проекте
info_file = os.path.join(output_dir, 'info.json')
with open(info_file, 'w', encoding='utf-8') as f:
    json.dump({
        'project_name': project_name,
        'created': datetime.now().isoformat(),
        'total_paths': len(paths),
        'paths': [' → '.join(path) for path in paths],
        'source_json': json_file
    }, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 50)
print(f"Всего создано кадров: {len(paths)}")
print(f"Папка: {output_dir}")
print("Кадры сохранены как path_01.png, path_02.png, и т.д.")
print("=" * 50)
print()
print(f"📂 Откройте viewer2.html и выберите папку: {project_name}")
