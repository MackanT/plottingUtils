from tkinter import *
from DataSeries import DataSeries
import math
import numpy as np
import os

class Plot:


    def __init__(self, width, height, window_name):
        
        # Dimensions
        self.screen_width = width
        self.screen_height = height
        self.screen_padding_y = width/10
        self.screen_padding_x = height/15
        self.font_size = int(width/100)
        self.font_type = 'arial %d' %self.font_size
        
        # Colors
        self.bg_color = '#E0DFD5'
        self.fg_color = '#313638'
        self.highlight_colors = ['#EF6461', '#9CD08F', '#E4B363', 
                                 '#E8E9EB', '#5C6B73']
        self.default_plot_colors = ['#5FBFF9', '#E85F5C', '#B2FFD6', 
                                    '#F9C784', '#343434', '#613F75']
        self.default_plot_color_counter = 0

        # Enabled Parameters
        self.has_title = False
        self.has_x_axis = False
        self.has_x_grid = False
        self.has_y_axis = False
        self.has_y_grid = False
        self.has_x_label = False
        self.has_y_label = False
        self.has_legend = False
        self.has_graph = False

        # Graphical Window
        self.root_window = Tk()
        self.root_window.title(window_name)

        self.canvas = Canvas(self.root_window, width = self.screen_width, 
                             height = self.screen_height, bg=self.bg_color)
        
        offset_x = 2*self.screen_padding_x
        offset_y = self.screen_padding_y
        canvas_width = width-2*self.screen_padding_x
        canvas_height = height-2*self.screen_padding_y/3

        self.canvas_boundary = [offset_x, offset_y, canvas_width, canvas_height]
        self.canvas.pack()

        self.plot_dimensions = [int(self.canvas_boundary[2]-self.canvas_boundary[0]), 
                                int(self.canvas_boundary[3]-self.canvas_boundary[1])]
        self.plot = Canvas(self.root_window, width = self.plot_dimensions[0], 
                           height = self.plot_dimensions[1], bg='#ffffff')
        self.plot.place(x = offset_x, y = offset_y ,anchor = NW)

        # Ginput
        """
        To be rewritten! - Ginput + lin approx
        """
        self.root_window.bind('<Button-1>', self.leftClick)
        self.ginput_click_counter = -1
        self.ginput_clicked_postions = []
        self.lineData = []
        self.lineApproximations = []

        # Animation
        self.has_animation = False
        self.animation_speed = 1
        self.animation_tags = []
        self.root_window.bind('<Right>', self.right_arrow_key_command)
        self.root_window.bind('<Left>', self.left_arrow_key_command)

        # Save Locations
        self.file_save_location = os.path.dirname(os.path.realpath(__file__)) \
                + '\\saveData'
        if not os.path.exists(self.file_save_location): 
                os.makedirs(self.file_save_location)

        """
        rewrite as nicer array of scale factors....
        """
        # Scaling Factors
        self.x_scale_factor = 0
        self.y_scale_factor = 0
        self.scale_type= ['lin', 'lin']
        self.x_boundary = []
        self.y_boundary = []

        self.x_axis_numbers = []
        self.y_axis_numbers = []
        self.x_grid_lines = []
        self.y_grid_lines = []
        self.legend_content = []
        self.legend_markers = []
        self.plotted_text = []
        self.plotted_text_tags = []
        self.data_series = []

        self.color_bar = []

        self.plotted_items = [] # Not in use anymore??? Only currently best fit = broken
        
        # Editing Tools
        self.add_dataset('bFit')
        self.root_window.bind('<e>', self.__open_plot_editor)
        self.has_plot_editor = False
        self.plot_editor_selected_counter = 0
        self.plot_editor_selected_item = None
        self.editor_canvas = Canvas(self.root_window, width = self.screen_width, 
                                    height = 230, bg=self.highlight_colors[3])
        self.generate_plot_editor()


    # Datasets

    def add_dataset(self, tag):
        if self.find_dataset(tag) != None: return
        else: self.data_series.append(DataSeries(tag, self.plot))

    def remove_dataset(self, tag):
        dataset = self.find_dataset(tag)
        if dataset != None:
            for i in range(len(self.data_series)):
                if self.data_series[i].getTag() == tag:
                    self.data_series.pop(i)
                    dataset.clearData()
                    return

    def clear_dataset(self, tag):
        dataset = self.find_dataset(tag)
        if dataset != None: dataset.clearData()

    def remove_drawn_items(self, thisList):
        for item in thisList: self.canvas.delete(item)            
        thisList.clear()

    def find_dataset(self, tag):
        for item in self.data_series:
            if item.get_tag() == tag: return item

    def find_tag_number(self, tag, search_list):
        for i in range(len(search_list)):
            if search_list[i] == tag: return i

    # Ginput (Will be rewritten... will not clean up)

    def leftClick(self, event):
        if self.ginput_click_counter >= 0:
            xLog = 10**(((event.x - self.canvas_boundary[0])*self.x_scale_factor-self.x_log_scale[1])/self.x_log_scale[0])
            yLog = 10**(((self.canvas_boundary[3] - event.y)*self.y_scale_factor-self.y_log_scale[1])/self.y_log_scale[0])

            self.ginput_clicked_postions.append([xLog, yLog])
            self.lineData.append([event.x, event.y])
        if self.ginput_click_counter == 0:
            self.canvas.create_line(self.lineData[0],self.lineData[1], fill='green', width=2)
            
            tau = (math.log10(self.ginput_clicked_postions[1][1])-math.log10(self.ginput_clicked_postions[0][1]))/(math.log10(self.ginput_clicked_postions[1][0])-math.log10(self.ginput_clicked_postions[0][0]))
            self.update_legend(['Continuous Tree Growth', 'Linearised Slope'],['',round(1-tau,4)])
        
        self.ginput_click_counter -= 1

        if self.plot_editor_selected_counter == 1: self.find_item(event.x, event.y)

    def ginput(self, count):
        self.ginput_clicked_postions = []
        self.ginput_click_counter = count - 1

    # Plot Properties

    def set_line_color(self, color, tag):
        dataset = self.find_dataset(tag)
        if dataset != None: dataset.set_color(color)

    def set_line_width(self, lineWidth, tag):
        dataset = self.find_dataset(tag)
        if dataset != None: dataset.set_line_width(lineWidth)

    def set_dot_size(self, size, tag):
        dataset = self.find_dataset(tag)
        if dataset != None: dataset.set_dot_size(size)

    # Plot Text

    def set_title(self, text):
        if self.has_title == False:
            self.has_title = True
            self.title = self.canvas.create_text(self.screen_width/2, 
                        4*self.font_size, font='arial %d' %(2*self.font_size), 
                        text = text, fill=self.fg_color)
        else: self.canvas.itemconfig(self.title, text = text)         

    def add_text(self, position, text, tag):
        scaled_pos = [self.scale_vector(position[0], 'x'), 
                      self.scale_vector(position[1], 'y')]
        self.plotted_text.append(self.plot.create_text(scaled_pos, anchor=NW,
                      font=self.font_type, text=text, fill=self.fg_color))
        self.plotted_text_tags.append(tag)

    def update_text(self, text, tag):
        text_item = self.find_tag_number(tag, self.plotted_text_tags)
        if text_item != None:
            self.canvas.itemconfig(self.plotted_text[text_item], text = text)
            return

    # Axis

    def set_labels(self, textx, texty):

        if self.has_x_label == False:
            self.has_x_label = True
            p1 = self.screen_width/2
            p2 = self.canvas_boundary[3] + 4*self.font_size
            self.xLabel = self.canvas.create_text(p1, p2, font=self.font_type,
                                                text = textx, fill=self.fg_color)
        elif textx != 'keep': self.canvas.itemconfig(self.xLabel, text=textx)
        if self.has_y_label == False:
            self.has_y_label = True
            p1 = self.canvas_boundary[0] - 6*self.font_size
            p2 = self.canvas_boundary[1] + self.plot_dimensions[1]/2
            self.yLabel = self.canvas.create_text(p1, p2, font=self.font_type, 
                                    angle=90, text = texty, fill=self.fg_color)
        elif texty != 'keep': self.canvas.itemconfig(self.yLabel, text=texty)

    def set_x_axis(self, x_start, x_end, *args):

        num_ticks = 10
        self.remove_drawn_items(self.x_axis_numbers)

        if x_start == 'keep': x_start = self.x_boundary[0]
        if x_end == 'keep': x_end = self.x_boundary[-1]

        for name in args:
            if name == 'graph':
                if self.has_x_axis: return
                if self.x_boundary:
                    cond1 = x_start > self.x_boundary[0]
                    cond2 = x_end < self.x_boundary[-1]
                    if cond1 and cond2 : return
                    else:
                        if x_start > self.x_boundary[0]: 
                            x_start = self.x_boundary[0]
                        if x_end < self.x_boundary[-1]: 
                            x_end = self.x_boundary[-1]
            elif name == 'lock': self.has_x_axis = True
            elif name == 'log': self.scale_type[0] = 'log'
            elif name == 'lin': self.scale_type[0] = 'lin'
            elif name == 'show': self.has_x_grid = True
            elif name == 'hidden': self.has_x_grid = False
            elif isinstance(name, int): num_ticks = name

        if num_ticks == 0: num_ticks = 1 

        # Scale relative to 0
        if x_start > x_end:
            tmp = x_start
            x_start = x_end
            x_end = tmp
        
        common_term = self.plot_dimensions[0]/(x_start - x_end)
        abs_term = abs(x_start)/(abs(x_start) + abs(x_end))
        if x_end < 0: self.x0 = common_term * x_end
        elif x_start > 0: self.x0 = common_term * (x_start)
        else: self.x0 = abs_term * self.plot_dimensions[0]

        self.x_boundary.clear()

        if self.scale_type[0] == 'lin':
            self.x_scale_factor = (x_end-x_start)/self.plot_dimensions[0]

            valueSize = (x_end-x_start)/num_ticks
            step_size = self.plot_dimensions[0]/num_ticks

            for i in range(num_ticks+1):
                self.x_boundary.append(x_start + i*valueSize)
            
        elif self.scale_type[0] == 'log':
            
            if x_start <= 0: 
                x_start = 1e-3
                x_end = 1e3
            self.x_scale_factor = (x_end-x_start)/self.plot_dimensions[0]

            k = (x_start-x_end)/(math.log10(x_start)-math.log10(x_end))
            c = x_end - k * math.log10(x_end)
            self.x_log_scale = [k, c]

            num_ticks = round(math.log10(x_end/x_start))
            step_size = self.plot_dimensions[0]/num_ticks

            for i in range(num_ticks+1):
                self.x_boundary.append(x_end * 10**(-num_ticks+i))
        
        for i in range(num_ticks + 1):
            pos = [self.canvas_boundary[0] + i*step_size, 
                   self.canvas_boundary[3] + self.font_size/2]
            tex = str(round(self.x_boundary[i],2))
            self.x_axis_numbers.append(self.canvas.create_text(pos, anchor=N,
                            fill=self.fg_color, font=self.font_type, text=tex))

        if self.has_x_grid == True: self.set_grid_lines('x', num_ticks)
        elif self.has_x_grid == False: self.remove_grid_lines('x')
        
        self.update_plots('all')

    def set_y_axis(self, y_start, y_end, *args):
        
        num_ticks = 10
        self.remove_drawn_items(self.y_axis_numbers)
        
        if y_start == 'keep': y_start = self.y_boundary[0]
        if y_end == 'keep': y_end = self.y_boundary[-1]

        for name in args:
            if name == 'graph':
                if self.has_y_axis == True: return
                if self.y_boundary:
                    cond1 = y_start > self.y_boundary[0]
                    cond2 = y_end < self.y_boundary[-1]
                    if cond1 and cond2: return
                    else:
                        if y_start > self.y_boundary[0]: 
                            y_start = self.y_boundary[0]
                        if y_end < self.y_boundary[-1]: 
                            y_end = self.y_boundary[-1]
            elif name == 'lock': self.has_y_axis = True
            elif name == 'log': self.scale_type[1] = 'log'
            elif name == 'lin': self.scale_type[1] = 'lin'
            elif name == 'show': self.has_y_grid = True
            elif name == 'hidden': self.has_y_grid = False
            elif isinstance(name, int): num_ticks = name

        if num_ticks == 0: num_ticks = 1 

        # Scale relative to 0
        if y_start > y_end:
            tmp = y_start
            y_start = y_end
            y_end = tmp
        
        common_term = self.plot_dimensions[1]/(y_start - y_end)
        abs_term = abs(y_end)/(abs(y_start) + abs(y_end))
        if y_end < 0: self.y0 = common_term*abs(y_end)
        elif y_start > 0: self.y0 = common_term*y_start + self.plot_dimensions[1]
        else: self.y0 = abs_term * self.plot_dimensions[1]

        self.y_boundary.clear()

        if self.scale_type[1] == 'lin':
            self.y_scale_factor = (y_end-y_start)/self.plot_dimensions[1]

            valueSize = (y_end-y_start)/num_ticks
            step_size = self.plot_dimensions[1]/num_ticks

            for i in range(num_ticks+1):
                self.y_boundary.append(y_start + i*valueSize)

        elif self.scale_type[1] == 'log':
            if y_start <= 0: 
                y_start = 1e-3
                y_end = 1e0
            self.y_scale_factor = (y_end-y_start)/self.plot_dimensions[1]

            k = (y_start-y_end)/(math.log10(y_start)-math.log10(y_end))
            c = y_end - k * math.log10(y_end)
            self.y_log_scale = [k, c]

            num_ticks = round(math.log10(y_end/y_start))
            step_size = self.plot_dimensions[1]/num_ticks

            for i in range(num_ticks+1):
                self.y_boundary.append(y_end * 10**(-num_ticks+i))

        for i in range(num_ticks + 1):
            pos = [self.canvas_boundary[0] - self.font_size/2, 
                   self.canvas_boundary[3] - i*step_size]
            tex = str(round(self.y_boundary[i],5))
            self.y_axis_numbers.append(self.canvas.create_text(pos, anchor=E,
                            fill=self.fg_color, font=self.font_type, text=tex))

        if self.has_y_grid == True: self.set_grid_lines('y', num_ticks)
        elif self.has_y_grid == False: self.remove_grid_lines('y')

        self.update_plots('all')

    # Grid Lines

    def __grid_x(self, num_ticks):
        self.remove_grid_lines('x')
        self.has_x_grid = True
        if self.scale_type[0] == 'lin':    
            step_size = self.plot_dimensions[0]/num_ticks
            for i in range(num_ticks):
                pos = [i*step_size, 0, i*step_size, self.plot_dimensions[1]]
                self.x_grid_lines.append(self.plot.create_line(pos, fill="gray"))
        elif self.scale_type[0] == 'log':
            for i in self.x_boundary[0:-1]:
                for j in range(9):
                    x = self.scale_vector([i * (1 + j)], 'x')[0]
                    pos = [x, 0, x, self.plot_dimensions[1]]
                    self.x_grid_lines.append(self.plot.create_line(pos, fill="gray"))
    
    def __grid_y(self, num_ticks):
        self.remove_grid_lines('y')
        self.has_y_grid = True
        if self.scale_type[1] == 'lin':
            step_size = self.plot_dimensions[1]/num_ticks
            for i in range(num_ticks):
                pos = [0, i*step_size, self.plot_dimensions[0], i*step_size]
                self.y_grid_lines.append(self.plot.create_line(pos, fill="gray"))
        elif self.scale_type[1] == 'log':
            for i in self.y_boundary[0:-1]:
                for j in range(9):
                    y = self.scale_vector([i * (1 + j)], 'y')[0]
                    pos = [0, y, self.plot_dimensions[0], y]
                    self.y_grid_lines.append(self.plot.create_line(pos, fill="gray"))

    def set_grid_lines(self, order, num_ticks):
        if order == 'x':
            self.has_x_grid = True
            self.__grid_x(num_ticks)
        elif order == 'y':
            self.has_y_grid = True
            self.__grid_y(num_ticks)
        elif order == 'xy':
            self.has_x_grid = True
            self.has_y_grid = True
            self.__grid_x(num_ticks)
            self.__grid_y(num_ticks)
        
        self.raise_items()

    def remove_grid_lines(self, order):
        if order == 'x': 
            for item in self.x_grid_lines:
                self.plot.delete(item)
            self.x_grid_lines.clear()
            self.has_x_grid = False
        elif order == 'y': 
            for item in self.y_grid_lines:
                self.plot.delete(item)
            self.y_grid_lines.clear()
            self.has_y_grid = False

    # Legend

    def set_legend(self, names, values, pos, *tags):
        
        num_data = len(values)

        if self.has_legend == False:
            self.has_legend = True

            cond1 = not isinstance(names, list)
            cond2 = len(values) > 1
            if cond1 and cond2: names = [names for i in range(num_data)]

            visibility = 'normal' if self.has_graph else 'hidden'
            text_length = 0

            for i in range(num_data):
                tmpStr = names[i] + ' ' + str(values[i])
                if len(tmpStr) > text_length: text_length = len(tmpStr) 
            text_length *= 3*self.font_size/4
            
            if pos[0] == 'N': yOffset = self.font_size
            elif pos[0] == 'S': yOffset = (self.plot_dimensions[1] 
                                           - 2*num_data*self.font_size)
            if pos[1] == 'W': xOffset = 2*self.font_size
            elif pos[1] == 'E': xOffset = self.plot_dimensions[0] - text_length

            for i in range(num_data):
                self.legend_content.append(self.plot.create_text(
                            xOffset, yOffset + 2*i*self.font_size, anchor=NW, 
                            fill=self.fg_color, font=self.font_type, 
                            text='%s  %s'%(names[i], values[i]), state=visibility))
                
                p1 = xOffset-3/2*self.font_size
                p2 = yOffset + (2*i+1/4)*self.font_size
                p3 = xOffset-1/2*self.font_size
                p4 = yOffset + (2*i+5/4)*self.font_size
                self.legend_markers.append(self.plot.create_oval(
                            p1, p2, p3, p4, fill=self.default_plot_colors[i], 
                            state=visibility))

        else:
            tag_num = self.find_tag_number(tags[0], self.data_series)
            self.plot.itemconfig(self.legend_content[tag_num], state='normal')
            self.plot.itemconfig(self.legend_markers[tag_num], state='normal')

    def update_legend(self, names, values):
        for i in range(len(names)):
            self.plot.itemconfig(self.legend_content[i], 
                                 text='%s:  %s'%(names[i], values[i]))

    # Data validation for plotted objects

    def scale_vector(self, data, *args):
        
        for name in args:
            if name == 'window': 
                self.x = self.canvas_boundary[0]
                self.y = self.canvas_boundary[3]
            else: 
                self.x = 0
                self.y = self.plot_dimensions[1]
        
        for name in args:
            if name == 'xy': 
                if self.scale_type[0] == 'log': 
                    dataX = np.array(data[0,:])
                    np.where(dataX == 0, 1e-20, dataX)
                    dataX = self.x + (self.x_log_scale[0]*np.log10(data) 
                                   + self.x_log_scale[1])/self.x_scale_factor

                    dataY = np.array(data[1,:])
                    np.where(dataY == 0, 1e-20, dataY)
                    dataY =  self.y - (self.y_log_scale[0]*np.log10(data) 
                                    + self.y_log_scale[1])/self.y_scale_factor

                    return [dataX, dataY]

                elif self.scale_type[0] == 'lin':
                    dataX = np.array(data[0,:])/self.x_scale_factor + self.x0 
                    dataY = -np.array(data[1,:])/self.y_scale_factor + self.y0
                    return [dataX, dataY]
            elif name == 'x':
                if self.scale_type[0] == 'log': 
                    data = np.array(data)
                    np.where(data == 0, 1e-20, data)
                    return self.x + (self.x_log_scale[0]*np.log10(data) 
                                  + self.x_log_scale[1])/self.x_scale_factor
                elif self.scale_type[0] == 'lin':
                    return np.array(data)/self.x_scale_factor + self.x0
            elif name == 'y':
                if self.scale_type[1] == 'log':
                    data = np.array(data)
                    np.where(data == 0, 1e-20, data)
                    return self.y - (self.y_log_scale[0]*np.log10(data) 
                                  + self.y_log_scale[1])/self.y_scale_factor
                elif self.scale_type[1] == 'lin':
                    return -np.array(data)/self.y_scale_factor + self.y0
            
    def get_scale_factor(self):
        return [self.x_scale_factor, self.y_scale_factor]

    # Plot Data

    def graph(self, x, y, tag, *args):
        self.has_graph = True

        dataset = self.find_dataset(tag)
        if dataset == None: 
            self.add_dataset(tag)
            dataset = self.find_dataset(tag)

        # Plotting Parameters
        
        plot_range = range(len(x))
        plot_type = 'line'
        grid_state = ''
        for name in args:
            if name == 'scatter': plot_type = 'scatter'
            elif name == 'animate':
                self.enable_animator(len(x)-1)
                self.animation_tags.append(tag)
                dataset.set_animation(True)
                plot_range = 0
            elif name == 'log': 
                self.scale_type[0] = 'log'
                self.scale_type[1] = 'log'
            elif name == 'show':
                grid_state = 'show'

        dx = (np.amax(x)-np.amin(x))/10
        dy = (np.amax(y)-np.amin(y))/10
        self.set_x_axis(np.amin(x)-dx, np.amax(x)+dx, grid_state, 'graph')
        self.set_y_axis(np.amin(y)-dy, np.amax(y)+dy, grid_state, 'graph')

        dataset.add_points(x,y)
        dataset.add_scaled_points(self.scale_vector(x, 'x'), 
                                  self.scale_vector(y, 'y'))

        if dataset.is_colored() == False:
            dataset.set_color(self.default_plot_colors[
                self.default_plot_color_counter%len(self.default_plot_colors)])
            self.default_plot_color_counter += 1
        
        dataset.set_plot_type(plot_type)
        dataset.draw(plot_range)

        if self.has_legend == True: self.set_legend('','','',tag)

    ### nPart of ginput!  
    def gen_x_path(self, points, x_start, x_end):
        if self.scale_type[0] == 'lin':
            dx = float(x_end-x_start)/points
            xPoints = [(x_start + i*dx) for i in range(points)]
            return xPoints
        elif self.scale_type[0] == 'log':
            nPoints = int(math.sqrt(points))
            xPoints = []
            for i in self.x_boundary[0:-1]:
                for j in range(nPoints):
                    xPoints.append(self.x_boundary[0] + i*(1+j))
            return xPoints
    def plotBestFit(self, *args):
        
        dataset = self.find_dataset('bFit')
        if dataset != None: 
            # num = self.find_dataset('bFit')
            for i in range(dataset.getNumberOfPoints()):
                y = self.lineApproximations[0] + self.lineApproximations[1]*math.exp(self.lineApproximations[2]*dataset.getPoint(i)[0])
                dataset.appendPoint([dataset.getPoint(i)[0],y], i)
            
            self.update_plots('bFit')
    
    def update_plots(self, *args):
        if args[0] == 'all':
            for dataset in self.data_series:
                if dataset.is_drawn() == True:        
                    oldP = dataset.get_points()
                    newX = self.scale_vector(oldP[0,:], 'x')
                    newY = self.scale_vector(oldP[1,:], 'y')
                    newIndex = self.animationScrollbar.get() if dataset.is_animated() == True else 0
                    dataset.update_item(newX, newY, newIndex)
    
    def enable_animator(self, length):
        if self.has_animation == False:
            self.animationScrollbar = Scale(self.canvas, from_=1, to=length, 
                        resolution=1, bg=self.bg_color, command=self.animate)
            self.animationScrollbar.place(x = self.canvas_boundary[2] 
                        + self.font_size , y = self.canvas_boundary[1])
            self.animationScrollbar.config(length = self.canvas_boundary[3]
                        - self.canvas_boundary[1] - self.font_size)
            self.has_animation = True

    def animate(self, value):
        value = int(value)-1
        for tag in self.animation_tags: self.find_dataset(tag).move_item(value)

    def right_arrow_key_command(self, event):
        if self.has_animation == True:
            self.animationScrollbar.set(self.animationScrollbar.get()
                                        + self.animation_speed)

    def left_arrow_key_command(self, event):
        if self.has_animation == True:
            self.animationScrollbar.set(self.animationScrollbar.get() 
                                        - self.animation_speed)

    # Colors

    def get_color(self, dataset):
        colors = dataset.get_color()
        data_range = range(dataset.getNumberOfPoints())
        if isinstance(colors, str): 
            colors = [dataset.get_color() for n in data_range]
        return colors

    def colorbar(self, colors, values, steps, tag):
        for item in self.color_bar: self.canvas.delete(item)
        self.color_bar.clear()
        
        num = int(len(colors)/steps)
        stepLength = self.plot_dimensions[1]/steps
        yPos = self.canvas_boundary[3]
        xPos = self.canvas_boundary[2]

        for i in range(steps): 

            p1 = xPos + self.font_size
            p2 = yPos - i*stepLength
            p3 = xPos + 2.5*self.font_size
            p4 = yPos - (i+1)*stepLength
            self.color_bar.append(self.canvas.create_rectangle(p1, p2, p3, p4, 
                                  fill=colors[num*i], width=0))
        
        stepLength = self.plot_dimensions[1]/(len(values)-1)

        for i in range(len(values)):
            p1 = xPos + 3*self.font_size
            p2 = yPos - i*stepLength
            self.color_bar.append(self.canvas.create_text(p1, p2, anchor=W, 
                                  font=self.font_type, text = values[i]))

    # Is this even in use???
    def clear_plot_data(self, tag):
        plotPos = self.find_dataset(tag)
        if plotPos != None: 
            for item in self.plotted_items[plotPos]:
                self.canvas.delete(item)

    def get_plot_x_values(self, index, tag):
        dataset = self.find_dataset(tag)
        if dataset != None: return dataset.get_point(index)

    def get_plot_y_values(self, index, tag):
        dataset = self.find_dataset(tag)
        if dataset != None: return dataset.get_point(index)

    # Save Data

    def save_data(self, *args):

        for i in args:
            dataset = self.find_dataset(i)
            data_name = self.file_save_location + '\\' + str(i) + '.txt'
            data_file = open(data_name, 'w+')
            
            for j in range(dataset.getNumberOfPoints()):
                data = str(dataset.getPoint(j)).replace(" ", "")
                data_file.write(data[1:-1] + '\n')
            
            data_file.close()
    
    def load_data(self, tag):

        data_name = self.file_save_location + '\\' + str(tag) + '.txt'
        if os.path.exists(data_name):

            x = []
            y = []
            with open(data_name) as f: lines = f.read().splitlines()
            for i in range(len(lines)):
                ind = lines[i].find(',')

                x.append(lines[i][0:ind])
                y.append(lines[i][ind+1:])

            return [x, y]

    # Plot Editor

    def __open_plot_editor(self, event):
        if self.has_plot_editor == False:
            self.update_editor()
            self.has_plot_editor = True
            self.editor_canvas.pack()

    def __close_editor(self):
        if self.has_plot_editor == True:
            self.has_plot_editor = False
            self.editor_canvas.forget()

    def update_editor(self):
        self.__update_editor_buttons('x_grid', 'y_grid', 'x_linlog','y_linlog', 
                                     'txt_input', 'animation_speed')

    def generate_plot_editor(self):

        # Title Edit
        self.editor_canvas.create_text(10, 10, anchor=W, text='Title')
        self.editor_canvas.create_line(10,16,200,16)
        self.title_input = Entry(self.editor_canvas, fg='gray')
        self.title_input.insert(0, 'Title')
        self.title_input.place(x=10,y=22, anchor=NW)
        self.__add_focus_listeners(self.title_input)
        self.title_input.bind("<Return>", lambda event: 
                    self.set_title(self.title_input.get()))

        # X Axis Edit
        self.editor_canvas.create_text(10, 60, anchor=W, text='X Axis')
        self.editor_canvas.create_line(10,66,200,66)
        self.lower_x_scale = Entry(self.editor_canvas, fg='gray')
        self.lower_x_scale.insert(0, 'Lower X')
        self.lower_x_scale.place(x=10,y=72, anchor=NW)
        self.__add_focus_listeners(self.lower_x_scale)
        self.lower_x_scale.bind("<Return>", lambda event: 
                    self.__change_axis('x','low', self.lower_x_scale.get()))

        self.upper_x_scale = Entry(self.editor_canvas, fg='gray')
        self.upper_x_scale.insert(0, 'Upper X')
        self.upper_x_scale.place(x=10,y=92, anchor=NW)
        self.__add_focus_listeners(self.upper_x_scale)
        self.upper_x_scale.bind("<Return>", lambda event: 
                    self.__change_axis('x','high', self.upper_x_scale.get()))

        self.x_scale_steps = Entry(self.editor_canvas, fg='gray')
        self.x_scale_steps.insert(0, '#Gridlines')
        self.x_scale_steps.place(x=10,y=112, anchor=NW)
        self.__add_focus_listeners(self.x_scale_steps)
        self.x_scale_steps.bind("<Return>", lambda event: self.set_x_axis('keep','keep', int(self.x_scale_steps.get())))

        self.x_grid_button = Button(self.editor_canvas, text='On', width=5, 
                    command=lambda: self.__enable_grid('x'), 
                    bg=self.highlight_colors[1])
        self.x_grid_button.place(x=145,y=75, anchor=NW)

        self.x_linlog_button = Button(self.editor_canvas, text='lin', width=5, 
                    command=lambda: self.__switch_linlog('x'), bg=self.bg_color)
        self.x_linlog_button.place(x=145,y=105, anchor=NW)


        # Y Axis Edit
        self.editor_canvas.create_text(10, 150, anchor=W, text='Y Axis')
        self.editor_canvas.create_line(10,156,200,156)
        self.lower_y_scale = Entry(self.editor_canvas, fg='gray')
        self.lower_y_scale.insert(0, 'Lower Y')
        self.lower_y_scale.place(x=10,y=162, anchor=NW)
        self.__add_focus_listeners(self.lower_y_scale)
        self.lower_y_scale.bind("<Return>", lambda event: 
                    self.__change_axis('y','low', self.lower_y_scale.get()))

        self.upper_y_scale = Entry(self.editor_canvas, fg='gray')
        self.upper_y_scale.insert(0, 'Upper Y')
        self.upper_y_scale.place(x=10,y=182, anchor=NW)
        self.__add_focus_listeners(self.upper_y_scale)
        self.upper_y_scale.bind("<Return>", lambda event: 
                    self.__change_axis('y','high', self.upper_y_scale.get()))

        self.y_scale_steps = Entry(self.editor_canvas, fg='gray')
        self.y_scale_steps.insert(0, '#Gridlines')
        self.y_scale_steps.place(x=10,y=202, anchor=NW)
        self.__add_focus_listeners(self.y_scale_steps)
        self.y_scale_steps.bind("<Return>", lambda event: 
                                self.set_y_axis('keep','keep', 
                                int(self.y_scale_steps.get())))

        self.y_grid_button = Button(self.editor_canvas, text='On', width=5, 
                                command=lambda: self.__enable_grid('y'), 
                                bg=self.highlight_colors[1])
        self.y_grid_button.place(x=145,y=165, anchor=NW)

        self.y_linlog_button = Button(self.editor_canvas, text='lin', width=5, 
                                command=lambda: self.__switch_linlog('y'), 
                                bg=self.bg_color)
        self.y_linlog_button.place(x=145,y=195, anchor=NW)

        # Labels
        self.editor_canvas.create_text(230, 10, anchor=W, text='Labels')
        self.editor_canvas.create_line(230,16,420,16)

        self.x_label_input = Entry(self.editor_canvas, fg='gray')
        self.x_label_input.insert(0, 'X Label')
        self.x_label_input.place(x=230,y=22, anchor=NW)
        self.__add_focus_listeners(self.x_label_input)
        self.x_label_input.bind("<Return>", lambda event: 
                            self.set_labels(self.x_label_input.get(), 'keep'))

        self.y_label_input = Entry(self.editor_canvas, fg='gray')
        self.y_label_input.insert(0, 'Y Label')
        self.y_label_input.place(x=230,y=42, anchor=NW)
        self.__add_focus_listeners(self.y_label_input)
        self.y_label_input.bind("<Return>", lambda event: 
                            self.set_labels('keep', self.y_label_input.get()))

        # Edit Texts
        self.editor_canvas.create_text(230, 80, anchor=W, text='Text Editor')
        self.editor_canvas.create_line(230,86,420,86)

        self.select_item_text_input = Entry(self.editor_canvas, fg='gray')
        self.select_item_text_input.insert(0, 'Text Editor')
        self.select_item_text_input.place(x=230,y=92, anchor=NW)
        self.__add_focus_listeners(self.select_item_text_input)
        self.select_item_text_input.bind("<Return>", self.__select_item_change)

        self.select_item_button = Button(self.editor_canvas, text='Select Item', 
                        bg=self.bg_color, width = 10, command=self.__select_item)
        self.select_item_button.place(x= 360, y = 92)

        # Animation
        self.editor_canvas.create_text(230, 130, anchor=W, text='Animation')
        self.editor_canvas.create_line(230,136,420,136)

        self.animation_speed_input = Entry(self.editor_canvas, fg='gray')
        self.animation_speed_input.insert(0, 'Animation Speed')
        self.animation_speed_input.place(x=230,y=142, anchor=NW)
        self.__add_focus_listeners(self.animation_speed_input)
        self.animation_speed_input.bind("<Return>", self.__set_animation_speed)

        # Exit
        self.editor_exit_button = Button(self.editor_canvas, text='X', 
                    bg=self.highlight_colors[0], command=self.__close_editor)
        self.editor_exit_button.place(x= self.screen_width - 20, y = 10)

        # Best Fit, not in use
        # self.bestFitButton = Button(self.editor_canvas, text='Best Fit', command=self.__bestFit)
        # self.bestFitButton.place(x= 450, y = 10)
        # self.edit_buttons = []
        # self.edit_buttons.append(Scale(self.editor_canvas, from_=0, to=10, 
        #                         resolution=0.01, command=self.__changeA))
        # self.edit_buttons.append(Scale(self.editor_canvas, from_=0, to=10, 
        #                         resolution=0.01, command=self.__changeB))
        # self.edit_buttons.append(Scale(self.editor_canvas, from_=0, to=100, 
        #                         resolution=0.01, command=self.__changeC))
        # for i in range(len(self.edit_buttons)):
        #     self.edit_buttons[i].place(x = (i+2)*120 + 300, y =30)

    def __add_focus_listeners(self, item):
        item.bind("<FocusIn>", self.__handle_focus_in)
        item.bind("<FocusOut>", self.__handle_focus_out)

    def __handle_focus_in(self, event):
        event.widget.delete(0, 'end')
        event.widget.config(fg='black')
    
    def __handle_focus_out(self, event):
        item = event.widget
        item.delete(0, 'end')
        item.config(fg='gray')
        iD = item.winfo_id() 
        if  iD == self.title_input.winfo_id(): item.insert(0, 'Title') 
        elif iD == self.lower_x_scale.winfo_id(): item.insert(0, 'Lower X') 
        elif iD == self.upper_x_scale.winfo_id(): item.insert(0, 'Upper X') 
        elif iD == self.lower_y_scale.winfo_id(): item.insert(0, 'Lower Y') 
        elif iD == self.upper_y_scale.winfo_id(): item.insert(0, 'Upper Y') 
        elif iD == self.x_scale_steps.winfo_id(): item.insert(0, '#Gridlines') 
        elif iD == self.y_scale_steps.winfo_id(): item.insert(0, '#Gridlines') 
        elif iD == self.x_label_input.winfo_id(): item.insert(0, 'X Label') 
        elif iD == self.y_label_input.winfo_id(): item.insert(0, 'Y Label') 
        elif iD == self.select_item_text_input.winfo_id(): 
                                        item.insert(0, 'Text Editor') 
        elif iD == self.animation_speed_input.winfo_id(): 
                                        item.insert(0, 'Animation Speed') 
        else: item.insert(0, 'Failure') 

    def __update_editor_buttons(self, *args):
        for button in args:
            if button == 'x_grid':
                x_grid_text = 'On' if self.has_x_grid == True else 'Off'
                x_grid_color = self.highlight_colors[1] if self.has_x_grid == True else self.highlight_colors[0]
                self.x_grid_button.config(text = x_grid_text, bg=x_grid_color)
                if self.scale_type[0] == 'log': self.x_scale_steps.config(state='disabled')
                elif self.scale_type[0] == 'lin': self.x_scale_steps.config(state='normal')
            elif button == 'y_grid':
                y_grid_text = 'On' if self.has_y_grid == True else 'Off'
                y_grid_color = self.highlight_colors[1] if self.has_y_grid == True else self.highlight_colors[0]
                self.y_grid_button.config(text = y_grid_text, bg=y_grid_color)
                if self.scale_type[1] == 'log': self.y_scale_steps.config(state='disabled')
                elif self.scale_type[1] == 'lin': self.y_scale_steps.config(state='normal')
            elif button == 'x_linlog': self.x_linlog_button.config(text=self.scale_type[0])
            elif button == 'y_linlog': self.y_linlog_button.config(text=self.scale_type[1])
            elif button == 'sel_item': 
                if self.plot_editor_selected_counter == 0: 
                    selText = 'Select Item'
                    selColor = self.bg_color
                elif self.plot_editor_selected_counter == 1:
                    selText = 'Selecting Item'
                    selColor = self.highlight_colors[1]
                elif self.plot_editor_selected_counter == 2:
                    selText = 'Unselect Item'
                    selColor = self.highlight_colors[0]
                self.select_item_button.config(text=selText, bg=selColor)
                self.select_item_text_input.delete(0, 'end')
                self.select_item_text_input.insert(0, 'Text Editor') 
            elif button == 'txt_input':
                if self.plot_editor_selected_counter != 2: self.select_item_text_input.config(state='disabled')
                else: self.select_item_text_input.config(state='normal')
            elif button == 'animation_speed' and self.has_animation == False:
                self.animation_speed_input.config(state='disabled')

    def __switch_linlog(self, order):
        
        if order == 'x':
            if self.scale_type[0] == 'lin': 
                self.set_x_axis('keep', 'keep', 'log')
            elif self.scale_type[0] == 'log': 
                self.set_x_axis('keep', 'keep', 'lin')
        elif order == 'y':
            if self.scale_type[1] == 'lin': 
                self.set_y_axis('keep', 'keep', 'log')
            elif self.scale_type[1] == 'log': 
                self.set_y_axis('keep', 'keep', 'lin')
        
        self.update_plots('all')
        self.__update_editor_buttons('x_grid', 'x_linlog', 
                                     'y_grid', 'y_linlog')
        
    def __enable_grid(self, order):
        if order =='x':
            if self.has_x_grid == True: self.remove_grid_lines(order)
            else: self.set_grid_lines(order, 10)
        if order =='y':
            if self.has_y_grid == True: self.remove_grid_lines(order)
            else: self.set_grid_lines(order, 10)
        self.raise_items()
        self.__update_editor_buttons('x_grid', 'y_grid')

    def __change_axis(self, order, direction, value):
        try:
            value = float(value)
            if order == 'x':
                if direction == 'low':
                    lower_x = value
                    upper_x = self.x_boundary[-1]
                elif direction == 'high':
                    lower_x = self.x_boundary[0]
                    upper_x = value
                self.set_x_axis(lower_x, upper_x)
            elif order == 'y':
                if direction == 'low':
                    lower_y = value
                    upper_y = self.y_boundary[-1]
                elif direction == 'high':
                    lower_y = self.y_boundary[0]
                    upper_y = value
                self.set_y_axis(lower_y, upper_y)
        except:
            pass

    def raise_items(self):
        for item in self.legend_content:
            self.plot.tag_raise(item)
        for item in self.legend_markers:
            self.plot.tag_raise(item)
        for i in range(len(self.plotted_items)):
            for item in self.plotted_items[i]:
                self.plot.tag_raise(item)  

    def __bestFit(self):
        if not self.lineApproximations:
            try: 
                for i in range(3): self.lineApproximations.append(0)
                if self.scale_type[0] == 'lin':  
                    x = self.gen_x_path(50, self.x_boundary[0], self.x_boundary[-1]) 
                elif self.scale_type[0] == 'log':
                    x = self.gen_x_path(50, self.x_boundary[0], self.x_boundary[-1])
                y = [0.1 for i in range(len(x))]
                
                dataset = self.find_dataset('bFit')
                for i in range(len(x)): dataset.addPoint([x[i], y[i]])

                markSize = dataset.getMarkerSize()/2
                colors = self.get_color(dataset)
                num = self.find_dataset('bFit')


                for i in range(len(x)):
                    a = self.scalePoint(dataset.getPoint(i))
                    self.plotted_items[num].append(self.canvas.create_oval(a[0]-markSize,a[1]-markSize,a[0]+markSize,a[1]+markSize, width=0, fill=colors[i]))
            except: 
                pass
        else: self.lineApproximations.clear()
    def __changeA(self, value):
        if len(self.lineApproximations) > 0:
            1
            #self.lineApproximations[0] = float(value)
            #self.plotBestFit()
            #self.plotFun('a', '+', 'b', '*', 'exp', '^', 'c')
    def __changeB(self, value):
        if len(self.lineApproximations) > 0:
            1
            # self.lineApproximations[1] = float(value)
            # self.plotBestFit()
            # self.plotFun('a', '+', 'b', '*', 'exp', '^', 'c')
    def __changeC(self, value):
        if len(self.lineApproximations) > 0:
            1
            # self.lineApproximations[2] = float(value)
            # self.plotBestFit()
            # self.plotFun('a', '+', 'b', '*', 'exp', '^', 'c')

    def __select_item(self):

        if self.plot_editor_selected_counter == 0:
            self.plot_editor_selected_counter = 1
            self.__update_editor_buttons('sel_item', 'txt_input')
        elif self.plot_editor_selected_counter == 1:
            self.plot_editor_selected_counter += 1
            self.__update_editor_buttons('sel_item', 'txt_input')
        else: 
            self.plot_editor_selected_counter = 0
            self.plot.itemconfig(self.plot_editor_selected_item, 
                                   fill = self.fg_color)
            self.plot_editor_selected_item = None
            self.__update_editor_buttons('sel_item', 'txt_input')

    def __set_animation_speed(self, event):
        try: self.animation_speed = int(self.animation_speed_input.get())
        except: pass

    # Add legend.marker to cahnge dataset colors???
    def find_item(self, x, y):
        for itemRow in [self.plotted_text, self.legend_content]:
            for item in itemRow:
                pos = self.plot.bbox(item)
                if x > pos[0] and x < pos[2] and y > pos[1] and y < pos[3]:
                    self.plot_editor_selected_item = item
                    self.plot.itemconfig(self.plot_editor_selected_item, 
                                           fill=self.highlight_colors[0])    
                    self.__select_item()
                    return

    def __select_item_change(self, event):
        if self.plot_editor_selected_item != None:
            self.plot.itemconfig(self.plot_editor_selected_item, 
                                   text=self.select_item_text_input.get())