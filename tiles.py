import math
import sys

import numpy as np
import pyglet
from numpy.random import choice, randint, rand, randn

colors = {
    'white': (255, 255, 255),
    'ash': (239, 239, 239),
    'lemon': (255, 255, 223),
    'scarlet': (255, 191, 191),
    'ruby': (239, 175, 175),
    'orange': (255, 223, 191),
    'stone': (127, 127, 127),
    'black': (0, 0, 0),
    'lime': (223, 255, 191),
    'moss': (207, 239, 175),
    'olive': (239, 255, 207),
    'lilac': (255, 191, 255),
    'mauve': (239, 175, 239),
    'peach': (255, 207, 239)
}

shapes = [
    'Arc'
]


class Game:
    def __init__(self, num=6, grid_width=720, margin=20, hard_mode=False):
        self.hard_mode = hard_mode
        self.num = num
        self.shape_per_cell = 4
        self.grid_width = (grid_width // self.num) * self.num
        self.margin = margin
        self.window = pyglet.window.Window(
            self.grid_width + self.margin * 2,
            self.grid_width + self.margin * 2 + 100)
        self.on_draw = self.window.event(self.on_draw)
        self.on_mouse_press = self.window.event(self.on_mouse_press)

        self.cell_width = self.grid_width // self.num

        self.canvas = pyglet.shapes.Rectangle(
            x=0,
            y=0,
            width=self.window.width,
            height=self.window.height,
            color=colors['white']
        )
        self.grid_batch = pyglet.graphics.Batch()
        self.shape_batch = pyglet.graphics.Batch()

        self.grid_background_group = pyglet.graphics.Group(order=0)
        self.grid_foreground_group = pyglet.graphics.Group(order=2)

        self.gridlines = []
        self.create_gridlines()

        self.cells = [[{} for _ in range(num)] for _ in range(num)]
        self.create_bases()

        self.highlighted_cells = [[{} for _ in range(num)] for _ in range(num)]
        self.create_highlighted_cells()

        self.shape_num = self.num * 4 if self.num % 2 == 0 else self.num * 2
        self.shapes = []
        self.shapes_params = []
        self.total_shape_count = 0

        self.create_shapes_params()

        self.distribute_shapes()

        self.max_streak = 0
        self.current_streak = 0
        self.current_streak_label = None
        self.max_streak_label = None
        self.create_labels()

        self.active = None
        self.go_anywhere = True

        self.square_rotation_is_positive = True

        pyglet.app.run()

    def create_labels(self):
        self.current_streak_label = pyglet.text.Label(
            text='Current: 0',
            x=self.margin,
            y=self.grid_width + self.margin + 20,
            anchor_x='left',
            anchor_y='bottom',
            font_size=24,
            color=(0, 0, 0)
        )

        self.max_streak_label = pyglet.text.Label(
            text='Max: 0',
            x=self.grid_width + self.margin,
            y=self.grid_width + self.margin + 20,
            anchor_x='right',
            anchor_y='bottom',
            font_size=24,
            color=(0, 0, 0)
        )

    def create_gridlines(self):
        for i in range(0, self.num + 1):
            width = 2
            color = colors['stone']
            group = self.grid_foreground_group

            vertical_line = pyglet.shapes.Rectangle(
                x=i * self.cell_width + self.margin,
                y=self.grid_width // 2 + self.margin,
                width=width,
                height=self.grid_width + width - 2,
                color=color,
                batch=self.grid_batch,
                group=group
            )
            vertical_line.anchor_x = width // 2
            vertical_line.anchor_y = (self.grid_width + width - 2) // 2

            horizontal_line = pyglet.shapes.Rectangle(
                x=self.grid_width // 2 + self.margin,
                y=i * self.cell_width + self.margin,
                width=self.grid_width + width - 2,
                height=width,
                color=color,
                batch=self.grid_batch,
                group=group
            )
            horizontal_line.anchor_x = (self.grid_width + width - 2) // 2
            horizontal_line.anchor_y = width // 2

            self.gridlines.append(vertical_line)
            self.gridlines.append(horizontal_line)

    def create_bases(self):
        if self.num % 2 == 0:
            choices = [1, 2, 4]
            p = [0.2, 0.4, 0.4]
        else:
            choices = [1, 2]
            p = [0.4, 0.6]
        base_color_num = choice(choices, 1, p=p)[0]
        print(base_color_num)
        base_colors = []
        for i in range(base_color_num):
            r = randint(192, 255)
            g = randint(192, 255)
            b = randint(192, 255)
            base_colors.append((r, g, b))

        is_four = choice([True, False], 1)[0]

        for i in range(self.num):
            for j in range(self.num):
                x = self.cell_width * (j + 0.5) + self.margin
                y = self.cell_width * (i + 0.5) + self.margin

                index = (i + j) if is_four else (i % 2 + j % 2)
                color = base_colors[index % base_color_num]
                square = pyglet.shapes.Rectangle(
                    x=x,
                    y=y,
                    width=self.cell_width,
                    height=self.cell_width,
                    color=color,
                    batch=self.grid_batch,
                    group=self.grid_background_group
                )
                square.anchor_x = self.cell_width // 2
                square.anchor_y = self.cell_width // 2

                self.cells[i][j]['square'] = square

    def create_highlighted_cells(self):
        for i in range(self.num):
            for j in range(self.num):
                edges = []
                x = self.cell_width * (j + 0.5) + self.margin
                y = self.cell_width * (i + 0.5) + self.margin

                top_edge = pyglet.shapes.Rectangle(
                    x=x,
                    y=y + self.cell_width // 2 - self.cell_width // 16,
                    width=self.cell_width,
                    height=self.cell_width // 8,
                    color=(127, 255, 0),
                    batch=self.grid_batch,
                    group=self.grid_foreground_group
                )
                top_edge.anchor_x = self.cell_width // 2
                top_edge.anchor_y = self.cell_width // 16
                top_edge.visible = False
                edges.append(top_edge)

                bottom_edge = pyglet.shapes.Rectangle(
                    x=x,
                    y=y - self.cell_width // 2 + self.cell_width // 16,
                    width=self.cell_width,
                    height=self.cell_width // 8,
                    color=(127, 255, 0),
                    batch=self.grid_batch,
                    group=self.grid_foreground_group
                )
                bottom_edge.anchor_x = self.cell_width // 2
                bottom_edge.anchor_y = self.cell_width // 16
                bottom_edge.visible = False
                edges.append(bottom_edge)

                right_edge = pyglet.shapes.Rectangle(
                    x=x + self.cell_width // 2 - self.cell_width // 16,
                    y=y,
                    width=self.cell_width // 8,
                    height=self.cell_width,
                    color=(127, 255, 0),
                    batch=self.grid_batch,
                    group=self.grid_foreground_group
                )
                right_edge.anchor_x = self.cell_width // 16
                right_edge.anchor_y = self.cell_width // 2
                right_edge.visible = False
                edges.append(right_edge)

                left_edge = pyglet.shapes.Rectangle(
                    x=x - self.cell_width // 2 + self.cell_width // 16,
                    y=y,
                    width=self.cell_width // 8,
                    height=self.cell_width,
                    color=(127, 255, 0),
                    batch=self.grid_batch,
                    group=self.grid_foreground_group
                )
                left_edge.anchor_x = self.cell_width // 16
                left_edge.anchor_y = self.cell_width // 2
                left_edge.visible = False
                edges.append(left_edge)

                self.highlighted_cells[i][j] = {'edges': edges, 'visible': False}

    def on_draw(self):
        self.window.clear()
        self.canvas.draw()
        self.current_streak_label.draw()
        self.max_streak_label.draw()
        self.grid_batch.draw()
        self.shape_batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.total_shape_count == 0:
            return

        i = (y - self.margin) // self.cell_width
        j = (x - self.margin) // self.cell_width

        if i not in range(self.num) or j not in range(self.num):
            return
        if self.active == (j, i):
            return

        if self.go_anywhere:
            if self.active is not None:
                self.deactivate(self.active[1], self.active[0])
            self.activate(i, j)
            self.go_anywhere = False
        else:
            last_j, last_i = self.active
            if not self.match(last_i, last_j, i, j):
                self.go_anywhere = True
                self.current_streak = 0
                self.current_streak_label.text = f'Current: {0}'
                self.deactivate(last_i, last_j)
            else:
                this_indices = {1 for shape in self.cells[i][j]['shapes'] if shape['visible']}
                if len(this_indices) == 0:
                    self.go_anywhere = True
                self.current_streak += 1
                self.current_streak_label.text = f'Current: {self.current_streak}'
                self.max_streak = max(self.max_streak, self.current_streak)
                self.max_streak_label.text = f'Max: {self.max_streak}'
                self.deactivate(last_i, last_j)
                self.activate(i, j)

                if self.total_shape_count == 0:
                    self.deactivate(i, j)
                    pyglet.clock.schedule_interval_for_duration(self.win, 0.04, 1.2)

    def create_shapes_params(self):
        red_limit = (1, 256)  # np.sort(randint(1, 256, size=2))
        green_imit = np.sort(randint(0, 256, size=2))
        if green_imit[1] == green_imit[0]:
            green_imit[1] += 1
        blue_limit = (1, 256)  # np.sort(randint(0, 256, size=2))

        thickness_upper_limit = randint(4, max(50 // self.num, 5))
        segments_upper_limit = int((randn() * 6) ** 2 + 2)

        for i in range(self.shape_num):
            shape_string = choice(shapes, 1)[0]
            if shape_string == 'Arc':

                thickness = randint(2, thickness_upper_limit)
                radius = rand(1)[0] * (self.cell_width / 8 - thickness) + (self.cell_width / 8)
                position_delta = rand(2) * (self.cell_width / 4)
                segments = randint(1, segments_upper_limit)
                arms = int((abs(randn()) * 3) + 3)
                angle = rand(1)[0] * math.pi * 1.5 + (math.pi / 4)
                start_angle = rand(1)[0] * math.pi * 2
                anchor_angle = rand(1)[0] * math.pi * 2
                r = randint(*red_limit)
                g = randint(*green_imit)
                b = randint(*blue_limit)
                color = (r, g, b)

                shape_params = dict(
                    index=i,
                    shape_string=shape_string,
                    segments=segments,
                    radius=float(radius),
                    angle=float(angle),
                    start_angle=float(start_angle),
                    anchor_angle=float(anchor_angle),
                    dx=float(position_delta[0]),
                    dy=float(position_delta[1]),
                    thickness=thickness,
                    color=color,
                    arms=arms
                )
            else:
                shape_params = None
            self.shapes_params.append(shape_params)

    def distribute_shapes(self):
        # print(self.shapes_params)

        places = [int(i) for i in np.arange(self.num ** 2)]
        occupied_places = [0] * self.num ** 2
        level = 0
        for i in range(self.num):
            for j in range(self.num):
                self.cells[i][j]['shapes'] = []
        for k, shape_params in enumerate(self.shapes_params):
            used_places = []
            for n in range(self.num ** 2 * self.shape_per_cell // self.shape_num):

                vacant_places = [p for p in places if occupied_places[p] == level and p not in used_places]

                place = int(choice(vacant_places))

                occupied_places[place] += 1
                if sum(occupied_places) == self.num ** 2 * (level + 1):
                    level += 1
                used_places.append(place)

                self.total_shape_count += 1

                i = place // self.num
                j = place % self.num
                x = j * self.cell_width + self.margin + self.cell_width // 2
                y = i * self.cell_width + self.margin + self.cell_width // 2

                shape_group = []
                for m in range(shape_params['arms']):

                    if shape_params['shape_string'] == 'Arc':
                        shape = pyglet.shapes.Arc(
                            x=x,
                            y=y,
                            segments=shape_params['segments'],
                            radius=shape_params['radius'],
                            angle=shape_params['angle'],
                            start_angle=shape_params['start_angle'],
                            thickness=shape_params['thickness'],
                            color=shape_params['color'],
                            batch=self.shape_batch
                        )
                        shape.anchor_x = shape_params['dx']
                        shape.anchor_y = shape_params['dy']

                        shape.rotation = ((360 / shape_params['arms']) * m + shape_params['anchor_angle']) % 360
                        # part.anchor_x = 35  # -float(position_delta[0])
                        # part.anchor_y = 20  # -float(position_delta[1])
                        # print(f'j: {j}, i: {i}, x: {shape.x}, y: {shape.y}, a_x: {round(shape.anchor_x)}, '
                        #       f'a_y: {round(shape.anchor_y)}, r: {shape.rotation}')
                        self.shapes.append(shape)
                        shape_group.append(shape)
                self.cells[i][j]['shapes'].append(
                    {
                        'index': shape_params['index'],
                        'shape_group': shape_group,
                        'visible': True
                    }
                )

    def match(self, last_i, last_j, i, j):
        last_indices = {shape['index'] for shape in self.cells[last_i][last_j]['shapes'] if shape['visible']}
        this_indices = {shape['index'] for shape in self.cells[i][j]['shapes'] if shape['visible']}
        matching_indices = last_indices & this_indices
        if len(matching_indices) == 0:
            return False
        for shape in self.cells[last_i][last_j]['shapes']:
            if shape['index'] in matching_indices:
                shape['visible'] = False
                self.total_shape_count -= 1
                for part in shape['shape_group']:
                    if self.hard_mode:
                        pyglet.clock.schedule_interval(
                            self.remove_shape,
                            0.04,
                            shape=part,
                            i=last_i,
                            j=last_j
                        )
                    else:
                        pyglet.clock.schedule_interval_for_duration(
                            self.remove_shape,
                            0.04,
                            0.4,
                            shape=part,
                            i=last_i,
                            j=last_j
                        )

        for shape in self.cells[i][j]['shapes']:
            if shape['index'] in matching_indices:
                shape['visible'] = False
                self.total_shape_count -= 1
                for part in shape['shape_group']:
                    if self.hard_mode:
                        pyglet.clock.schedule_interval(
                            self.remove_shape,
                            0.04,
                            shape=part,
                            i=i,
                            j=j
                        )
                    else:
                        pyglet.clock.schedule_interval_for_duration(
                            self.remove_shape,
                            0.04,
                            0.4,
                            shape=part,
                            i=i,
                            j=j
                        )

        return True

    def remove_shape(self, interval, shape, i, j):
        if (i + j) % 2 == 0:
            shape.rotation += 15
        else:
            shape.rotation -= 15
        if not self.hard_mode:
            shape.opacity = max(0, int(shape.opacity // 1.5 - 1))
            if shape.opacity <= 10:
                shape.visible = False

    def activate(self, i, j):
        self.active = (j, i)
        self.highlighted_cells[i][j]['visible'] = True
        for edge in self.highlighted_cells[i][j]['edges']:
            edge.visible = True

    def deactivate(self, i, j):
        self.active = None
        self.highlighted_cells[i][j]['visible'] = False
        for edge in self.highlighted_cells[i][j]['edges']:
            edge.visible = False

    def win(self, interval):
        d = int(self.cell_width // 8)
        for gridline in self.gridlines:
            gridline.opacity = max(0, int(gridline.opacity // 1.15 - 1))
        for i in range(self.num):
            for j in range(self.num):
                if self.square_rotation_is_positive:
                    self.cells[i][j]['square'].width -= d
                    self.cells[i][j]['square'].anchor_x -= d // 2
                else:
                    self.cells[i][j]['square'].width += d
                    self.cells[i][j]['square'].anchor_x += d // 2
                if self.cells[i][j]['square'].width <= 0:
                    self.square_rotation_is_positive = not self.square_rotation_is_positive
                self.cells[i][j]['square'].opacity = max(0, int(self.cells[i][j]['square'].opacity // 1.15 - 1))


def main(args):
    kwargs = {}
    if len(args) > 0:
        kwargs['num'] = int(args[0])
    if len(args) > 1:
        kwargs['grid_width'] = int(args[1])
    if len(args) > 2:
        kwargs['margin'] = int(args[2])
    if len(args) > 3:
        kwargs['hard_mode'] = bool(int(args[3]))
    Game(**kwargs)


if __name__ == "__main__":
    main(sys.argv[1:])
