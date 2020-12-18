from tkinter import *
from PIL import ImageTk,Image
from DataSeries import DataSeries
import math
import numpy as np
import os
from datetime import datetime

class Plot:


    def __init__(self, width, height, window_name, font_size=None, font_type=None):
        
        # Dimensions
        self.screen_width = width
        self.screen_height = height
        self.font_size = 10 if font_size == None else font_size
        self.offset_y = 40 + 4*self.font_size
        self.font = 'helvetica' if font_type == None else font_type
        self.font_type = '%s %d' %(self.font, self.font_size)
        
        # Colors
        self.bg_color = '#E0DFD5'
        self.fg_color = '#313638'
        self.highlight_colors = ['#EF6461', '#9CD08F', '#E4B363', 
                                 '#E8E9EB', '#5C6B73']
        # Red, Green, Yellow, Gray, Slate
        self.default_plot_colors = ['#5FBFF9', '#E85F5C', '#B2FFD6', 
                                    '#F9C784', '#343434', '#613F75']
        self.default_plot_color_counter = 0

        # Enabled Parameters
        self.has_title = False
        self.lock_x_axis = False
        self.has_x_grid = False
        self.lock_y_axis = False
        self.has_y_grid = False
        self.has_x_label = False
        self.has_y_label = False
        self.has_legend = False
        self.has_graph = False
        self.has_colorbar = False

        # Graphical Window
        self.root_window = Toplevel()
        self.root_window.title(window_name)
        self.root_window.geometry('%dx%d'%(self.screen_width, self.screen_height))
        self.root_window.configure(bg=self.bg_color)
        self.root_window.bind('<Configure>', self.resize_screen)


        self.canvas = Canvas(self.root_window, width = self.screen_width, 
                             height = self.screen_height, bg=self.highlight_colors[3], 
                             bd = 0, highlightthickness = 0)
        self.set_canvas_dimensions()
        self.canvas.place(x = 0, y = 0)

        self.plot = Canvas(self.root_window, width = self.plot_dimensions[0], 
                           height = self.plot_dimensions[1], bg='#ffffff', bd=0)
        self.plot.place(x = self.offset_x, y = self.offset_y ,anchor = NW)

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
        self.root_window.bind('<Up>', self.up_arrow_key_command)
        self.root_window.bind('<Down>', self.down_arrow_key_command)
        self.root_window.bind('<Delete>', self.delete_arrow_key_command)

        # Save Locations
        self.file_save_location = os.path.dirname(os.path.realpath(__file__)) \
                + '\\saveData'
        if not os.path.exists(self.file_save_location): 
                os.makedirs(self.file_save_location)

        self.file_image_location = os.path.dirname(os.path.realpath(__file__)) \
                + '\\images'


        """
        rewrite as nicer array of scale factors.... Maybe??
        """
        # Scaling Factors
        self.x_scale_factor = 0
        self.y_scale_factor = 0
        self.scale_type= ['lin', 'lin']
        self.axis_grid_lines = [10, 10]
        self.x_boundary = []
        self.y_boundary = []
        self.scale_unit_style = '{:.2f}'
        self.show_axis_custom = ''
        self.legend_pos = 'NE'

        self.x_axis_numbers = []
        self.y_axis_numbers = []
        self.x_grid_lines = []
        self.y_grid_lines = []
        self.legend_content = []
        self.legend_markers = []
        self.plotted_text = []
        self.plotted_text_tags = []
        self.plotted_text_position = []
        self.data_series = []

        self.color_bar = Canvas(self.root_window, width = 25, 
                           height = self.plot_dimensions[1], 
                           bg=None, highlightthickness=0)
        self.color_bar_text = []

        self.plotted_items = [] # Not in use anymore??? Only currently best fit = broken
        
        # Editing Tools
        self.add_dataset('bFit')
        self.root_window.bind('<e>', self.__open_plot_editor)
        self.editor_window = Toplevel()
        self.editor_window.title('Plot Editor')
        self.editor_window.geometry('750x230')
        self.editor_window.protocol("WM_DELETE_WINDOW", self.__close_editor)
        self.editor_window.withdraw()
        
        self.has_plot_editor = False
        self.plot_editor_selected_counter = 0
        self.plot_editor_selected_item = None
        self.editor_canvas = Canvas(self.editor_window, width = self.screen_width, 
                                    height = 230, bg=self.highlight_colors[3])
        self.editor_canvas.place(x=0, y=0)
        self.generate_plot_editor()

        # Plot Editing Toold
        self.enable_plot_movement()
        self.__add_home_button()
        self.__add_scale_units_button()
        self.__add_datapoint_selector()
        self.datapoints_selection = False
        self.marked_points = []
        self.marked_text = []
        self.marked_objects = []

    # Datasets

    def add_dataset(self, tag):
        """
        Creates a Dataset series with assigned tag if it does not 
        already exist. A dataset is needed for each series that is to be
        plotted
        """
        if self.find_dataset(tag) != None: return
        else: self.data_series.append(DataSeries(tag, self.plot))

    def remove_dataset(self, tag):
        """
        Removes an existing datasets from memory and plotted view
        """
        for i in range(len(self.data_series)):
            if self.data_series[i].get_tag() == tag:
                dataset = self.find_dataset(tag)
                dataset.clear_data()
                self.data_series.pop(i)
                return

    def clear_dataset(self, tag):
        """
        Removes dataset from plotted view but keeps it in memory
        """
        dataset = self.find_dataset(tag)
        if dataset != None: dataset.undraw_item(0)

    def remove_drawn_items(self, search_list):
        """
        Clears plotted content from the window itself
        """
        for item in search_list: self.canvas.delete(int(item))            
        search_list.clear()

    def find_dataset(self, tag):
        """
        Searches and returns the requested dataset
        """
        for item in self.data_series:
            if item.get_tag() == tag: return item

    def find_tag_number(self, tag, search_list):
        """
        Returns index of requested tag in its appropriate list
        """
        for i in range(len(search_list)):
            if search_list[i] == tag: return i


    # Resize Screen    

    def set_canvas_dimensions(self):
        """
        Updates Screen Dimensions to allow for screen resizing
        """
        self.screen_padding_x = 4*self.font_size
        self.offset_x = 2*self.screen_padding_x
        
        canvas_width = self.screen_width-2*self.screen_padding_x
        canvas_height = self.screen_height-2*self.offset_y/3

        self.canvas_boundary = [self.offset_x, self.offset_y, canvas_width, canvas_height]
        self.plot_dimensions = [int(self.canvas_boundary[2]-self.canvas_boundary[0]), 
                                int(self.canvas_boundary[3]-self.canvas_boundary[1])]

    def resize_screen(self, event):
        """
        Handles Resize and scaling of entire window
        """

        screen_size = self.root_window.geometry()
        plus_location = screen_size.find('+')
        x_position = screen_size.find('x')
        
        screen_width = int(screen_size[0:x_position])
        screen_height = int(screen_size[x_position+1:plus_location])

        width_delta = screen_width / self.screen_width
        height_delta = screen_height / self.screen_height

        if width_delta == 1 and height_delta == 1: return
        
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.set_canvas_dimensions()
        self.canvas.config(width = self.screen_width, 
                           height=self.screen_height)

        self.plot.config(width = self.plot_dimensions[0] * width_delta, 
                         height = self.plot_dimensions[1] * height_delta)
        self.plot.place(x = self.offset_x, y = self.offset_y)
        
        self.auto_focus()

        if self.has_colorbar:
            self.color_bar.config(height = self.plot_dimensions[1])
            self.color_bar.place(x = self.canvas_boundary[2] + 10, 
                                 y = self.canvas_boundary[1])
        if self.has_title: 
            self.canvas.moveto(self.title, self.plot_dimensions[0]/2, 
                               self.offset_y/2-2*self.font_size)
        if self.has_y_label: 
            p1 = 2*self.font_size
            p2 = self.canvas_boundary[1] + self.plot_dimensions[1]/2
            self.canvas.moveto(self.y_label, p1, p2)
        if self.has_x_label:
            p1 = self.screen_width/2
            p2 = self.canvas_boundary[3] + 2.5*self.font_size
            self.canvas.moveto(self.x_label, p1, p2)
        if self.has_colorbar:
            self.add_colorbar(self.color_bar_colors[0], 
                              self.color_bar_colors[1])     
            if self.color_bar_text:
                dH = self.plot_dimensions[1]/(len(self.color_bar_text)-1)
                for i in range(len(self.color_bar_text)):
                    self.canvas.moveto(self.color_bar_text[i], 
                                       self.canvas_boundary[2] + 50, 
                                       self.canvas_boundary[3] - i*dH 
                                       - self.font_size)       
        
        self.home_button.place(x = self.canvas_boundary[2] - 5, 
                               y = self.canvas_boundary[1] - 5)
        self.scale_unit_button.place(x = self.canvas_boundary[2] - 45,
                                     y = self.canvas_boundary[1] - 5)
        self.datapoint_selector.place(x = self.canvas_boundary[2] - 85,
                                     y = self.canvas_boundary[1] - 5)

        self.raise_items()        

    # Drag and Drop screen

    def enable_plot_movement(self):
        """
        Adds mouse controll over the graph
        """
        self.plot_drag_mouse_clicked = False
        self.plot_drag_mouse_pos = [0, 0]

        self.plot.bind('<ButtonPress-1>', self.mouse_pressed)
        self.plot.bind('<B1-Motion>', self.mouse_dragged)
        self.plot.bind('<ButtonRelease-1>', self.mouse_released)
        self.plot.bind('<MouseWheel>', self.mouse_scrolled)

    def mouse_pressed(self, event):
        """
        Gets mouse click on plot area
        """
        if self.datapoints_selection == True:
            
            click_x = self.anti_scale_vector(event.x, 'x')
            click_y = self.anti_scale_vector(event.y, 'y')
            closest_point = self.find_datapoint(click_x, click_y)

            if np.linalg.norm(closest_point - [click_x, click_y]) > 2: return
            self.marked_points.append(closest_point)
            self.draw_point_marker()

        else:
            if self.plot_editor_selected_counter != 1:
                self.plot_drag_mouse_clicked = True
                self.plot_drag_mouse_pos = [event.x, event.y]

    def mouse_dragged(self, event):
        """
        Allows for real time moving of the graphed data
        """

        if self.plot_drag_mouse_clicked == True:
            delta_x = ((self.plot_drag_mouse_pos[0] - event.x) 
                            * self.x_scale_factor)
            delta_y = ((event.y - self.plot_drag_mouse_pos[1]) 
                            * self.y_scale_factor)
            
            self.set_x_axis(self.x_boundary[0] + delta_x, 
                            self.x_boundary[-1] + delta_x)
            self.set_y_axis(self.y_boundary[0] + delta_y, 
                            self.y_boundary[-1] + delta_y)

            self.plot_drag_mouse_pos = [event.x, event.y]

    def mouse_released(self, event):
        """
        Disables graph movement and does item placement
        """

        if self.plot_drag_mouse_clicked == True:
            self.plot_drag_mouse_clicked = False

            delta_x = ((self.plot_drag_mouse_pos[0] - event.x) 
                            * self.x_scale_factor)
            delta_y = ((event.y - self.plot_drag_mouse_pos[1]) 
                            * self.y_scale_factor)
            
            self.set_x_axis(self.x_boundary[0] + delta_x, 
                            self.x_boundary[-1] + delta_x, 'drag')
            self.set_y_axis(self.y_boundary[0] + delta_y, 
                            self.y_boundary[-1] + delta_y, 'drag')

            self.update_plots('all')
            self.raise_items()

    def mouse_scrolled(self, event):
        """
        Zoom in and out on graph
        """

        if self.plot_editor_selected_counter != 1:

            # Scroll Location
            pos_x = event.x * self.x_scale_factor
            pos_y = event.y * self.y_scale_factor

            origin_x = (self.x_boundary[-1]-self.x_boundary[0]) / 2
            origin_y = (self.y_boundary[-1]-self.y_boundary[0]) / 2

            displacement_x = pos_x - origin_x
            displacement_y = origin_y - pos_y

            zoom_strength = 5
            zoom_direction = event.delta/120 / zoom_strength
            
            delta_x = (self.x_boundary[-1]-self.x_boundary[0]) * zoom_direction
            delta_y = (self.y_boundary[-1]-self.y_boundary[0]) * zoom_direction

            self.set_x_axis(self.x_boundary[0] + delta_x + displacement_x, 
                        self.x_boundary[-1] - delta_x + displacement_x, 'drag')
            self.set_y_axis(self.y_boundary[0] + delta_y + displacement_y, 
                        self.y_boundary[-1] - delta_y + displacement_y, 'drag')

            self.update_plots('all')


    # Canvas Buttons

    def __add_home_button(self):
        """
        Creates auto focus button on graph
        """

        image_file = self.file_image_location + '\\home.png'
        self.button_image_auto_home = ImageTk.PhotoImage(Image.open(image_file)) 
        self.home_button = Button(self.canvas, width = 30, 
                                height = 35, command=self.auto_focus, 
                                bg = self.bg_color, image = self.button_image_auto_home)
        self.home_button.place(x=self.canvas_boundary[2] - 5,
                               y=self.canvas_boundary[1] - 5, anchor=SE)
        
    def __add_scale_units_button(self):
        """ Allows for manual switching of units on the axis numbers
        self.__scale_unit_iter is default type which is float """
        
        self.__scale_unit_iter = 0
        
        image_file = self.file_image_location + '\\scientific.png'
        self.button_image_axis_unit = ImageTk.PhotoImage(Image.open(image_file)) 
        self.scale_unit_button = Button(self.canvas, width = 30, 
                                height = 35, command=self.change_unit_scale, 
                                bg = self.bg_color, image = self.button_image_axis_unit)
        self.scale_unit_button.place(x=self.canvas_boundary[2] - 45,
                                     y=self.canvas_boundary[1] - 5, anchor=SE)

    def change_unit_scale(self):
        """ Keeps track of which units are printed on the axis
        Sets and updates graph accordingly """
        
        self.__scale_unit_iter += 1
        self.__scale_unit_iter %= 5

        if self.__scale_unit_iter == 0:
            self.show_axis_custom = ''
            tex = 'scientific'
            style = '{:.2f}'
        elif self.__scale_unit_iter == 1:
            tex = 'percent'
            style = '{:.2e}'
        elif self.__scale_unit_iter == 2:
            tex = 'time' #u23F0
            style = '{:.2%}'
        elif self.__scale_unit_iter == 3:
            self.show_axis_custom = 'time'
            tex = 'blank'
            style = '{:.2f}'
            # Add Time
        elif self.__scale_unit_iter == 4:
            self.show_axis_custom = 'blank'
            tex = 'number'
            style = ''

        image_file = self.file_image_location + '\\' + tex + '.png'
        self.button_image_axis_unit = ImageTk.PhotoImage(Image.open(image_file)) 

        self.scale_unit_button.config(image = self.button_image_axis_unit)
        self.scale_unit_style = style
        self.set_axis_numbers(len(self.x_axis_numbers) - 1, 'x')
        self.set_axis_numbers(len(self.y_axis_numbers) - 1, 'y')

    def __add_datapoint_selector(self):
        """ Creates data selection button """

        image_file = self.file_image_location + '\\select.png'
        self.button_image_select_point = ImageTk.PhotoImage(Image.open(image_file)) 
        self.datapoint_selector = Button(self.canvas, width = 30, 
                                height = 35, command=self.select_datapoint, 
                                bg = self.bg_color, image = self.button_image_select_point)
        self.datapoint_selector.place(x=self.canvas_boundary[2] - 85,
                                      y=self.canvas_boundary[1] - 5, anchor=SE)

    def select_datapoint(self):
        if self.datapoints_selection == False:
            self.datapoint_selector.config(bg=self.highlight_colors[2])
            self.datapoints_selection = True
        else:
            self.datapoint_selector.config(bg=self.bg_color)
            self.datapoints_selection = False

    def find_datapoint(self, x, y):
        
        shortest_distance = math.inf
        for item in self.data_series:
            if item.get_tag() != 'bFit': 
                points = np.array(item.get_points())
                delta_x = points[0,:] - x
                delta_y = points[1,:] - y
                length = np.zeros(np.size(delta_x))
                for i in range(np.size(delta_x)):
                    length[i] = np.sqrt(delta_x[i]**2 + delta_y[i]**2)
                if np.min(length) < shortest_distance: 
                    shortest_distance = np.min(length)
                    best_index = np.argmin(length)
                    best_point = points[:, best_index]
        return best_point

    def draw_point_marker(self):

        position = self.marked_points[-1]
        scaled_pos = [self.scale_vector(position[0], 'x'), 
                      self.scale_vector(position[1], 'y')]
        
        p1 = scaled_pos[0] - 3
        p2 = scaled_pos[1] - 3
        p3 = scaled_pos[0] + 3
        p4 = scaled_pos[1] + 3

        self.marked_objects.append(self.plot.create_oval(p1, p2, p3, p4))
        self.marked_text.append(self.plot.create_text(
                    [scaled_pos[0] + 5, scaled_pos[1]], fill=self.fg_color, 
                    font=self.font_type, anchor=W, text=position))

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
        """
        Adds dataset if it does not exist and then 
        sets color of specified dataset
        """
        dataset = self.find_dataset(tag)
        if dataset != None: 
            self.add_dataset(tag)
            dataset = self.find_dataset(tag)
        dataset.set_color(color)

    def set_line_width(self, lineWidth, tag):
        """
        Adds dataset if it does not exist and then 
        sets width of specified dataset lines
        """

        dataset = self.find_dataset(tag)
        if dataset != None: 
            self.add_dataset(tag)
            dataset = self.find_dataset(tag)
        dataset.set_line_width(lineWidth)

    def set_dot_size(self, size, tag):
        """
        Adds dataset if it does not exist and then 
        sets size of specified datasets scatter points
        """

        dataset = self.find_dataset(tag)
        if dataset != None: 
            self.add_dataset(tag)
            dataset = self.find_dataset(tag) 
        dataset.set_dot_size(size)

    # Plot Text

    def set_title(self, text):
        """ Sets/Updates title, Text = conent """
        if self.has_title == False:
            self.has_title = True
            self.title = self.canvas.create_text(self.plot_dimensions[0]/2, 
                        self.offset_y/2-2*self.font_size, font='%s %d' %(self.font, 2*self.font_size), 
                        text = text, fill=self.fg_color, anchor=NW)
        else: self.canvas.itemconfig(self.title, text = text)         

    def add_text(self, position, text, tag):
        """ Sets text on graph: Position = [x, y], Text = content, Tag = reference  """
        self.plotted_text_position.append(position)
        scaled_pos = [self.scale_vector(position[0], 'x'), 
                      self.scale_vector(position[1], 'y')]
        self.plotted_text.append(self.plot.create_text(scaled_pos, anchor=NW,
                      font=self.font_type, text=text, fill=self.fg_color))
        self.plotted_text_tags.append(tag)

    def update_text(self, text, tag):
        """ Updates existing text on graph, Text = content, Tag = reference """
        text_item = self.find_tag_number(tag, self.plotted_text_tags)
        if text_item != None:
            self.plot.itemconfig(self.plotted_text[text_item], text = text)
            return

    def find_text(self, content):
        """ Returns index of text item, Content = widget to search"""
        text = self.plot.itemcget(content, 'text')
        for i in range(len(self.plotted_text)):
            if self.plot.itemcget(self.plotted_text[i], 'text') == text:
                return i    


    # Axis

    def auto_focus(self, *args):
        """
        Estimates a good x and y scale for the plotted data by
        finding the min/max x/y for all data
        """
        first_data_serie = True

        for item in self.data_series:
            if item.get_tag() != 'bFit': 
                points = np.array(item.get_points())

                if first_data_serie == True:
                    first_data_serie = False

                    min_x = np.min(points[0,:])
                    max_x = np.max(points[0,:])
                    min_y = np.min(points[1,:])
                    max_y = np.max(points[1,:])
                else:
                    if np.min(points[0,:]) < min_x: min_x = np.min(points[0,:])
                    if np.max(points[0,:]) < max_x: max_x = np.max(points[0,:])
                    if np.min(points[1,:]) < min_y: min_y = np.min(points[1,:])
                    if np.max(points[1,:]) < max_y: max_y = np.max(points[1,:])
        
        if min_x != max_x: delta_x = (max_x - min_x) / 10
        else: delta_x = 2
        if min_y != max_y: delta_y = (max_y - min_y) / 10
        else: delta_y = 2

        # Used by log axis to auto set when changing lin/log
        for name in args:
            if   name == 'axis_x': return [min_x - delta_x, max_x + delta_x]
            elif name == 'axis_y': return [min_y - delta_y, max_y + delta_y]

        self.set_x_axis(min_x - delta_x, max_x + delta_x, 'drag')
        self.set_y_axis(min_y - delta_y, max_y + delta_y, 'drag')
        self.update_plots('all')

    def set_labels(self, textx, texty):
        """ Sets/Updates axis labels, Textx = X Label, Texty = Y Label """
        if self.has_x_label == False:
            self.has_x_label = True
            p1 = self.screen_width/2
            p2 = self.canvas_boundary[3] + 2.5*self.font_size
            self.x_label = self.canvas.create_text(p1, p2, font=self.font_type,
                                    text = textx, fill=self.fg_color, anchor=NW)
        elif textx != 'keep': self.canvas.itemconfig(self.x_label, text=textx)

        if self.has_y_label == False:
            self.has_y_label = True
            p1 = 2*self.font_size
            p2 = self.canvas_boundary[1] + self.plot_dimensions[1]/2
            self.y_label = self.canvas.create_text(p1, p2, font=self.font_type, 
                                    angle=90, text = texty, fill=self.fg_color,
                                    anchor=NE)
        elif texty != 'keep': self.canvas.itemconfig(self.y_label, text=texty)

    def set_zero(self, start, end, order):
        """
        Finds the position of 0 used by linear graphs as an additive factor
        """

        if order == 'x': plot_dim = self.plot_dimensions[0]; numerator = start
        elif order == 'y': plot_dim = self.plot_dimensions[1]; numerator = end
        common_term = plot_dim/(start - end)
        abs_term = abs(numerator)/(abs(start) + abs(end))

        if order == 'x':
            if end < 0: self.x0 = common_term * end
            elif start > 0: self.x0 = common_term * start
            else: self.x0 = abs_term * plot_dim
        elif order == 'y':
            if end < 0: self.y0 = common_term*abs(end)
            elif start > 0: self.y0 = -common_term*start + plot_dim
            else: self.y0 = abs_term * plot_dim

    def set_x_axis(self, x_start, x_end, *args):
        """ Sets X-Axis, Args: Keep = keeps axis, Lock = locks axis, Log = Log Axis,
        Lin = Lin Axis, Show = show gridlines, Hidden = hide gridlines """

        update_plot = True
        auto_focus = False

        if x_start == 'keep': x_start = self.x_boundary[0]
        if x_end == 'keep': x_end = self.x_boundary[-1]

        for name in args:
            if name == 'graph':
                auto_focus = True
                if self.lock_x_axis: return
                if self.x_boundary:
                    cond1 = x_start > self.x_boundary[0]
                    cond2 = x_end < self.x_boundary[-1]
                    if cond1 and cond2 : return
                    else:
                        if x_start > self.x_boundary[0]: 
                            x_start = self.x_boundary[0]
                        if x_end < self.x_boundary[-1]: 
                            x_end = self.x_boundary[-1]
            elif name == 'lock': self.lock_x_axis = True
            elif name == 'log': self.scale_type[0] = 'log'
            elif name == 'lin': self.scale_type[0] = 'lin'
            elif name == 'show': self.has_x_grid = True
            elif name == 'hidden': self.has_x_grid = False
            elif isinstance(name, int): self.axis_grid_lines[0] = name
            elif name == 'drag': update_plot = False
        
        num_ticks = self.axis_grid_lines[0]
        if num_ticks == 0: num_ticks = 1 

        if auto_focus == True: x_start, x_end = self.auto_focus('axis_x')
        if x_start > x_end: x_start, x_end = x_end, x_start
        self.set_zero(x_start, x_end, 'x')   
        
        self.x_boundary.clear()
        if self.scale_type[0] == 'lin':
            self.x_scale_factor = (x_end-x_start)/self.plot_dimensions[0]
            valueSize = (x_end-x_start)/num_ticks
            for i in range(num_ticks+1):
                self.x_boundary.append(x_start + i*valueSize)
            
        elif self.scale_type[0] == 'log':
            
            if x_start <= 0: x_start, x_end = self.log_scale('axis_x')
            self.x_scale_factor = (x_end-x_start)/self.plot_dimensions[0]
            k = (x_start-x_end)/(math.log10(x_start)-math.log10(x_end))
            c = x_end - k * math.log10(x_end)
            self.x_log_scale = [k, c]

            num_ticks = round(math.log10(x_end/x_start))

            for i in range(num_ticks+1):
                self.x_boundary.append(x_end * 10**(-num_ticks+i))
        
        self.set_axis_numbers(num_ticks, 'x')

        if self.has_x_grid == True: self.set_grid_lines('x', num_ticks)
        elif self.has_x_grid == False: self.remove_grid_lines('x')
        
        if update_plot: self.update_plots('all')

    def set_y_axis(self, y_start, y_end, *args):
        """ Sets Y-Axis, Args: Keep = keeps axis, Lock = locks axis, Log = Log Axis,
        Lin = Lin Axis, Show = show gridlines, Hidden = hide gridlines """

        update_plot = True
        auto_focus = False

        if y_start == 'keep': y_start = self.y_boundary[0]
        if y_end == 'keep': y_end = self.y_boundary[-1]

        for name in args:
            if name == 'graph':
                auto_focus = True
                if self.lock_y_axis == True: return
                if self.y_boundary:
                    cond1 = y_start > self.y_boundary[0]
                    cond2 = y_end < self.y_boundary[-1]
                    if cond1 and cond2: return
                    else:
                        if y_start > self.y_boundary[0]: 
                            y_start = self.y_boundary[0]
                        if y_end < self.y_boundary[-1]: 
                            y_end = self.y_boundary[-1]
            elif name == 'lock': self.lock_y_axis = True
            elif name == 'log': self.scale_type[1] = 'log'
            elif name == 'lin': self.scale_type[1] = 'lin'
            elif name == 'show': self.has_y_grid = True
            elif name == 'hidden': self.has_y_grid = False
            elif isinstance(name, int): self.axis_grid_lines[1] = name
            elif name == 'drag': update_plot = False

        num_ticks = self.axis_grid_lines[1]
        if num_ticks == 0: num_ticks = 1 

        if auto_focus == True: y_start, y_end = self.auto_focus('axis_y')
        if y_start > y_end: y_start, y_end = y_end, y_start
        self.set_zero(y_start, y_end, 'y')   

        self.y_boundary.clear()
        if self.scale_type[1] == 'lin':
            self.y_scale_factor = (y_end-y_start)/self.plot_dimensions[1]

            valueSize = (y_end-y_start)/num_ticks

            for i in range(num_ticks+1):
                self.y_boundary.append(y_start + i*valueSize)

        elif self.scale_type[1] == 'log':
            
            if y_start <= 0: y_start, y_end = self.log_scale('axis_y')
            self.y_scale_factor = (y_end-y_start)/self.plot_dimensions[1]
            k = (y_start-y_end)/(math.log10(y_start)-math.log10(y_end))
            c = y_end - k * math.log10(y_end)
            self.y_log_scale = [k, c]

            num_ticks = round(math.log10(y_end/y_start))

            for i in range(num_ticks+1):
                self.y_boundary.append(y_end * 10**(-num_ticks+i))

        self.set_axis_numbers(num_ticks, 'y')
        if self.has_y_grid == True: self.set_grid_lines('y', num_ticks)
        elif self.has_y_grid == False: self.remove_grid_lines('y')

        if update_plot: self.update_plots('all')

    def set_axis_numbers(self, num_ticks, order):
        """
        Called on to update axis numbers to viually 
        show where data is located
        """

        if order == 'x':
            if self.show_axis_custom == 'blank':
                for item in self.x_axis_numbers: self.canvas.delete(item)
                return
            self.remove_drawn_items(self.x_axis_numbers)
            step_size = self.plot_dimensions[0]/num_ticks
            for i in range(num_ticks + 1):
                pos = [self.canvas_boundary[0] + i*step_size, 
                       self.canvas_boundary[3] + self.font_size/2]
                if self.show_axis_custom == 'time':
                    hour = int(self.x_boundary[i]%24)
                    minute = int(60*(self.x_boundary[i]%24 
                              - hour))
                    tex = str(hour).zfill(2) + ':' + str(minute).zfill(2)
                else: tex = self.scale_unit_style.format(self.x_boundary[i])
                self.x_axis_numbers.append(self.canvas.create_text(pos, 
                                            anchor=N, fill=self.fg_color, 
                                            font=self.font_type, text=tex))
        elif order == 'y':
            if self.show_axis_custom == 'blank':
                for item in self.y_axis_numbers: self.canvas.delete(item)
                return
            self.remove_drawn_items(self.y_axis_numbers)
            step_size = self.plot_dimensions[1]/num_ticks
            for i in range(num_ticks + 1):
                pos = [self.canvas_boundary[0] - self.font_size/2, 
                       self.canvas_boundary[3] - i*step_size]
                tex = self.scale_unit_style.format(self.y_boundary[i])
                self.y_axis_numbers.append(self.canvas.create_text(pos, 
                                            anchor=E, fill=self.fg_color, 
                                            font=self.font_type, text=tex))

    def log_scale(self, order):
        """
        Called upon to estimate a good plot focus for log graphs
        Estimates by rounding data to nearest power of 10
        """
        data_low, data_high = self.auto_focus(order)
        power_low = round(math.log10(abs(data_low)))
        power_high = round(math.log10(abs(data_high)))

        if order == 'axis_x': return [10**(-power_low), 10**power_high]
        elif order =='axis_y': return [10**power_low, 10**power_high]

    def set_axis_scale_type(self, *args):
        """
        Automatically Sets scale type:
        Options: digit, e, %, time, ''
        """
        for name in args:

            if name == 'digit': self.__scale_unit_iter = 4
            elif name == 'e': self.__scale_unit_iter = 0
            elif name == '%': self.__scale_unit_iter = 1
            elif name == '\u231A': self.__scale_unit_iter = 2
            elif name == '': self.__scale_unit_iter = 3
            else: return

            self.change_unit_scale()
            return
            

    # Grid Lines

    def __grid_x(self, num_ticks):
        """
        Adds x gridlines to plot
        """
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
        """
        Adds y gridlines to plot
        """

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
        """ Sets requested gridlines """
        
        if not isinstance(num_ticks, int):
            if not num_ticks.isnumeric(): return
            else: num_ticks = int(num_ticks)
        if num_ticks == 0: num_ticks = 1

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
        """
        Removes requested gridlines
        """
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

    def set_legend(self, pos):

        self.has_legend = True
        
        names, colors = [], []
        for dataset in self.data_series:
            if dataset.get_legend() != None:
                names.append(dataset.get_legend())
                colors.append(dataset.get_color())

        if pos == 'NE': self.legend_pos = 'NE'
        elif pos == 'NW': self.legend_pos = 'NW'
        elif pos == 'SE': self.legend_pos = 'SE'
        elif pos == 'SW': self.legend_pos = 'SW'

        text_length = len(max(names, key=len))
        if pos[0]   == 'N': self.legend_y_offset = self.font_size
        if pos[0]   == 'S': self.legend_y_offset = (self.plot_dimensions[1] 
                                                    - len(names)*2*self.font_size)
        if pos[1]   == 'W': self.legend_x_offset = 2*self.font_size
        elif pos[1] == 'E': self.legend_x_offset = (self.plot_dimensions[0] 
                                                    - text_length*self.font_size)

        for i in range(len(names)): self.add_to_legend(names[i], colors[i])

    def add_to_legend(self, name, color):

        i = len(self.legend_content)
        self.legend_content.append(self.plot.create_text(self.legend_x_offset,
                            self.legend_y_offset + 2*i*self.font_size, anchor=NW, 
                            fill=self.fg_color, font=self.font_type, 
                            text=name))
                
        p1 = self.legend_x_offset-3/2*self.font_size
        p2 = self.legend_y_offset + (2*i+1/4)*self.font_size
        p3 = self.legend_x_offset-1/2*self.font_size
        p4 = self.legend_y_offset + (2*i+5/4)*self.font_size
        self.legend_markers.append(self.plot.create_oval(
                            p1, p2, p3, p4, fill=color))

    def update_legend(self, names):
        for i in range(len(names)):
            self.plot.itemconfig(self.legend_content[i], text=names[i])

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
            
    def anti_scale_vector(self, data, *args):

        data = np.array(data)

        for name in args:
            if name == 'x':
                if self.scale_type[0] == 'log': 
                    return 10**((data * self.x_scale_factor 
                                - self.x_log_scale[1]) / self.x_log_scale[0])
                elif self.scale_type[0] == 'lin':
                    return (data-self.x0) * self.x_scale_factor
            elif name == 'y':
                if self.scale_type[1] == 'log':
                    return 10**((data * self.y_scale_factor 
                                - self.y_log_scale[1]) / self.y_log_scale[0])
                elif self.scale_type[1] == 'lin':
                    return (self.y0 - data) * self.y_scale_factor
            
    def get_scale_factor(self):
        return [self.x_scale_factor, self.y_scale_factor]

    # Plot Data

    def graph(self, x, y, tag, *args, legend=None):
        """
        Args: legend=, line, scatter, animate, log, show
        """
        self.has_graph = True

        dataset = self.find_dataset(tag)
        if dataset == None: 
            self.add_dataset(tag)
            dataset = self.find_dataset(tag)

        # Plotting Parameters
        plot_range = range(np.size(x))
        plot_type = 'line'
        grid_state = False
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
            elif name == 'show': grid_state = True
        
        if legend != None: dataset.set_legend(legend)

        dataset.add_points(x,y)
        self.auto_focus()
        dataset.add_scaled_points(self.scale_vector(x, 'x'), 
                                  self.scale_vector(y, 'y'))
        if grid_state == True: self.set_grid_lines('xy', 10)

        if dataset.is_colored() == False:
            dataset.set_color(self.default_plot_colors[self.default_plot_color_counter])
            self.next_plot_color()
        
        dataset.set_plot_type(plot_type)
        dataset.draw(plot_range)

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
                    point = dataset.get_points()
                    new_x = self.scale_vector(point[0,:], 'x')
                    new_y = self.scale_vector(point[1,:], 'y')
                    if dataset.is_animated() == True: 
                        new_index = self.animationScrollbar.get()
                    else: new_index = 0
                    dataset.update_item(new_x, new_y, new_index)
            for i in range(len(self.plotted_text)):      
                self.update_text_pos(i)
            for i in range(len(self.marked_points)):
                position = self.marked_points[i]
                scaled_pos = [self.scale_vector(position[0], 'x'), 
                              self.scale_vector(position[1], 'y')]
                self.plot.moveto(self.marked_objects[i], scaled_pos[0] - 3, 
                                scaled_pos[1] - 3)
                self.plot.moveto(self.marked_text[i], scaled_pos[0] + 5, 
                                scaled_pos[1] - 7)

    def update_text_pos(self, i):
        position = self.plotted_text_position[i]
        scaled_pos = [self.scale_vector(position[0], 'x'), 
                      self.scale_vector(position[1], 'y')]
        self.plot.moveto(self.plotted_text[i], scaled_pos[0], 
                         scaled_pos[1])

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
        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            x_scale = (self.x_boundary[-1]-self.x_boundary[0])/100
            self.plotted_text_position[txt_index][0] += x_scale
            self.update_text_pos(txt_index)
            
        elif self.has_animation == True:
            self.animationScrollbar.set(self.animationScrollbar.get()
                                        + self.animation_speed)

    def left_arrow_key_command(self, event):
        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            x_scale = (self.x_boundary[-1]-self.x_boundary[0])/100
            self.plotted_text_position[txt_index][0] -= x_scale
            self.update_text_pos(txt_index)
        elif self.has_animation == True:
            self.animationScrollbar.set(self.animationScrollbar.get() 
                                        - self.animation_speed)
    
    def up_arrow_key_command(self, event):
        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            y_scale = (self.y_boundary[-1]-self.y_boundary[0])/100
            self.plotted_text_position[txt_index][1] += y_scale
            self.update_text_pos(txt_index)
    
    def down_arrow_key_command(self, event):
        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            y_scale = (self.y_boundary[-1]-self.y_boundary[0])/100
            self.plotted_text_position[txt_index][1] -= y_scale
            self.update_text_pos(txt_index)

    def delete_arrow_key_command(self, event):
        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            self.plot.delete(self.plotted_text[txt_index])
            self.plotted_text.pop(txt_index)
            self.plotted_text_tags.pop(txt_index)
            self.plotted_text_position.pop(txt_index)
            self.__select_item()

    # Markers

    def set_markerbar(self, size_array, tag):
        dataset = self.find_dataset(tag)
        if dataset == None: 
            self.add_dataset(tag)
            dataset = self.find_dataset(tag)
        dataset.set_markerbar(size_array)

    def update_markers(self, tag):
        dataset = self.find_dataset(tag)
        if dataset == None: return
        dataset.update_markers()
    
    # Colors

    def next_plot_color(self): 
        self.default_plot_color_counter +=1
        self.default_plot_color_counter %= len(self.default_plot_colors)

    def get_color(self, dataset):
        colors = dataset.get_color()
        data_range = range(dataset.getNumberOfPoints())
        if isinstance(colors, str): 
            colors = [dataset.get_color() for n in data_range]
        return colors

    def update_colors(self, tag):
        dataset = self.find_dataset(tag)
        if dataset == None: return
        dataset.update_colors()

    def set_colorbar(self, color_array, tag):
        dataset = self.find_dataset(tag)
        if dataset == None: 
            self.add_dataset(tag)
            dataset = self.find_dataset(tag)
        dataset.set_colorbar(color_array)

    def add_colorbar(self, color_start, color_end, *args):   

        self.color_bar.place(x = self.canvas_boundary[2] + 10, 
                             y = self.canvas_boundary[1])
        self.has_colorbar = True
        self.color_bar.delete('all')
        self.color_bar_colors = [color_start, color_end]

        limit = self.plot_dimensions[1]

        (r1,g1,b1) = self.color_bar.winfo_rgb(color_start)
        (r2,g2,b2) = self.color_bar.winfo_rgb(color_end)

        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit

        i_vec = np.arange(0, limit)
        nr = (i_vec*r_ratio + r1).astype(int)
        ng = (i_vec*g_ratio + g1).astype(int)
        nb = (i_vec*b_ratio + b1).astype(int)

        self.colorbar_colors = np.empty(limit, dtype='S13')
        for i in range(limit):
            self.colorbar_colors[i] = "#%4.4x%4.4x%4.4x" % (nr[i],ng[i],nb[i])
            self.color_bar.create_line(0,i,25,i, fill=self.colorbar_colors[i])

        if args:
            dH = self.plot_dimensions[1]/(len(args[0])-1)
            for i in range(len(args[0])):

                scaled_pos = [self.canvas_boundary[2] + 50, self.canvas_boundary[3] - i*dH - self.font_size]
                self.color_bar_text.append(self.canvas.create_text(scaled_pos, anchor=NW,
                    font=self.font_type, text=args[0][i], fill=self.fg_color))

    def get_colorbar(self): 
        return np.flip(self.colorbar_colors)

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
            if dataset == None: return

            cur_time = str(datetime.now().time())[0:8]
            cur_time = cur_time.replace(':', '_')
            
            data_name = self.file_save_location + '\\' + str(i) + '_' + cur_time
            data = dataset.get_points()
            np.save(data_name, data, allow_pickle=True, fix_imports=True)
    
    def load_data(self):

        tag = self.om_load_variable.get()
        if tag == '': return 

        data_name = self.file_save_location + '\\' + str(tag)
        if os.path.exists(data_name):
            
            self.add_dataset(tag)
            dataset = self.find_dataset(tag)
            dataset.set_color(self.load_data_color)

            data = np.load(data_name)    
            self.graph(data[0,:], data[1,:], str(tag), self.load_data_type)

            if self.load_data_legend: self.add_to_legend(tag, self.load_data_color)


    # Plot Editor

    def __open_plot_editor(self, event):
        if self.has_plot_editor == False:
            self.update_editor()
            self.has_plot_editor = True
            self.editor_window.deiconify()

    def __close_editor(self):
        if self.has_plot_editor == True:
            self.has_plot_editor = False
            self.editor_window.withdraw()

    def update_editor(self):
        self.__update_editor_buttons('x_grid', 'y_grid', 'x_linlog','y_linlog', 
                                    'txt_input', 'animation_speed', 'save_data', 
                                    'load_data')

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
        self.x_scale_steps.bind("<Return>", lambda event: 
                                self.set_grid_lines('x', self.x_scale_steps.get()))
        
        image_file = self.file_image_location + '\\on.png'
        self.button_image_on = ImageTk.PhotoImage(Image.open(image_file)) 
        self.x_grid_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__enable_grid('x'), 
                    bg=self.highlight_colors[1], image=self.button_image_on)
        self.x_grid_button.place(x=145,y=70, anchor=NW)

        image_file = self.file_image_location + '\\lin.png'
        self.button_image_linlog_x = ImageTk.PhotoImage(Image.open(image_file)) 
        self.x_linlog_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__switch_linlog('x'), bg=self.bg_color, 
                    image=self.button_image_linlog_x)
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
                                self.set_grid_lines('y', self.y_scale_steps.get()))

        self.y_grid_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__enable_grid('y'), 
                    bg=self.highlight_colors[1], image=self.button_image_on)
        self.y_grid_button.place(x=145,y=160, anchor=NW)
        
        image_file = self.file_image_location + '\\lin.png'
        self.button_image_linlog_y = ImageTk.PhotoImage(Image.open(image_file)) 
        self.y_linlog_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__switch_linlog('y'), bg=self.bg_color, 
                    image=self.button_image_linlog_y)
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
        self.select_item_text_input.place(x=230,y=96, anchor=NW)
        self.__add_focus_listeners(self.select_item_text_input)
        self.select_item_text_input.bind("<Return>", self.__select_item_change)

        self.select_item_button = Button(self.editor_canvas, text='Select Item', 
                        bg=self.bg_color, width = 8, command=self.__select_item)
        self.select_item_button.place(x= 360, y = 92)

        # Animation
        self.editor_canvas.create_text(230, 130, anchor=W, text='Animation')
        self.editor_canvas.create_line(230,136,420,136)

        self.animation_speed_input = Entry(self.editor_canvas, fg='gray')
        self.animation_speed_input.insert(0, 'Animation Speed')
        self.animation_speed_input.place(x=230,y=142, anchor=NW)
        self.__add_focus_listeners(self.animation_speed_input)
        self.animation_speed_input.bind("<Return>", self.__set_animation_speed)

        # Save Data
        self.editor_canvas.create_text(450, 10, anchor=W, text='Save Data')
        self.editor_canvas.create_line(450,16,680,16)

        self.om_save_variable = StringVar()
        self.om_save_variable.trace('w', self.__update_save_tag)
        self.save_data_tag_selector = OptionMenu(self.editor_canvas, 
                                            self.om_save_variable, '')
        self.save_data_tag_selector.config(bg=self.bg_color, width=1, font='bold')                                            
        self.save_data_tag_selector.place(x=580, y=22)

        image_file = self.file_image_location + '\\save.png'
        self.button_image_save_data = ImageTk.PhotoImage(Image.open(image_file)) 
        self.save_data_button = Button(self.editor_canvas, width=30, height=35, 
                                command=lambda: self.save_data(self.om_save_variable.get()), 
                                bg=self.bg_color, image=self.button_image_save_data)
        self.save_data_button.place(x=640,y=22, width=40, anchor=NW)

        self.save_data_name_color = self.editor_canvas.create_oval(450, 36, 458, 44, state='hidden')
        self.save_data_name_selection = self.editor_canvas.create_text(465, 40, anchor=W, text='')

        # Load Data
        self.editor_canvas.create_text(450, 62, anchor=W, text='Load Data')
        self.editor_canvas.create_line(450,68,680,68)

        self.om_load_variable = StringVar()
        self.om_load_variable.trace('w', self.__update_load_tag)
        self.load_data_tag_selector = OptionMenu(self.editor_canvas, 
                                            self.om_load_variable, '')
        self.load_data_tag_selector.config(bg=self.bg_color, width=1, font='bold')                                            
        self.load_data_tag_selector.place(x=580, y=74)

        image_file = self.file_image_location + '\\load.png'
        self.button_image_load_data = ImageTk.PhotoImage(Image.open(image_file)) 
        self.load_data_button = Button(self.editor_canvas, width=30, height=35, 
                                command=lambda:self.load_data(), 
                                bg=self.bg_color, image=self.button_image_load_data)
        self.load_data_button.place(x=640,y=74, width=40, anchor=NW)

        self.load_data_name_selection = self.editor_canvas.create_text(465, 128, anchor=W, text='')

        # Load Selections

        image_file = self.file_image_location + '\\scatter.png'
        self.load_data_type = 'scatter'
        self.button_image_data_type = ImageTk.PhotoImage(Image.open(image_file)) 
        self.load_data_type_button = Button(self.editor_canvas, width = 30, 
                                height = 35, command=self.__change_plot_type, 
                                bg = self.bg_color, image = self.button_image_data_type)
        self.load_data_type_button.place(x=450,y=74, anchor=NW)

        index = self.default_plot_color_counter
        self.load_data_color = self.default_plot_colors[index]
        self.load_data_color_button = Button(self.editor_canvas, width = 3, 
                                height = 2, command=self.__change_plot_color, 
                                bg = self.load_data_color)
        self.load_data_color_button.place(x=490,y=74, anchor=NW)

        image_file = self.file_image_location + '\\legend.png'
        self.load_data_legend = True
        self.button_image_legend = ImageTk.PhotoImage(Image.open(image_file)) 
        self.load_data_legend_button = Button(self.editor_canvas, width = 30, 
                                height = 35, command=self.__change_plot_legend, 
                                bg = self.highlight_colors[1], image=self.button_image_legend)
        self.load_data_legend_button.place(x=525, y=74, anchor=NW)
        

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
                x_grid_color = self.highlight_colors[1] if self.has_x_grid == True else self.highlight_colors[0]
                self.x_grid_button.config(bg=x_grid_color)
                if self.scale_type[0] == 'log': self.x_scale_steps.config(state='disabled')
                elif self.scale_type[0] == 'lin': self.x_scale_steps.config(state='normal')
            elif button == 'y_grid':
                y_grid_color = self.highlight_colors[1] if self.has_y_grid == True else self.highlight_colors[0]
                self.y_grid_button.config(bg=y_grid_color)
                if self.scale_type[1] == 'log': self.y_scale_steps.config(state='disabled')
                elif self.scale_type[1] == 'lin': self.y_scale_steps.config(state='normal')
            elif button == 'x_linlog':              
                if self.scale_type[0] == 'lin':
                    image_file = self.file_image_location + '\\lin.png'
                elif self.scale_type[0] == 'log':
                    image_file = self.file_image_location + '\\log.png'
                self.button_image_linlog_x = ImageTk.PhotoImage(Image.open(image_file)) 
                self.x_linlog_button.config(image=self.button_image_linlog_x)
            elif button == 'y_linlog': 
                if self.scale_type[1] == 'lin':
                    image_file = self.file_image_location + '\\lin.png'
                elif self.scale_type[1] == 'log':
                    image_file = self.file_image_location + '\\log.png'
                self.button_image_linlog_y = ImageTk.PhotoImage(Image.open(image_file)) 
                self.y_linlog_button.config(image=self.button_image_linlog_y)
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
            elif button == 'save_data':
                menu = self.save_data_tag_selector['menu']
                menu.delete(0, 'end')
                for item in self.data_series: 
                    data_tag = item.get_tag()
                    menu.add_command(label=data_tag, 
                                    command=lambda value=data_tag: 
                                    self.om_save_variable.set(value))
            elif button == 'load_data':
                menu = self.load_data_tag_selector['menu']
                menu.delete(0, 'end')
                with os.scandir(self.file_save_location) as dirs:
                    for entry in dirs:
                        menu.add_command(label=entry.name, 
                                        command=lambda value=entry.name: 
                                        self.om_load_variable.set(value))

    def __update_save_tag(self, *args):
        
        tag = self.om_save_variable.get()
        tag_color = self.find_dataset(tag).get_color()

        self.editor_canvas.itemconfig(self.save_data_name_selection, text=tag)
        self.editor_canvas.itemconfig(self.save_data_name_color, fill=tag_color, state='normal')
        self.om_save_variable.set(tag)

    def __update_load_tag(self, *args):
        
        tag = self.om_load_variable.get()
        self.editor_canvas.itemconfig(self.load_data_name_selection, text=tag)

    def __change_plot_type(self):

        data_type = 'scatter' if self.load_data_type == 'line' else 'line'

        self.load_data_type = data_type
        scatter_file = self.file_image_location + '\\' + data_type + '.png'
        self.button_image_data_type = ImageTk.PhotoImage(Image.open(scatter_file)) 
        self.load_data_type_button.config(image = self.button_image_data_type)

    def __change_plot_color(self):
        
        index = self.default_plot_color_counter
        self.next_plot_color()
        self.load_data_color = self.default_plot_colors[index]
        self.load_data_color_button.config(bg = self.load_data_color)

    def __change_plot_legend(self):
        
        color_index = 0 if self.load_data_legend == True else 1
        self.load_data_legend = color_index
        self.load_data_legend_button.config(bg=self.highlight_colors[color_index])

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
        self.auto_focus()
        self.update_plots('all')
        self.__update_editor_buttons('x_grid', 'x_linlog', 
                                    'y_grid', 'y_linlog')
        
    def __enable_grid(self, order):
        if order =='x':
            if self.has_x_grid == True: self.remove_grid_lines(order)
            else: self.set_grid_lines(order, self.axis_grid_lines[0])
        if order =='y':
            if self.has_y_grid == True: self.remove_grid_lines(order)
            else: self.set_grid_lines(order, self.axis_grid_lines[1])
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