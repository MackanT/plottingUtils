from tkinter import *
import numpy as np

class Grid:

    def __init__(self, direction, canvas, color=None, steps=None, style='lin', line_visibility=True):
        """ steps = number of grid- lines/numbers
            line_visibility = if gridlines active """

        self.canvas = canvas
        self.direction = direction
        self.style = style
        self.line_visibility = line_visibility
        if steps == None:
            if style == 'lin': self.number_of_steps = 10
            elif style == 'log': self.number_of_steps = 3
        else: self.number_of_steps = steps
        self.col = color

        # Actual Lines
        self.pos = np.zeros(self.number_of_steps + 1)
        self.drawn_grid = []

        self.update_pos()

    def set_style(self, style):
        self.style = style
        self.redraw()
    def get_style(self):
        return self.style

    def invert_line_visibility(self):
        self.line_visibility = not(self.line_visibility)
        self.redraw() 
    def set_line_visibility(self, state):
        self.line_visibility = state
        self.redraw()
    def get_line_visibility(self):
        return self.line_visibility

    def set_number_of_steps(self, steps):
        self.number_of_steps = int(steps)
        self.pos = np.zeros(self.number_of_steps + 1)
        self.update_pos()
    def get_number_of_steps(self):
        return self.number_of_steps

    def get_type(self):
        return self.style

    def get_pos(self):
        return self.pos
    def update_pos(self):

        if self.direction == 'x':
            step = int(self.canvas.winfo_width() / self.number_of_steps)
            for i in range(self.number_of_steps + 1):
                self.pos[i] =  i * step
        else: 
            offset = self.canvas.winfo_height()
            step = int(self.canvas.winfo_height() / self.number_of_steps)
            for i in range(self.number_of_steps + 1):
                self.pos[i] =  offset - i * step
        self.redraw()

    def remove(self):
        for item in self.drawn_grid: self.canvas.delete(item)
        self.drawn_grid.clear() 

    def redraw(self):
        
        self.remove()

        if self.style == 'lin':
            if self.direction == 'x': self.__lin_x()
            else: self.__lin_y()
        elif self.style == 'log':
            if self.direction == 'x': self.__log_x()
            else: self.__log_y()
        
    def __lin_x(self):
        
        end = 0 if self.line_visibility else self.canvas.winfo_height() - 5
        for val in self.pos:
            pos = [val, self.canvas.winfo_height(), val, end]
            self.drawn_grid.append(self.canvas.create_line(pos, fill="gray"))

    def __lin_y(self):
        
        end = self.canvas.winfo_width() if self.line_visibility else 5
        for val in self.pos:
            pos = [0, val, end, val]
            self.drawn_grid.append(self.canvas.create_line(pos, fill="gray"))

    def __log_x(self):

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        k = (10**self.number_of_steps - 1) / self.number_of_steps
        scale_factor = (10**self.number_of_steps - 1)

        end = 0 if self.line_visibility else height - 5

        for i in range(len(self.pos)):
            for j in range(9):
                pixel = (1 + k * (i + np.log10(1 + j)))/scale_factor * width
                pos = [pixel, height, pixel, end]
                self.drawn_grid.append(self.canvas.create_line(pos, fill="gray"))

    def __log_y(self):

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        k = (10**self.number_of_steps - 1) / self.number_of_steps
        scale_factor = (10**self.number_of_steps - 1)

        end = width if self.line_visibility else 5

        for i in range(len(self.pos)):
            for j in range(9):
                pixel = height - (1 + k * (i + np.log10(1 + j)))/scale_factor * height
                pos = [0, pixel, end, pixel]
                self.drawn_grid.append(self.canvas.create_line(pos, fill="gray"))

class Axis_Numbers:

    def __init__(self, direction, canvas, pos, color):
        """ direction = x/y, canvas = Plot.canvas """

        self.canvas = canvas
        self.direction = direction
        self.axis_values = []
        self.drawn_numbers = []
        self.col = color
        self.lower = 0
        self.upper = 0

        self.pos = pos

    def set_axis_values(self, values):
        self.axis_values = values
        self.update()
    def get_axis_values(self):
        return self.axis_values
    def set_lower_axis(self, lower):
        self.lower = float(lower)
    def get_lower_axis(self):
        return self.lower
    def set_upper_axis(self, upper):
        self.upper = float(upper)
    def get_upper_axis(self):
        return self.upper

    def set_pos(self, pos, update=False):
        self.pos = pos
        if update == True: self.redraw()

    def update_numbers(self, plot_width, canvas_boundary, font_size):
        self.plot_width = plot_width
        self.canvas_boundary = canvas_boundary
        self.font_size = font_size
        self.redraw()

    def update(self):
        
        if len(self.drawn_numbers) != len(self.axis_values):
            self.redraw()
            return
        
        for i in range(len(self.axis_values)):
            self.canvas.itemconfig(self.drawn_numbers[i], text = self.axis_values[i])

    def remove(self):
        for item in self.drawn_numbers: self.canvas.delete(item)
        self.drawn_numbers.clear()

    def redraw(self):

        self.remove()

        if self.direction == 'x':
            for i in range(len(self.axis_values)):
                pos = [self.pos[i] + self.canvas_boundary, 
                       self.canvas.winfo_height() - self.canvas_boundary + self.font_size]
                self.drawn_numbers.append(self.canvas.create_text(pos, anchor = N, 
                                        text = self.axis_values[i], fill=self.col))
        else:
            for i in range(len(self.axis_values)):
                pos = [self.canvas_boundary - self.font_size/2, 
                       self.pos[i] + self.canvas_boundary]
                self.drawn_numbers.append(self.canvas.create_text(pos, anchor = E, 
                                        text = self.axis_values[i], fill=self.col))
            