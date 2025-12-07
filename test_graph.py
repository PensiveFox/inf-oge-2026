import json
import networkx as nx
import matplotlib.pyplot as plt

# Загружаем граф из JSON файла
with open('json/graph-1.json', 'r', encoding='utf-8') as f:
    graph_data = json.load(f)

# Создаём ориентированный граф
G = nx.DiGraph()

# Добавляем рёбра из JSON
edges = [(edge['from'], edge['to']) for edge in graph_data['edges']]
G.add_edges_from(edges)

# Создаём словарь позиций - ПРЯМО из JSON без масштабирования
pos = {}
for node in graph_data['nodes']:
    label = node['label']
    x = node['x']
    y = -node['y']  # Только инвертируем Y
    pos[label] = (x, y)

print("Координаты вершин (без масштабирования):")
for label, (x, y) in pos.items():
    print(f"  {label}: ({x:.1f}, {y:.1f})")

# Рисуем граф
plt.figure(figsize=(14, 8))

# Все узлы
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=1500, edgecolors='blue', linewidths=2)

# Все рёбра
nx.draw_networkx_edges(G, pos, edge_color='gray', width=2, arrows=True, arrowsize=20, arrowstyle='->')

# Подписи вершин
nx.draw_networkx_labels(G, pos, font_size=16, font_weight='bold', font_color='black')

plt.title('Тестовый граф (координаты напрямую из JSON)', fontsize=18, fontweight='bold')
plt.axis('off')
plt.tight_layout()

# Сохраняем
plt.savefig('test_graph.png', dpi=150, bbox_inches='tight', facecolor='white')
print("\n✅ Сохранено: test_graph.png")
plt.close()
