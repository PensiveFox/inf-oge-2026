import json
import networkx as nx
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Имя проекта
project_name = input("Введите имя проекта (или Enter для автоматического): ").strip()
if not project_name:
    project_name = f"animated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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
    y = -node['y']  # Только инвертируем Y
    pos[label] = (x, y)

print("=" * 50)
print("Граф загружен из JSON")
print("=" * 50)
print(f"Вершины: {list(G.nodes())}")
print(f"Рёбра: {list(G.edges())}")
print()

# Находим все простые пути из A в H
start_node = input("Начальная вершина (по умолчанию A): ").strip() or 'A'
end_node = input("Конечная вершина (по умолчанию H): ").strip() or 'H'

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

# Создаём анимированные кадры для каждого пути
frame_number = 0
all_frames = []

for path_idx, path in enumerate(paths, 1):
    print(f"🎬 Генерация анимации для пути {path_idx}: {' → '.join(path)}")
    
    # Создаём кадры с постепенным наращиванием пути
    for step in range(1, len(path) + 1):
        frame_number += 1
        
        # Текущая часть пути
        current_path = path[:step]
        current_edges = list(zip(current_path[:-1], current_path[1:])) if len(current_path) > 1 else []
        current_edges_set = set(current_edges)
        
        plt.figure(figsize=(14, 8))
        
        # Рёбра не в текущем пути (бледные)
        other_edges = [edge for edge in G.edges() if edge not in current_edges_set]
        
        # Узлы не в текущем пути
        other_nodes = [node for node in G.nodes() if node not in current_path]
        
        # СНАЧАЛА РИСУЕМ ВСЕ РЁБРА (чтобы они были под вершинами)
        
        # Рисуем бледные рёбра (не в пути)
        if other_edges:
            nx.draw_networkx_edges(G, pos, edgelist=other_edges, 
                                  edge_color='gray', width=2.5, alpha=0.4,
                                  arrows=True, arrowsize=20, arrowstyle='->')
        
        # Рисуем рёбра текущего пути (ЯРКИЕ)
        if current_edges:
            nx.draw_networkx_edges(G, pos, edgelist=current_edges, 
                                  edge_color='#FF1744', width=5,
                                  arrows=True, arrowsize=30, arrowstyle='->',
                                  node_size=1500)  # Указываем размер узлов для правильного отступа
        
        # ПОТОМ РИСУЕМ ВСЕ ВЕРШИНЫ (поверх стрелок)
        
        # Рисуем узлы не в пути (серые)
        if other_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=other_nodes, 
                                  node_color='lightgray', node_size=1500, alpha=0.5)
        
        # Рисуем узлы в текущем пути
        if len(current_path) > 1:
            # Промежуточные узлы (оранжевые)
            intermediate = current_path[:-1]
            nx.draw_networkx_nodes(G, pos, nodelist=intermediate, 
                                  node_color='orange', node_size=1500, 
                                  edgecolors='#ff8c00', linewidths=3)
        
        # Текущая (последняя) вершина - ярко подсвечена
        current_node = current_path[-1]
        nx.draw_networkx_nodes(G, pos, nodelist=[current_node], 
                              node_color='#ff4500', node_size=1800, 
                              edgecolors='#ff0000', linewidths=4)
        
        # Подписи вершин
        nx.draw_networkx_labels(G, pos, font_size=16, font_weight='bold', font_color='#333')
        
        # Заголовок с информацией о шаге
        title = f'Путь {path_idx}/{len(paths)} | Шаг {step}/{len(path)}: {" → ".join(current_path)}'
        plt.title(title, fontsize=18, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # Сохраняем кадр
        filename = f'frame_{frame_number:04d}.png'
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        all_frames.append({
            'number': frame_number,
            'path_index': path_idx,
            'step': step,
            'current_path': ' → '.join(current_path),
            'filename': filename
        })
    
    print(f"  ✅ Создано {len(path)} кадров для пути {path_idx}")

print()
print("=" * 50)

# Сохраняем информацию о проекте
info_file = os.path.join(output_dir, 'info.json')
with open(info_file, 'w', encoding='utf-8') as f:
    json.dump({
        'project_name': project_name,
        'created': datetime.now().isoformat(),
        'total_paths': len(paths),
        'total_frames': frame_number,
        'animation_type': 'progressive',
        'paths': [' → '.join(path) for path in paths],
        'frames': all_frames,
        'source_json': json_file,
        'start_node': start_node,
        'end_node': end_node
    }, f, ensure_ascii=False, indent=2)

print(f"Всего создано кадров: {frame_number}")
print(f"Путей: {len(paths)}")
print(f"Папка: {output_dir}")
print("=" * 50)
print()
print(f"📂 Откройте viewer3.html и выберите проект: {project_name}")
print()
print("💡 Кадры создаются с анимацией построения пути:")
print("   - Каждый шаг пути = отдельный кадр")
print("   - Текущая вершина подсвечена ярко-красным")
print("   - Пройденные вершины - оранжевые")
