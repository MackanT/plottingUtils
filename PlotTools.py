from tkinter import *
import numpy as np

class Lin_Grid:

    def __init__(self, direction, canvas, steps=10, line_visibility=True):
        """ steps = number of grid- lines/numbers
            line_visibility = if gridlines active """

        self.canvas = canvas
        self.canvas_dim = [0, 0]
        self.direction = direction

        self.number_of_steps = steps
        self.line_visibility = line_visibility

        # Actual Lines
        self.pos = np.zeros(self.number_of_steps)
        self.lines = []

        self.update_pos()

    def invert_line_visibility(self):
        self.line_visibility = not(self.line_visibility)
        self.redraw() 
    def set_line_visibility(self, state):
        self.line_visibility = state
        self.redraw()
    def get_line_visibility(self):
        return self.line_visibility

    def set_number_of_steps(self, steps):
        self.number_of_steps = steps
        self.redraw()
    def get_number_of_steps(self):
        return self.number_of_steps

    def __get_canvas_dim(self):
        return [self.canvas.winfo_width(), self.canvas.winfo_height()]

    def update_pos(self):

        if self.__get_canvas_dim() == self.canvas_dim: return
        self.canvas_dim = self.__get_canvas_dim()

        if self.direction == 'x':
            step = int(self.canvas.winfo_width() / self.number_of_steps)
            for i in range(self.number_of_steps):
                self.pos[i] =  i * step
        else: 
            offset = self.canvas.winfo_height()
            step = int(self.canvas.winfo_height() / self.number_of_steps)
            for i in range(self.number_of_steps):
                self.pos[i] =  offset - i * step

    def redraw(self):
        
        for item in self.lines: self.canvas.delete(item)
        self.lines.clear()          

        
        if self.direction == 'x':
            end = 0 if self.line_visibility else self.canvas.winfo_height() - 5
        else:
            end = self.canvas.winfo_width() if self.line_visibility else 5

        for val in self.pos:
            if self.direction == 'x':
                pos = [val, self.canvas.winfo_height(), val, end]
                self.lines.append(self.canvas.create_line(pos, fill="gray"))
            else:
                pos = [0, val, end, val]
                self.lines.append(self.canvas.create_line(pos, fill="gray"))

class Log_Grid(Lin_Grid):

    def __init__(self, direction, canvas, steps=10, line_visibility=True):
        """ steps = number of grid- lines/numbers
            line_visibility = if gridlines active  """

        self.canvas = canvas
        self.canvas_dim = [0, 0]
        self.direction = direction

        self.number_of_steps = steps
        self.line_visibility = line_visibility

        # Actual Grid Lines
        self.pos = np.zeros(self.number_of_steps)
        self.lines = []

        self.update_pos()

    def redraw(self):
        
        for item in self.lines: self.canvas.delete(item)
        self.lines.clear()          

        if self.line_visibility == False: return
        
        const = self.pos[1]/9
        for val in self.pos:
            if self.direction == 'x':
                for j in range(9):
                    pos = [val + j*const, 0, val + j*const , self.canvas.winfo_height()]
                    
                    self.lines.append(self.canvas.create_line(pos, fill="gray"))
            else:
                for j in range(9):
                    pos = [0, val, self.canvas.winfo_width(), val]
                    self.lines.append(self.canvas.create_line(pos, fill="gray"))


    
                    (self.x_log_scale[0]*np.log10(data) 
                                  + self.x_log_scale[1])/self.x_scale_factor

    #     elif self.scale_type[0] == 'log':
    #         for i in self.x_boundary[0:-1]:
    #             for j in range(9):
    #                 x = self.scale_vector([i * (1 + j)], 'x')[0]
    #                 pos = [x, 0, x, self.plot_dimensions[1]]
    #                 self.x_grid_lines.append(self.plot.create_line(pos, fill="gray"))


