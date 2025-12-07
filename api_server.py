#!/usr/bin/env python3
"""
API сервер для автоматической генерации анимаций
Запуск: ./venv/bin/python api_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для браузера

@app.route('/api/generate', methods=['POST'])
def generate_animation():
    try:
        data = request.json
        
        # Получаем данные
        project_name = data.get('projectName', f'web_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        graph_data = data.get('graphData')
        start_node = data.get('startNode', 'A')
        end_node = data.get('endNode', 'H')
        
        if not graph_data:
            return jsonify({'success': False, 'error': 'Нет данных графа'}), 400
        
        # Сохраняем JSON граф
        json_dir = 'json'
        os.makedirs(json_dir, exist_ok=True)
        json_file = os.path.join(json_dir, f'{project_name}.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        
        # Создаём временный скрипт для генерации с параметрами
        output_dir = f'output/{project_name}'
        
        # Импортируем и запускаем генератор напрямую
        import networkx as nx
        import matplotlib
        matplotlib.use('Agg')  # Без GUI
        import matplotlib.pyplot as plt
        
        # Создаём граф
        G = nx.DiGraph()
        edges = [(edge['from'], edge['to']) for edge in graph_data['edges']]
        G.add_edges_from(edges)
        
        # Позиции
        pos = {}
        for node in graph_data['nodes']:
            label = node['label']
            x = node['x']
            y = -node['y']
            pos[label] = (x, y)
        
        # Находим пути
        if start_node not in G.nodes() or end_node not in G.nodes():
            return jsonify({
                'success': False, 
                'error': f'Вершины {start_node} или {end_node} не найдены'
            }), 400
        
        paths = list(nx.all_simple_paths(G, source=start_node, target=end_node))
        
        if len(paths) == 0:
            return jsonify({
                'success': False,
                'error': f'Путей из {start_node} в {end_node} не найдено'
            }), 400
        
        # Создаём выходную директорию
        os.makedirs(output_dir, exist_ok=True)
        
        # Генерируем кадры
        frame_number = 0
        all_frames = []
        
        for path_idx, path in enumerate(paths, 1):
            for step in range(1, len(path) + 1):
                frame_number += 1
                
                current_path = path[:step]
                current_edges = list(zip(current_path[:-1], current_path[1:])) if len(current_path) > 1 else []
                current_edges_set = set(current_edges)
                
                plt.figure(figsize=(14, 8))
                
                other_edges = [edge for edge in G.edges() if edge not in current_edges_set]
                other_nodes = [node for node in G.nodes() if node not in current_path]
                
                # Рёбра (сначала)
                if other_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=other_edges,
                                          edge_color='gray', width=2.5, alpha=0.4,
                                          arrows=True, arrowsize=20, arrowstyle='->')
                
                if current_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=current_edges,
                                          edge_color='#FF1744', width=5,
                                          arrows=True, arrowsize=30, arrowstyle='->',
                                          node_size=1500)
                
                # Вершины (поверх)
                if other_nodes:
                    nx.draw_networkx_nodes(G, pos, nodelist=other_nodes,
                                          node_color='lightgray', node_size=1500, alpha=0.5)
                
                if len(current_path) > 1:
                    intermediate = current_path[:-1]
                    nx.draw_networkx_nodes(G, pos, nodelist=intermediate,
                                          node_color='orange', node_size=1500,
                                          edgecolors='#ff8c00', linewidths=3)
                
                current_node = current_path[-1]
                nx.draw_networkx_nodes(G, pos, nodelist=[current_node],
                                      node_color='#ff4500', node_size=1800,
                                      edgecolors='#ff0000', linewidths=4)
                
                nx.draw_networkx_labels(G, pos, font_size=16, font_weight='bold', font_color='#333')
                
                title = f'Путь {path_idx}/{len(paths)} | Шаг {step}/{len(path)}: {" → ".join(current_path)}'
                plt.title(title, fontsize=18, fontweight='bold', pad=20)
                plt.axis('off')
                plt.tight_layout()
                
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
        
        # Сохраняем info.json
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
        
        return jsonify({
            'success': True,
            'projectName': project_name,
            'totalFrames': frame_number,
            'totalPaths': len(paths),
            'outputDir': output_dir
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """Список всех проектов"""
    try:
        output_dir = 'output'
        if not os.path.exists(output_dir):
            return jsonify({'projects': []})
        
        projects = []
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path):
                info_file = os.path.join(item_path, 'info.json')
                if os.path.exists(info_file):
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        projects.append({
                            'name': item,
                            'created': info.get('created'),
                            'totalFrames': info.get('total_frames', 0),
                            'totalPaths': info.get('total_paths', 0)
                        })
        
        # Сортируем по дате создания
        projects.sort(key=lambda x: x.get('created', ''), reverse=True)
        
        return jsonify({'projects': projects})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Graph Animation API Server")
    print("=" * 50)
    print("Сервер запущен на http://localhost:5000")
    print("API endpoints:")
    print("  POST /api/generate - Генерация анимации")
    print("  GET  /api/projects - Список проектов")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
