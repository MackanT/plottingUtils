from tkinter import *
import numpy as np

class DataSeries:

    def __init__(self, tag, canvas):
        self.tag = tag
        self.line_width = 3
        self.scatter_width = 4
        self.color = '#5FBFF9'
        self.canvas = canvas
        self.plot_type = 'line'

        self.plotted_items = []
        
        self.has_colorbar = False
        self.has_markerbar = False
        self.has_drawn = False
        self.has_animation = False
        self.has_color = False
        self.has_legend = False

    def get_tag(self):
        return self.tag

    def set_legend(self, data_input):
        # index = data_input.find('=') + 1
        # self.legend_name = data_input[index:]
        self.legend_name = data_input
        self.has_legend = True

    def get_legend(self):
        if self.has_legend: return self.legend_name
        else: return None

    def is_animated(self):
        return self.has_animation

    def set_animation(self, has_animation):
        self.has_animation = has_animation

    def set_data_length(self, data_length):
        self.data_length = data_length
        self.data_points = np.zeros((2, data_length))
        self.scaled_points = np.zeros((2, data_length))

    def is_drawn(self):
        return self.has_drawn

    def draw(self, index):
        
        self.has_drawn = True
        if not index: index = [index]
        if self.has_animation == True:    
            self.plotted_items = np.empty(1)
            p1 = self.scaled_points[0,index[0]]
            p2 = self.scaled_points[1,index[0]]
            use_color = self.colorbar[index] if self.has_colorbar else self.color
            dot_size = self.markerbar[index]/2 if self.has_markerbar else self.scatter_width/2
            if self.plot_type == 'scatter': 
                self.plotted_items[0] = self.__draw_dot(p1, p2, dot_size, use_color)
            elif self.plot_type == 'line': 
                p3 = self.scaled_points[0,index[0]+1]
                p4 = self.scaled_points[1,index[0]+1]
                self.plotted_items[0] = self.__draw_line(p1,p2,p3,p4)  
        else:
            self.plotted_items = np.empty(len(index))
            drawPos = 0
            for i in index:
                p1 = self.scaled_points[0,i]
                p2 = self.scaled_points[1,i]
                use_color = self.colorbar[i] if self.has_colorbar else self.color
                dot_size = self.markerbar[i]/2 if self.has_markerbar else self.scatter_width/2
                if self.plot_type == 'scatter':
                    self.plotted_items[drawPos] = self.__draw_dot(p1, p2, dot_size, use_color)
                elif self.plot_type == 'line' and i < self.data_length-1:
                    self.plotted_items[drawPos] = self.__draw_line(p1,p2,self.scaled_points[0,i+1],self.scaled_points[1,i+1])
                drawPos += 1

    def __draw_dot(self, p1, p2, dot_size, use_color):
        return self.canvas.create_oval(p1-dot_size,p2-dot_size,p1+dot_size,
                                       p2+dot_size, width=0, fill=use_color)

    def __draw_line(self, p1, p2, p3, p4):
        return self.canvas.create_line(p1,p2,p3,p4, width=self.line_width, 
                                       fill=self.color)

    def undraw_item(self, index):
        for item in self.plotted_items: self.canvas.delete(int(item))
        self.plotted_items = np.empty(index)

    def move_item(self, index):

        items = [0] if self.has_animation else range(len(self.plotted_items))
        if isinstance(index, int): index = np.array([index])
        if self.plot_type == 'scatter':
            for i in items:
                p1 = self.scaled_points[0,index[i]] - self.scatter_width/2
                p2 = self.scaled_points[1,index[i]] - self.scatter_width/2
                self.canvas.moveto(int(self.plotted_items[i]), p1, p2)
        elif self.plot_type == 'line':
            for i in items:
                if i != self.data_length-1:
                    p1 = self.scaled_points[0,index[i]]
                    p2 = self.scaled_points[1,index[i]]
                    p3 = self.scaled_points[0,index[i]+1]
                    p4 = self.scaled_points[1,index[i]+1]
                    self.canvas.coords(int(self.plotted_items[i]), p1, p2, p3, p4)

    def update_colors(self):
        for i in range(len(self.plotted_items)):
            use_color = self.colorbar[i] if self.has_colorbar else self.color
            self.canvas.itemconfig(int(self.plotted_items[i]), fill=use_color)

    def update_markers(self):
        for i in range(len(self.plotted_items)):
            
            dot_size = self.markerbar[i]/2 if self.has_markerbar else self.scatter_width/2

            p1 = self.scaled_points[0,i]
            p2 = self.scaled_points[1,i]
            self.canvas.coords(int(self.plotted_items[i]), p1 - dot_size, p2 - dot_size, p1 + dot_size, p2 + dot_size)

    def update_item(self, x, y, *args):
        self.scaled_points[0,:] = x
        self.scaled_points[1,:] = y
        if self.has_animation: self.move_item(args[0])
        else: self.move_item([i for i in range(self.data_length)])

    def get_color(self):
        if self.has_colorbar: return self.colorbar
        else: return self.color

    def is_colored(self):
        return self.has_color

    def set_color(self, color):
        self.has_color = True
        self.color = color

    def set_colorbar(self, color):
        self.has_colorbar = True
        self.colorbar = np.array(color)

    def set_markerbar(self, sizes):
        self.has_markerbar = True
        self.markerbar = np.array(sizes)

    def get_line_width(self):
        return self.line_width

    def set_line_width(self, linewidth):
        self.line_width = linewidth

    def get_scatter_size(self):
        return self.scatter_width

    def set_scatter_size(self, scatter_width):
        self.scatter_width = scatter_width

    def get_plot_type(self):
        return self.plot_type
    
    def set_plot_type(self, plot_type):
        self.plot_type = plot_type

    def get_number_of_points(self):
        return self.data_length

    def add_points(self, x, y):
        self.set_data_length(np.size(x))   
        self.data_points[0,:] = x
        self.data_points[1,:] = y
    
    def add_scaled_points(self, x, y):
        self.scaled_points[0,:] = x
        self.scaled_points[1,:] = y

    def edit_point(self, point, index):
        self.data_points[index] = point

    def get_point(self, index):
        return self.data_points[:,index]

    def get_points(self):
        return self.data_points

    def clear_data(self):
        self.undraw_item(0)
        self.data_points = np.empty(2)