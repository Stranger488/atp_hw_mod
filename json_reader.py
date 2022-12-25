import json
import sys

BASE_DIR = sys.path[0]


def read_input(file, scale):
    output = json.load(file)
    info = output[0]
    start_point = (output[1]['x'] * scale, (100 - output[1]['y']) * scale)
    end_point = (output[2]['x'] * scale, (100 - output[2]['y']) * scale)

    # Массив, хранящий координаты вершин полигонов
    obstacle_points = []

    for inf_dict in output:
        if inf_dict['type'] == 'polygon':
            arr = []
            [arr.append((point['x'] * scale, (100 - point['y']) * scale)) for point in inf_dict['points']]
            obstacle_points.append(arr)

    return obstacle_points, info, start_point, end_point
