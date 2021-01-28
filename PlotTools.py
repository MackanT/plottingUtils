from tkinter import *
import numpy as np

class Grid:

    def __init__(self, direction, canvas, steps=None, style='lin', line_visibility=True):
        """ steps = number of grid- lines/numbers
            line_visibility = if gridlines active """

        self.canvas = canvas
        self.direction = direction
        self.style = style
        self.line_visibility = line_visibility
        if steps == None:
            if style == 'lin': self.number_of_steps = 10
            elif style == 'log': self.number_of_steps = 3

        # Actual Lines
        self.pos = np.zeros(self.number_of_steps)
        self.lines = []

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
        self.pos = np.zeros(self.number_of_steps)
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
            for i in range(self.number_of_steps):
                self.pos[i] =  i * step
        else: 
            offset = self.canvas.winfo_height()
            step = int(self.canvas.winfo_height() / self.number_of_steps)
            for i in range(self.number_of_steps):
                self.pos[i] =  offset - i * step
        print('a %s' %self.pos)
        self.redraw()

    def remove(self):
        for item in self.lines: self.canvas.delete(item)
        self.lines.clear() 

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
            self.lines.append(self.canvas.create_line(pos, fill="gray"))

    def __lin_y(self):
        
        end = self.canvas.winfo_width() if self.line_visibility else 5
        for val in self.pos:
            pos = [0, val, end, val]
            self.lines.append(self.canvas.create_line(pos, fill="gray"))

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
                self.lines.append(self.canvas.create_line(pos, fill="gray"))

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
                self.lines.append(self.canvas.create_line(pos, fill="gray"))

class Axis_Numbers:

    def __init__(self, direction, canvas, position):
        """ direction = x/y, canvas = Plot.canvas """

        self.canvas = canvas
        self.direction = direction
        self.axis_values = []
        self.drawn_items = []

        self.position = position

    def set_axis_values(self, values):
        length = len(self.axis_values)
        self.axis_values = values
        self.redraw(length=length)
    def get_axis_values(self):
        return self.axis_values
    def get_lower_axis(self):
        return self.axis_values[0]
    def get_upper_axis(self):
        return self.axis_values[-1]

    def set_position(self, position):
        self.position = position

    def update_numbers(self, plot_width, canvas_boundary, font_size):
        self.plot_width = plot_width
        self.canvas_boundary = canvas_boundary
        self.font_size = font_size

    def draw(self):

        if self.direction == 'x':
            step_size = self.plot_width/len(self.axis_values)
            for i in range(len(self.axis_values)-1):
                pos = [self.position[i], 
                       self.canvas.winfo_height() - 3*self.font_size]
                tex = '{:.2f}'.format(self.axis_values[i])
                self.drawn_items.append(self.canvas.create_text(pos, 
                                            anchor = N, 
                                            text = tex))

    def redraw(self, length=None):
        
        if length != len(self.axis_values):
            for item in self.drawn_items: self.canvas.delete(item)
            self.draw()
            return

        for i in range(len(self.axis_values)):
            self.canvas.itemconfig(self.axis_values[i], text=values[i])
            
            