import numpy as np
from matplotlib import pyplot as plt

N = [27, 48, 108,
     192, 300, 506,
     783, 1276, 2686]
gen_512 = [0.105, 0.135, 0.195,
           0.268, 0.334, 0.399,
           0.546, 0.632, 0.93]
gen_1024 = [0.207, 0.335, 0.45,
            0.557, 0.807, 0.942,
            1.121, 1.408, 2.068]

d_512 = [0.163, 0.249, 0.342,
         0.482, 0.659, 0.741,
         0.922, 1.175, 1.711]
d_1024 = [0.345, 0.53, 0.745,
          1.085, 1.29, 1.725,
          1.931, 2.655, 3.852]

a_512 = [0.061, 0.04, 0.133,
         0.182, 0.213, 0.271,
         0.28, 0.527, 0.919]
a_1024 = [0.133, 0.078, 0.29,
          0.36, 0.483, 0.537,
          0.578, 1.119, 1.976]

def plot(x, y1, y2, title):
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 6), dpi=400)
        axes.plot(x, y1, '.-', markersize=8, linewidth=1.5, label='512x512')
        axes.plot(x, y2, '.-', markersize=8, linewidth=1.5, label='1024x1024')
        axes.grid()
        axes.legend(loc='best')
        axes.set_xlabel('Количество вершин препятствий')
        axes.set_ylabel('Время работы, сек.')
        axes.set_title(title)
        plt.show()


plot(N, gen_512, gen_1024, title='Генерация дерева квадрантов')
plot(N, d_512, d_1024, title='Поиск пути алгоритмом Дейкстры')
plot(N, a_512, a_1024, title='Поиск пути алгоритмом A*')

plot(N, np.array(gen_512) + np.array(d_512),
     np.array(gen_1024) + np.array(d_1024), title='Общее время решения, алгоритм Дейкстры')
plot(N, np.array(gen_512) + np.array(a_512),
     np.array(gen_1024) + np.array(a_1024), title='Общее время решения, алгоритм A*')