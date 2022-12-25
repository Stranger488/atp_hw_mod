import argparse
from pathlib import Path
from tkinter import *
from tkinter import filedialog

from PIL import ImageTk, ImageDraw
import mapgen
import quadtree
import astar
import graph
import json_reader
from mapgen import IMPASSABLE

# square map height and width. power of 2. e.g 256, 512, 1024
MAPSIZE = 512


class MainObject:
    def run(self, args):
        self.input_file = args.in_json
        self.mapimage = None
        self.quadtree = None
        self.startpoint = None
        self.endpoint = None
        self.drag_startp = False

        self._setupgui()

        self.onReset()

        self.root.mainloop()

    def _setupgui(self):
        self.root = Tk()
        self.root.title('QuadTree A*')

        self.canvas = Canvas(self.root, bg='gray', width=MAPSIZE, height=MAPSIZE)
        self.canvas.pack(side=LEFT)

        self.image_item = self.canvas.create_image((0, 0), anchor=NW)

        rightframe = Frame(self.root)
        rightframe.pack(side=LEFT, fill=Y)

        openfile = Frame(rightframe, relief=SUNKEN, borderwidth=2)
        openfile.pack(fill=X, padx=5, pady=5)

        label = Label(openfile, text='Input', font=('Helvetica', 13))
        label.pack()

        self.openlabelvar = StringVar()
        label = Label(openfile, textvariable=self.openlabelvar)
        label.pack()

        quadtreebtn = Button(openfile, text='Open file', command=self.onButtonOpenFilePress)
        quadtreebtn.pack(pady=2)

        qtframe = Frame(rightframe, relief=SUNKEN, borderwidth=2)
        qtframe.pack(fill=X, padx=5, pady=5)

        label = Label(qtframe, text='QuadTree', font=('Helvetica', 13))
        label.pack()

        frame1 = Frame(qtframe)
        frame1.pack(fill=X, padx=4)

        label = Label(frame1, text='Depth Limit')
        label.pack(side=LEFT, pady=4)

        var = StringVar(self.root)
        var.set('50')
        self.limitspin = Spinbox(frame1, from_=2, to=50, textvariable=var)
        self.limitspin.pack(expand=True)

        self.qtlabelvar = StringVar()
        label = Label(qtframe, fg='#FF8080', textvariable=self.qtlabelvar)
        label.pack()

        quadtreebtn = Button(qtframe, text='Generate QuadTree', command=self.onButtonQuadTreePress)
        quadtreebtn.pack(pady=2)

        astarframe = Frame(rightframe, relief=SUNKEN, borderwidth=2)
        astarframe.pack(fill=X, padx=5, pady=5)

        label = Label(astarframe, text='Path', font=('Helvetica', 13))
        label.pack()

        self.pathlabelvar = StringVar()
        label = Label(astarframe, fg='#0000FF', textvariable=self.pathlabelvar)
        label.pack()

        self.astarlabelvar = StringVar()
        label = Label(astarframe, fg='#8080FF', textvariable=self.astarlabelvar)
        label.pack()

        resetbutton = Button(astarframe, text='Reset', command=self.onReset)
        resetbutton.pack(pady=2)

        label = Label(rightframe, text='Instructions', font=('Helvetica', 13))
        label.pack()
        label = Label(rightframe, justify=LEFT, text=
        'Read map from file.\n'
        'Black regions are impassable.\n'
        'Generate QuadTree on map.\n'
        'Set start position by dragging aqua circle.\n'
        'Click anywhere on map to find a path.')
        label.pack(padx=14)

        self.canvas.bind('<ButtonPress-1>', self.onMouseButton1Press)
        self.canvas.bind('<ButtonRelease-1>', self.onMouseButton1Release)
        self.canvas.bind('<B1-Motion>', self.onMouseMove)

    def onMouseButton1Press(self, event):
        if not self.quadtree:
            return

        if self.startpoint in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
            self.drag_startp = True
            return

        self.canvas.coords(self.endpoint, event.x - 4, event.y - 4, event.x + 4, event.y + 4)

        startx, starty, _, _ = self.canvas.coords(self.startpoint)
        start = self.quadtree.get(startx + 4, starty + 4)
        goal = self.quadtree.get(event.x, event.y)

        adjacent = graph.make_adjacent_function(self.quadtree)
        path, distances, considered = astar.astar(adjacent, graph.euclidian, graph.euclidian, start, goal)

        im = self.qtmapimage.copy()
        draw = ImageDraw.Draw(im)

        self.astarlabelvar.set('Nodes visited: {} considered: {}'.format(len(distances), considered))
        for tile in distances:
            fill_tile(draw, tile, color=(0xC0, 0xC0, 0xFF))

        if path:
            self.pathlabelvar.set('Path Cost: {}  Nodes: {}'.format(round(distances[goal], 1), len(path)))
            for tile in path:
                fill_tile(draw, tile, color=(0, 0, 255))
        else:
            self.pathlabelvar.set('No Path found.')

        self._updateimage(im)

    def onMouseButton1Release(self, event):
        self.drag_startp = False

    def onMouseMove(self, event):
        if self.drag_startp:
            self.canvas.coords(self.startpoint, event.x - 4, event.y - 4, event.x + 4, event.y + 4)

    def readAndDrawInput(self, input_file):
        self.root.config(cursor='watch')
        self.root.update()

        self.mapimage = mapgen.generate_map(MAPSIZE)
        self._updateimage(self.mapimage)

        self.quadtree = None
        self.qtlabelvar.set('')
        self.canvas.delete(self.startpoint)
        self.canvas.delete(self.endpoint)
        self.startpoint = None
        self.endpoint = None
        self.astarlabelvar.set('')
        self.pathlabelvar.set('')
        self.root.config(cursor='')

        obst_arr, info, start, end = json_reader.read_input(input_file, MAPSIZE / 100)
        draw = ImageDraw.Draw(self.mapimage)
        draw_obstacles(draw, obst_arr, IMPASSABLE)
        self.openlabelvar.set(Path(input_file.name).name)
        self._updateimage(self.mapimage)

        self.startpoint = self.canvas.create_oval(start[0] - 4, start[1] - 4, start[0] + 4, start[1] + 4,
                                                  fill='#43c4a3', width=2)
        self.endpoint = self.canvas.create_oval(end[0] - 4, end[1] - 4, end[0] + 4, end[1] + 4,
                                                fill='#a441c8', width=2)

    def onButtonOpenFilePress(self):
        filetypes = (
            ('json files', '*.json'),
            ('all files', '*.*')
        )

        f = filedialog.askopenfile(filetypes=filetypes)
        self.readAndDrawInput(f)

    def onButtonQuadTreePress(self):
        if not self.mapimage:
            return

        depthlimit = int(self.limitspin.get())
        self.quadtree = quadtree.Tile(self.mapimage, limit=depthlimit)
        self.qtmapimage = self.mapimage.copy()
        draw = ImageDraw.Draw(self.qtmapimage)
        draw_quadtree(draw, self.quadtree, 8)
        self._updateimage(self.qtmapimage)

        self.qtlabelvar.set('Depth: {}  Nodes: {}'.format(self.quadtree.depth(), self.quadtree.count()))
        self.astarlabelvar.set('')
        self.pathlabelvar.set('')

        if not self.startpoint:
            pos = MAPSIZE // 2
            self.startpoint = self.canvas.create_oval(pos - 4, pos - 4, pos + 4, pos + 4, fill='#43c4a3', width=2)
        if not self.endpoint:
            pos = MAPSIZE // 4
            self.endpoint = self.canvas.create_oval(pos - 4, pos - 4, pos + 4, pos + 4, fill='#a441c8',
                                                    width=2)

        startx, starty, _, _ = self.canvas.coords(self.endpoint)
        e = Event()
        e.x = startx + 4
        e.y = starty + 4
        self.onMouseButton1Press(e)

    def onReset(self):
        with open(json_reader.BASE_DIR + "/" + self.input_file, 'r') as f:
            self.readAndDrawInput(f)

    def _updateimage(self, image):
        self.imagetk = ImageTk.PhotoImage(image)
        self.canvas.itemconfig(self.image_item, image=self.imagetk)


def draw_quadtree(draw, tile, maxdepth):
    if tile.level == maxdepth:
        draw_tile(draw, tile, color=(255, 110, 110))
        return

    if tile.childs:
        for child in tile.childs:
            draw_quadtree(draw, child, maxdepth)
    else:
        draw_tile(draw, tile, color=(255, 110, 110))


def draw_tile(draw, tile, color):
    draw.rectangle([tile.bb.x, tile.bb.y, tile.bb.x + tile.bb.w, tile.bb.y + tile.bb.h], outline=color)


def fill_tile(draw, tile, color):
    draw.rectangle([tile.bb.x + 1, tile.bb.y + 1, tile.bb.x + tile.bb.w - 1, tile.bb.y + tile.bb.h - 1], outline=None,
                   fill=color)


def draw_obstacles(draw, obst_arr, color):
    for obst in obst_arr:
        draw.polygon(obst, fill=color, outline=color)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--in_json', action='store', type=str,
                            help='Input file with json map')

    o = MainObject()
    o.run(arg_parser.parse_args())
