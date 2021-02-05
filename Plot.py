from tkinter import *
import tkinter.font as tkFont
from PIL import ImageTk, Image
from DataSeries import DataSeries
from PlotTools import Grid, Axis_Numbers
import math
import numpy as np
import os
import re
from datetime import datetime

class Plot:

    def __init__(self, width=None, height=None, name=None, 
                       font_size=None, font_type=None, debug=False):

        # Save Locations
        self.file_save_location = os.path.dirname(os.path.realpath(__file__)) \
                + '\\saveData'
        if not os.path.exists(self.file_save_location): 
                os.makedirs(self.file_save_location)

        self.file_image_location = os.path.dirname(os.path.realpath(__file__)) \
                + '\\images'


        # Debugging
        self.debug = False
        if debug != False:
            self.debug = True

            self.file_debug_location = os.path.dirname(os.path.realpath(__file__)) \
                + '\\logData'
            if not os.path.exists(self.file_debug_location): 
                os.makedirs(self.file_debug_location)

            cur_time = str(datetime.now().time())[0:8]
            cur_time = cur_time.replace(':', '_')

            self.file_debug = self.file_debug_location + '\\' + 'log_' + cur_time + '.txt'
            self.debug_log('Debug log for %s \n' %cur_time)
            self.debug_log('Starting PlottingUtils in debugging mode')
            self.debug_log('------------------------------------------')
            print('\n Running PlottingUtils in debugging mode - see generated log for more info \n')

        
        # Dimensions
        self.screen_width = width if width != None else 1000
        self.screen_height = height if height != None else 800

        
        # Text Info
        self.font_size = font_size if isinstance(font_size, int) else 10
        self.font = 'helvetica' if font_type == None else font_type
        self.default_font = tkFont.nametofont('TkDefaultFont')
        self.default_font.configure(family=self.font, size=self.font_size)
        self.title_font = tkFont.Font(family=self.font, size=2*self.font_size)
        self.editor_font = tkFont.Font(family='helvetica', size=9)
        
        # Colors
        self.bg_color = '#E0DFD5'
        self.fg_color = '#313638'
        self.highlight_colors = ['#EF6461', '#9CD08F', '#E4B363', 
                                 '#E8E9EB', '#5C6B73', '#FFFFFF']
                                # Red, Green, Yellow, Gray, Slate, White
        self.default_plot_colors = ['#5FBFF9', '#E85F5C', '#B2FFD6', 
                                    '#F9C784', '#343434', '#613F75']
                                    # Blue, Red, Green, Yellow, Black, Purple
        self.default_plot_color_iterator = 0

        # Enabled Parameters
        self.has_title = False
        self.has_x_label = False
        self.has_y_label = False
        self.has_legend = False
        self.has_colorbar = False
        self.has_animation = False
        self.has_plot_editor = False

        # Graphical Window
        self.root_window = Toplevel()
        self.root_image = self.get_image('home_screen')
        self.root_window.iconphoto(False, self.root_image)
        window_name = name if name != None else 'PlottingUtils - Figure'
        self.root_window.title(window_name)
        self.root_window.geometry('%dx%d'%(self.screen_width, self.screen_height))
        self.root_window.configure(bg=self.bg_color)
        self.root_window.update()
        self.root_window.bind('<Configure>', self.update_screen_dimensions)
        self.root_window.protocol("WM_DELETE_WINDOW", self.__close_program)

        # Draw/Text area
        self.canvas = Canvas(self.root_window, width = self.screen_width, 
                             height = self.screen_height, bd = 0, 
                             bg=self.highlight_colors[5], 
                             highlightthickness = 0)
        self.update_canvas_dimensions()
        self.canvas.place(x = 0, y = 0)

        # Plotting Area
        self.plot = Canvas(self.root_window, width = self.plot_dimensions[0], 
                           height = self.plot_dimensions[1], bg='#ffffff', bd=0)
        self.plot.place(x = self.offset_x, y = self.offset_y ,anchor = NW)
        self.plot.update()
        
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
        self.animation_speed = 1
        self.animation_tags = []

        # Keyboard shortcuts
        self.root_window.bind('<Right>', self.right_arrow_key_command)
        self.root_window.bind('<Left>', self.left_arrow_key_command)
        self.root_window.bind('<Up>', self.up_arrow_key_command)
        self.root_window.bind('<Down>', self.down_arrow_key_command)
        self.root_window.bind('<Delete>', self.delete_key_command)
        self.root_window.bind('<Escape>', self.escape_key_command)


        """
        rewrite as nicer array of scale factors.... Maybe??
        """
        # Scaling Factors
        self.x_scale_factor = 0
        self.y_scale_factor = 0
        self.scale_type= ['lin', 'lin']
        self.x_boundary = []
        self.y_boundary = []
        self.scale_unit_style = '{:.2f}'
        self.show_axis_custom = ''
        self.legend_pos = 'NE'

        # Grid
        self.x_grid = Grid('x', self.plot, self.fg_color)
        self.y_grid = Grid('y', self.plot, self.fg_color)

        self.X_axis_numbers = Axis_Numbers('x', self.canvas, self.x_grid.get_pos(), self.fg_color)
        self.X_axis_numbers.update_numbers(self.plot.winfo_width(), self.canvas_boundary[0], self.font_size)

        self.Y_axis_numbers = Axis_Numbers('y', self.canvas, self.y_grid.get_pos(), self.fg_color)
        self.Y_axis_numbers.update_numbers(self.plot.winfo_height(), self.canvas_boundary[0], self.font_size)

        # Drawn Content
        self.x_axis_numbers = []
        self.y_axis_numbers = []
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
        self.dataset_add('bFit')
        self.root_window.bind('<e>', self.__open_plot_editor)
        self.editor_window = Toplevel()
        self.editor_window.title('Plot Editor')
        self.editor_window.geometry('750x230')
        self.editor_window.protocol("WM_DELETE_WINDOW", self.__close_editor)
        self.editor_window.withdraw()
        
        self.plot_editor_selected_counter = 0
        self.plot_editor_selected_item = None
        self.editor_canvas = Canvas(self.editor_window, width = self.screen_width, 
                                    height = 230, bg=self.highlight_colors[3])
        self.editor_canvas.place(x=0, y=0)
        self.generate_plot_editor()

        # Plot Editing Toold
        self.mouse_enabled()
        self.__canvas_button_home_add()
        self.__canvas_button_axis_add()
        self.__canvas_button_select_add()
        self.__canvas_button_zoom_add()
        self.datapoints_selection = False
        self.zoom_data = False
        self.zoom_data_p1 = [0, 0]
        self.zoom_marker = self.plot.create_rectangle(0, 0, 0, 0, state='hidden')
        self.marked_points = []
        self.marked_text = []
        self.marked_objects = []

    # Debugging

    def debug_log(self, text_input):

        with open(self.file_debug, 'a') as save_file:
            save_file.write(text_input + '\n')

    # General

    def __close_program(self):
        self.root_window.withdraw()
        sys.exit()


    # Datasets

    def dataset_add(self, tag, create=None):
        """
        Creates a Dataset object with assigned tag if it 
        does not already exist. A dataset object is needed 
        for each unique plotted dataset
        """

        if self.debug: self.debug_log('dataset_add %s' %tag)

        if create == 'new': self.data_series.append(DataSeries(tag, self.plot))
        elif self.dataset_find(tag) != None: return
        else: self.data_series.append(DataSeries(tag, self.plot))

    def dataset_remove(self, tag):
        """
        Removes an existing datasets from memory and plotted view
        """

        if self.debug: self.debug_log('dataset_remove %s' %tag)

        for i in range(len(self.data_series)):
            if self.data_series[i].get_tag() == tag:
                dataset = self.data_series[i]
                if dataset.has_legend() == True:
                    1 # Add remove legend item!
                dataset.clear_data()
                self.data_series.pop(i)
                return

    def dataset_state(self, state, tag):
        """
        Hides/Unhides dataset from plotted view but keeps it in memory
        state = hidden, shown
        """

        if self.debug: self.debug_log('dataset_state %s, %s' %(state, tag))

        dataset = self.dataset_find(tag)
        if dataset != None: 
            if state == 'hidden': dataset.undraw_item(0)
            elif state == 'shown': 
                n_points = range(dataset.get_number_of_points())
                dataset.draw(n_points)
                self.update_plots(tag)
    
    def dataset_find(self, tag, create=None):
        """
        Returns the requested dataset given tag. 
        create='new' will generate the dataset if
        it does not exist
        """

        if self.debug: self.debug_log('dataset_find %s, %s' %(tag, create))

        for item in self.data_series: 
            if item.get_tag() == tag: return item
        
        if create == 'new':
            dataset = self.dataset_add(tag, create='new')
            return self.data_series[-1]


    # Index Operations

    def remove_drawn_items(self, search_list):
        """ Clears plotted content in search_list """

        if self.debug: self.debug_log('remove_drawn_items %s' %search_list)

        for item in search_list: self.canvas.delete(int(item))            
        search_list.clear()

    def find_tag_number(self, tag, search_list):
        """ Returns index of requested tag in its appropriate list """
        
        if self.debug: self.debug_log('find_tag_number %s, %s' %(tag, search_list))

        for i in range(len(search_list)):
            if search_list[i] == tag: return i


    # Resize Screen    

    def update_canvas_dimensions(self):
        """ Updates Screen Dimensions to allow for screen resizing """

        if self.debug: self.debug_log('update_canvas_dimensions')
        
        self.screen_padding_x = 4*self.font_size
        self.offset_x = 2*self.screen_padding_x
        self.offset_y = 40 + 4*self.font_size
        
        canvas_width = self.screen_width - 2*self.screen_padding_x
        canvas_height = self.screen_height - self.offset_y

        self.canvas_boundary = [self.offset_x, self.offset_y, 
                                canvas_width, canvas_height]
        self.plot_dimensions = (
                [int(self.canvas_boundary[2] - self.canvas_boundary[0]), 
                 int(self.canvas_boundary[3] - self.canvas_boundary[1])] )

    def update_screen_dimensions(self, event):
        """ Handles rescaling of program window """

        if self.debug: self.debug_log('update_screen_dimensions %s' %event)

        screen_size = self.root_window.geometry()
        plus_location = screen_size.find('+')
        x_position = screen_size.find('x')

        screen_width = int(screen_size[0:x_position])
        screen_height = int(screen_size[x_position+1:plus_location])

        width_delta = screen_width / self.screen_width
        height_delta = screen_height / self.screen_height

        # Screen only moved, not resized
        if width_delta == 1 and height_delta == 1: return
        
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.update_canvas_dimensions()
        self.canvas.config(width = self.screen_width, 
                           height = self.screen_height)

        self.plot.config(width = self.plot_dimensions[0] * width_delta, 
                         height = self.plot_dimensions[1] * height_delta)
        self.plot.place(x = self.offset_x, y = self.offset_y)

        self.x_grid.update_pos()
        self.y_grid.update_pos()
        self.X_axis_numbers.update_numbers(self.plot.winfo_width(), self.canvas_boundary[0], self.font_size)
        self.Y_axis_numbers.update_numbers(self.plot.winfo_height(), self.canvas_boundary[0], self.font_size)

        self.auto_focus()

        if self.has_colorbar:
            self.color_bar.config(height = self.plot_dimensions[1])
            self.color_bar.place(x = self.canvas_boundary[2] + 10, 
                                 y = self.canvas_boundary[1])
        if self.has_title: 

            bbox = self.canvas.bbox(self.title)
            width = (bbox[2] - bbox[0])/2
            self.canvas.moveto(self.title, self.screen_width/2 - width, 
                               self.font_size)
        if self.has_y_label: 
            bbox = self.canvas.bbox(self.y_label)
            height = (bbox[3] - bbox[1])/2
            p1 = self.font_size
            p2 = self.canvas_boundary[1] + self.plot_dimensions[1]/2 - height
            self.canvas.moveto(self.y_label, p1, p2)
        if self.has_x_label:
            bbox = self.canvas.bbox(self.x_label)
            width = (bbox[2] - bbox[0])/2
            p1 = self.canvas_boundary[0] + self.plot_dimensions[0]/2 - width
            p2 = self.canvas_boundary[3] + 5/2*self.font_size
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
        if self.has_legend: self.reposition_legend()


        self.home_button.place(x = self.canvas_boundary[2] - 5, 
                               y = self.canvas_boundary[1] - 5)
        self.scale_unit_button.place(x = self.canvas_boundary[2] - 45,
                                     y = self.canvas_boundary[1] - 5)
        self.datapoint_selector.place(x = self.canvas_boundary[2] - 85,
                                     y = self.canvas_boundary[1] - 5)

        self.raise_items()        

    def update_plots(self, tag=None):
        """ Redraws plotted data """
        
        if self.debug: self.debug_log('update_plots %s' %tag)

        data_list = []

        if tag != None:
            dataset = self.dataset_find(tag)
            if dataset != None: data_list.append(dataset)
        else:
            for dataset in self.data_series: data_list.append(dataset)
        for dataset in data_list:
            if dataset.is_drawn():        
                point = dataset.get_points()
                new_x = self.scale_vector(point[0,:], 'x')
                new_y = self.scale_vector(point[1,:], 'y')
                if dataset.is_animated(): 
                    new_index = self.animationScrollbar.get()
                else: new_index = 0
                dataset.update_item(new_x, new_y, new_index)
        
        for i in range(len(self.plotted_text)): self.update_text_pos(i)
        for i in range(len(self.marked_points)): self.update_data_marker(i)

    def update_text_pos(self, i):
        """ Moves text item[i] to the correct position """

        if self.debug: self.debug_log('update_text_pos %s' %i)

        position = self.plotted_text_position[i]
        scaled_x = self.scale_vector(position[0], 'x') 
        scaled_y = self.scale_vector(position[1], 'y')
        self.plot.moveto(self.plotted_text[i], scaled_x, scaled_y)

    def update_data_marker(self, i):

        if self.debug: self.debug_log('update_data_marker %s' %i)

        position = self.marked_points[i]

        scaled_x = self.scale_vector(position[0], 'x')
        scaled_y = self.scale_vector(position[1], 'y')

        box = self.plot.bbox(self.marked_objects[i])

        x = int(scaled_x - (box[2] - box[0]) / 2)
        y = int(scaled_y - (box[3] - box[1]) / 2)
        
        self.plot.moveto(self.marked_objects[i], x, y)
        self.plot.moveto(self.marked_text[i], x + 18, y)

    # Drag and Drop screen

    def mouse_enabled(self):

        if self.debug: self.debug_log('mouse_enabled')

        """ Adds mouse controll over the graph """
        self.plot_drag_mouse_clicked = False
        self.plot_drag_mouse_pos = [0, 0]

        self.plot.bind('<ButtonPress-1>', self.mouse_pressed)
        self.plot.bind('<ButtonPress-3>', self.right_mouse_pressed)
        self.plot.bind('<B1-Motion>', self.mouse_dragged)
        self.plot.bind('<ButtonRelease-1>', self.mouse_released)
        self.plot.bind('<MouseWheel>', self.mouse_scrolled)

    def mouse_pressed(self, event):
        """ Gets mouse click on plot area """

        if self.debug: self.debug_log('mouse_pressed %s' %event)

        # Data Marker
        if self.datapoints_selection:
            
            click_x = self.anti_scale_vector(event.x, 'x')
            click_y = self.anti_scale_vector(event.y, 'y')
            closest_point = self.datapoint_find(click_x, click_y)

            if np.linalg.norm(closest_point - [click_x, click_y]) > 2: return
            self.marked_points.append(closest_point)
            self.datapoint_mark()
        
        # Zoom in area
        elif self.zoom_data:
            self.zoom_data_p1[0] = event.x
            self.zoom_data_p1[1] = event.y
            self.plot.itemconfig(self.zoom_marker, state='normal')

        # Screen drag
        else:
            if self.plot_editor_selected_counter != 1:

                self.plot_drag_mouse_clicked = True
                
                if self.scale_type[0] == 'lin': x_val = event.x
                else: x_val = self.anti_scale_vector(event.x, 'x')
                
                if self.scale_type[1] == 'lin': y_val = event.y
                else: y_val = self.anti_scale_vector(event.y, 'y')
                
                self.plot_drag_mouse_pos = [x_val, y_val]

    def mouse_dragged(self, event):
        """ Allows for real time moving of the graphed data """

        if self.debug: self.debug_log('mouse_dragged %s' %event)

        if self.zoom_data:
            
            self.plot.coords(self.zoom_marker, self.zoom_data_p1[0], self.zoom_data_p1[1], event.x, event.y)

        elif self.plot_drag_mouse_clicked == True:

            if self.scale_type[0] == 'lin':
                delta_x = self.plot_drag_mouse_pos[0] - event.x
                delta_x *= self.x_scale_factor
                x_min = self.X_axis_numbers.get_lower_axis() + delta_x
                x_max = self.X_axis_numbers.get_upper_axis() + delta_x
                self.plot_drag_mouse_pos[0] = event.x
            elif self.scale_type[0] == 'log':
                delta_x = self.plot_drag_mouse_pos[0] - self.anti_scale_vector(event.x, 'x')
                x_min = self.X_axis_numbers.get_lower_axis() + delta_x
                x_max = self.X_axis_numbers.get_upper_axis() + delta_x
                
            if self.scale_type[1] == 'lin':
                delta_y = event.y - self.plot_drag_mouse_pos[1]
                delta_y *= self.y_scale_factor
                y_min = self.Y_axis_numbers.get_lower_axis() + delta_y
                y_max = self.Y_axis_numbers.get_upper_axis() + delta_y
                self.plot_drag_mouse_pos[1] = event.y
            elif self.scale_type[1] == 'log':
                delta_y = self.plot_drag_mouse_pos[1] - self.anti_scale_vector(event.y, 'y')
                y_min = self.Y_axis_numbers.get_lower_axis() + delta_y
                y_max = self.Y_axis_numbers.get_upper_axis() + delta_y

            self.set_x_axis(x_min, x_max, update=False)
            self.set_y_axis(y_min, y_max, update=False)

            self.update_plots()

    def mouse_released(self, event):
        """
        Disables graph movement and does item placement
        """

        if self.debug: self.debug_log('mouse_released %s' %event)

        # Zoom in area
        if self.zoom_data:
            self.plot.itemconfig(self.zoom_marker, state='hidden')
            x2 = self.anti_scale_vector(event.x, 'x')
            y2 = self.anti_scale_vector(event.y, 'y')

            self.set_x_axis(self.anti_scale_vector(self.zoom_data_p1[0], 'x'), x2, update=False)
            self.set_y_axis(self.anti_scale_vector(self.zoom_data_p1[0], 'x'), y2, update=False)
            self.update_plots()

        # End screen drag
        elif self.plot_drag_mouse_clicked == True:
            self.plot_drag_mouse_clicked = False

    def right_mouse_pressed(self, event):
        
        if self.zoom_data: self.__canvas_button_zoom_update()
        if self.datapoints_selection: self.__canvas_button_select_update()

    def mouse_scrolled(self, event):
        """
        Zoom in and out on graph
        """

        if self.debug: self.debug_log('mouse_scrolled %s' %event)

        if self.plot_editor_selected_counter != 1:

            # Scroll Location
            pos_x = event.x * self.x_scale_factor
            pos_y = event.y * self.y_scale_factor

            origin_x = (self.X_axis_numbers.get_upper_axis()-self.X_axis_numbers.get_lower_axis()) / 2
            origin_y = (self.Y_axis_numbers.get_upper_axis()-self.Y_axis_numbers.get_lower_axis()) / 2

            displacement_x = pos_x - origin_x
            displacement_y = origin_y - pos_y

            zoom_strength = 5
            zoom_direction = event.delta/120 / zoom_strength
            
            delta_x = (self.X_axis_numbers.get_upper_axis()-self.X_axis_numbers.get_lower_axis()) * zoom_direction
            delta_y = (self.Y_axis_numbers.get_upper_axis()-self.Y_axis_numbers.get_lower_axis()) * zoom_direction

            self.set_x_axis(self.X_axis_numbers.get_lower_axis() + delta_x + displacement_x, 
                        self.X_axis_numbers.get_upper_axis() - delta_x + displacement_x, update=False)
            self.set_y_axis(self.Y_axis_numbers.get_lower_axis() + delta_y + displacement_y, 
                        self.Y_axis_numbers.get_upper_axis() - delta_y + displacement_y, update=False)

            self.update_plots()


    # Canvas Buttons

    def __canvas_button_home_add(self):
        """ Creates auto focus button """

        if self.debug: self.debug_log('__canvas_button_home_add')

        image_file = self.file_image_location + '\\home.png'
        self.button_image_auto_home = (
                                ImageTk.PhotoImage(Image.open(image_file)) )
        self.home_button = Button(self.canvas, width = 30, height = 35, 
                                command = self.auto_focus, bg = self.bg_color, 
                                image = self.button_image_auto_home)
        self.home_button.place(x = self.canvas_boundary[2] - 5,
                               y = self.canvas_boundary[1] - 5, anchor = SE)
        
    def __canvas_button_axis_add(self):
        """Creates change axis label type button """
        
        if self.debug: self.debug_log('__canvas_button_axis_add')

        self.__scale_unit_iter = 0
        
        image_file = self.file_image_location + '\\scientific.png'
        self.button_image_axis_unit = (
                                ImageTk.PhotoImage(Image.open(image_file)) )
        self.scale_unit_button = Button(self.canvas, width = 30, height = 35, 
                        command = self.set_axis_label_type, bg = self.bg_color, 
                        image = self.button_image_axis_unit)
        self.scale_unit_button.place(x=self.canvas_boundary[2] - 45,
                        y=self.canvas_boundary[1] - 5, anchor = SE)

    def set_axis_label_type(self):
        """ Keeps track of which text format are used on the axis numbering
        Sets and updates graph accordingly """

        if self.debug: self.debug_log('set_axis_label_type')
        
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
            tex = 'time'
            style = '{:.2%}'
        elif self.__scale_unit_iter == 3:
            self.show_axis_custom = 'time'
            tex = 'blank'
            style = '{:.2f}'
            # Add More/Better Time Alternatives
        elif self.__scale_unit_iter == 4:
            self.show_axis_custom = 'blank'
            tex = 'number'
            style = ''

        image_file = self.file_image_location + '\\' + tex + '.png'
        self.button_image_axis_unit = (
                                ImageTk.PhotoImage(Image.open(image_file)) )

        self.scale_unit_button.config(image = self.button_image_axis_unit)
        self.scale_unit_style = style

        values = self.get_axis_numbers(item=self.X_axis_numbers)
        self.X_axis_numbers.set_axis_values(values)       
        values = self.get_axis_numbers(item=self.Y_axis_numbers)
        self.Y_axis_numbers.set_axis_values(values)       

    def __canvas_button_select_add(self):
        """ Creates data selection button """

        if self.debug: self.debug_log('__canvas_button_select_add')

        image_file = self.file_image_location + '\\select.png'
        self.button_image_select_point = (
                                ImageTk.PhotoImage(Image.open(image_file)) )
        self.datapoint_selector = Button(self.canvas, width = 30, height = 35, 
                                command = self.__canvas_button_select_update, 
                                bg = self.bg_color, 
                                image = self.button_image_select_point)
        self.datapoint_selector.place(x = self.canvas_boundary[2] - 85,
                                y = self.canvas_boundary[1] - 5, anchor = SE)

    def __canvas_button_select_update(self, extra=False):
        """ Updates '__canvas_button_select_add' button """

        if self.debug: self.debug_log('__canvas_button_select_update')

        if self.zoom_data == True and extra == False:
            self.__canvas_button_zoom_update(extra=True)

        if self.datapoints_selection == False:
            self.datapoint_selector.config(bg = self.highlight_colors[2])
            self.datapoints_selection = True
        else:
            self.datapoint_selector.config(bg = self.bg_color)
            self.datapoints_selection = False

    def __canvas_button_zoom_add(self):
        """ Creates data zoom button """

        if self.debug: self.debug_log('__canvas_button_zoom_add')

        image_file = self.file_image_location + '\\zoom.png'
        self.button_image_zoom = (
                                ImageTk.PhotoImage(Image.open(image_file)) )
        self.zoom_button = Button(self.canvas, width = 30, height = 35, 
                                command = self.__canvas_button_zoom_update, 
                                bg = self.bg_color, 
                                image = self.button_image_zoom)
        self.zoom_button.place(x = self.canvas_boundary[2] - 125,
                                y = self.canvas_boundary[1] - 5, anchor = SE)

    def __canvas_button_zoom_update(self, extra=False):
        """ Updates '__canvas_button_zoom_add' button """

        if self.debug: self.debug_log('__canvas_button_zoom_update')

        if self.datapoints_selection == True and extra == False:
            self.__canvas_button_select_update(extra=True)

        if self.zoom_data == False:
            self.zoom_button.config(bg = self.highlight_colors[2])
            self.zoom_data = True
        else:
            self.zoom_button.config(bg = self.bg_color)
            self.zoom_data = False


    def datapoint_find(self, x, y):
        
        if self.debug: self.debug_log('datapoint_fing %s, %s' %(x, y))

        shortest_distance = math.inf
        for i in range(1, len(self.data_series)):
            points = np.array(self.data_series[i].get_points())
            delta_x = points[0,:] - x
            delta_y = points[1,:] - y

            length = np.sqrt(delta_x**2 + delta_y**2)
            
            if np.min(length) < shortest_distance: 
                shortest_distance = np.min(length)
                best_index = np.argmin(length)
                best_point = points[:, best_index]

        return best_point

    def datapoint_mark(self):

        if self.debug: self.debug_log('datapoint_mark')

        position = self.marked_points[-1]
        
        self.marked_objects.append(self.plot.create_text(0, 0, text = '\u20dd', 
                                   anchor = CENTER, fill = self.fg_color))

        content = ('({:.2f}'.format(position[0]) 
                + ', {:.2f})'.format(position[1]))
        self.marked_text.append(self.plot.create_text(0, 0, 
                        fill = self.fg_color, anchor = W, text = content))
        self.update_data_marker(-1)


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
        """ Adds dataset if it does not exist and then 
        sets color of specified dataset """

        if self.debug: self.debug_log('set_line_color %s, %s' %(color, tag))

        dataset = self.dataset_find(tag, create='new')
        dataset.set_color(color)

    def set_line_width(self, lineWidth, tag):
        """
        Adds dataset if it does not exist and then 
        sets width of specified dataset lines
        """

        if self.debug: self.debug_log('set_line_width %s, %s' %(lineWidth, tag))

        dataset = self.dataset_find(tag, create='new')
        dataset.set_line_width(lineWidth)

    def set_dot_size(self, size, tag):
        """
        Adds dataset if it does not exist and then 
        sets size of specified datasets scatter points
        """

        if self.debug: self.debug_log('set_dot_size %s, %s' %(size, tag))

        dataset = self.dataset_find(tag, create = 'new')
        dataset.set_dot_size(size)


    # Plot Text

    def set_title(self, text):
        """ Sets/Updates title, Text = 'title' """

        if self.debug: self.debug_log('set_title %s' %text)

        if self.has_title == False:
            self.has_title = True
            self.title = self.canvas.create_text(self.screen_width/2, 
                        self.font_size, font = self.title_font, anchor = N,
                        text = text, fill = self.fg_color)
        else: self.canvas.itemconfig(self.title, text = text)         

    def set_text(self, position, text, tag):
        """ Sets text on graph: Position = [x, y], Text = content, Tag = reference  """

        if self.debug: self.debug_log('set_text %s, %s, %s' %(position, text, tag))

        self.plotted_text_position.append(position)
        scaled_pos = [self.scale_vector(position[0], 'x'), 
                      self.scale_vector(position[1], 'y')]
        self.plotted_text.append(self.plot.create_text(scaled_pos, anchor = NW,
                      text = text, fill = self.fg_color))
        self.plotted_text_tags.append(tag)

    def update_text(self, text, tag):
        """ Updates existing text on graph, Text = content, Tag = reference """

        if self.debug: self.debug_log('update_text %s, %s' %(text, tag))

        text_item = self.find_tag_number(tag, self.plotted_text_tags)
        if text_item != None:
            self.plot.itemconfig(self.plotted_text[text_item], text = text)
            return

    def find_text(self, content):
        """ Returns index of text item, Content = widget to search"""

        if self.debug: self.debug_log('find_text %s' %(content))

        text = self.plot.itemcget(content, 'text')
        for i in range(len(self.plotted_text)):
            if self.plot.itemcget(self.plotted_text[i], 'text') == text:
                return i    


    # Axis

    def auto_focus(self, source=None):
        """ Estimates a good x and y scale for the plotted data by 
        finding the min/max x/y for all data """

        if self.debug: self.debug_log('auto_focus %s' %source)

        all_values = False if source == 'scale_x' or source == 'scale_y' else True
        for i in range(1, len(self.data_series)):

            points = np.array(self.data_series[i].get_points())

            x, y = points[0,:], points[1,:]
            if all_values == False: x, y = x[x > 0], y[y > 0]

            if i == 1:
                min_x, max_x = np.min(x), np.max(x)
                min_y, max_y = np.min(y), np.max(y)
            else:
                if np.min(x) < min_x: min_x = np.min(x)
                if np.max(x) > max_x: max_x = np.max(x)
                if np.min(y) < min_y: min_y = np.min(y)
                if np.max(y) > max_y: max_y = np.max(y)


        # Used by log axis to auto set when changing lin/log            
        if source == 'scale_x': return [min_x, max_x]
        if source == 'scale_y': return [min_y, max_y]

        # To avoid div by 0, if min_x = max_x etc.
        delta_x = (max_x - min_x) / 10 if min_x != max_x else 2
        delta_y = (max_y - min_y) / 10 if min_y != max_y else 2

        # Graph auto-set
        if source == 'axis_x': return [round(min_x - delta_x), round(max_x + delta_x)]
        if source == 'axis_y': return [round(min_y - delta_y), round(max_y + delta_y)]

        if self.x_boundary and self.y_boundary:
            same_x = self.X_axis_numbers.get_lower_axis() == round(min_x - delta_x)
            same_y = self.Y_axis_numbers.get_lower_axis() == round(min_y - delta_y)
            if same_x and same_y: return

        self.set_x_axis((min_x - delta_x), (max_x + delta_x), update=False)
        self.set_y_axis((min_y - delta_y), (max_y + delta_y), update=False)
        self.update_plots()

    def set_labels(self, textx, texty):
        """ Sets/Updates axis labels, Textx = X Label, Texty = Y Label """

        if self.debug: self.debug_log('set_labels %s, %s' %(textx, texty))

        if self.has_x_label == False:
            self.has_x_label = True
            p1 = self.canvas_boundary[0] + self.plot_dimensions[0]/2
            p2 = self.canvas_boundary[3] + 5/2*self.font_size
            self.x_label = self.canvas.create_text(p1, p2, text = textx, 
                                            fill = self.fg_color, anchor = N)
        elif textx != 'keep': self.canvas.itemconfig(self.x_label, text = textx)

        if self.has_y_label == False:
            self.has_y_label = True
            p1 = self.font_size
            p2 = self.canvas_boundary[1] + self.plot_dimensions[1]/2
            self.y_label = self.canvas.create_text(p1, p2, angle=90, 
                                            text = texty, fill = self.fg_color,
                                            anchor = N)
        elif texty != 'keep': self.canvas.itemconfig(self.y_label, text = texty)

    def set_zero(self, start, end, order):
        """ Finds the position of 0 used by linear graphs as an additive factor """

        if self.debug: self.debug_log('set_zero %s, %s, %s' %(start, end, order))

        if order == 'x': 
            plot_dim = self.plot_dimensions[0] 
            numerator = start
        elif order == 'y': 
            plot_dim = self.plot_dimensions[1] 
            numerator = end
        common_term = plot_dim / (start - end)
        abs_term = abs(numerator) / (abs(start) + abs(end))

        if order == 'x':
            if end < 0: self.x0 = common_term * end
            elif start > 0: self.x0 = common_term * start
            else: self.x0 = abs_term * plot_dim
        elif order == 'y':
            if end < 0: self.y0 = common_term*abs(end)
            elif start > 0: self.y0 = -common_term*start + plot_dim
            else: self.y0 = abs_term * plot_dim

    def set_x_axis(self, x_start, x_end, steps=None, lines=None, update=True, axis=None, *args):
        """ Sets X-Axis, Args: Keep = keeps axis, axis = lin/log if want to switch,
            lines = true/false gridlines """
        
        if self.debug: self.debug_log('set_x_axis %s, %s, %s' %(x_start, x_end, args))

        if x_start == 'keep': x_start = self.X_axis_numbers.get_lower_axis()
        if x_end == 'keep': x_end = self.X_axis_numbers.get_upper_axis()

        # Gridlines + log/lin
        if axis != None:
            steps = self.x_grid.get_number_of_steps()
            visibility = self.x_grid.get_line_visibility()
            self.x_grid.remove()
        if axis == 'log': self.x_grid.set_style('log')
        elif axis == 'lin': self.x_grid.set_style('lin')
        if lines != None: self.x_grid.set_line_visibility(lines)
        if steps != None: 
            self.x_grid.set_number_of_steps(steps)
            self.X_axis_numbers.set_pos(self.x_grid.get_pos())     

        for name in args:
            if name == 'graph':
                x_start, x_end = self.auto_focus(source='axis_x')
                if self.x_boundary:
                    cond1 = x_start > self.X_axis_numbers.get_lower_axis()
                    cond2 = x_end < self.X_axis_numbers.get_upper_axis()
                    if cond1 and cond2 : return
                    else:
                        if x_start > self.X_axis_numbers.get_lower_axis(): 
                            x_start = self.X_axis_numbers.get_lower_axis()
                        if x_end < self.X_axis_numbers.get_upper_axis(): 
                            x_end = self.X_axis_numbers.get_upper_axis()
        
        num_ticks = self.x_grid.get_number_of_steps()
        if num_ticks == 0: num_ticks = 1 
        
        if x_start > x_end: x_start, x_end = x_end, x_start
        self.set_zero(x_start, x_end, 'x')   
        
        self.X_axis_numbers.set_lower_axis(x_start)
        self.X_axis_numbers.set_upper_axis(x_end)

        if self.scale_type[0] == 'lin':
            self.x_scale_factor = (x_end-x_start)/self.plot_dimensions[0]        
        elif self.scale_type[0] == 'log':
            if x_start <= 0: x_start, x_end = self.log_scale('scale_x')
            self.x_scale_factor = (x_end-x_start)/self.plot_dimensions[0]
            k = (x_start-x_end)/(math.log10(x_start)-math.log10(x_end))
            c = x_end - k * math.log10(x_end)
            self.x_log_scale = [k, c]

            num_ticks = round(math.log10(x_end/x_start))
            
            for i in range(num_ticks+1):
                self.x_boundary.append(x_end * 10**(-num_ticks+i))
        
        values = self.get_axis_numbers(steps=num_ticks, start=x_start, end=x_end)
        self.X_axis_numbers.set_axis_values(values)       
        
        
        if update: self.update_plots()

    def set_y_axis(self, y_start, y_end, steps=None, lines=None, update=True, axis=None, *args):
        """ Sets Y-Axis, Args: Keep = keeps axis, Lock = locks axis, axis = line/log,
            lines = true/false gridlines """

        if self.debug: self.debug_log('set_y_axis %s, %s, %s' %(y_start, y_end, args))

        auto_focus = False

        if y_start == 'keep': y_start = self.Y_axis_numbers.get_lower_axis()
        if y_end == 'keep': y_end = self.Y_axis_numbers.get_upper_axis()

        if axis != None:
            steps = self.y_grid.get_number_of_steps()
            visibility = self.y_grid.get_line_visibility()
            self.y_grid.remove()
        if axis == 'log': self.y_grid.set_style('log')
        elif axis == 'lin': self.y_grid.set_style('lin')
        if lines != None: self.y_grid.set_line_visibility(lines)
        if steps != None: 
            self.y_grid.set_number_of_steps(steps)
            self.Y_axis_numbers.set_pos(self.y_grid.get_pos())

        for name in args:
            if name == 'graph':
                auto_focus = True
                if self.y_boundary:
                    cond1 = y_start > self.Y_axis_numbers.get_lower_axis()
                    cond2 = y_end < self.Y_axis_numbers.get_upper_axis()
                    if cond1 and cond2: return
                    else:
                        if y_start > self.Y_axis_numbers.get_lower_axis(): 
                            y_start = self.Y_axis_numbers.get_lower_axis()
                        if y_end < self.Y_axis_numbers.get_upper_axis(): 
                            y_end = self.Y_axis_numbers.get_upper_axis()

        num_ticks = self.y_grid.get_number_of_steps()
        if num_ticks == 0: num_ticks = 1 

        if auto_focus == True: y_start, y_end = self.auto_focus(source='axis_y')
        if y_start > y_end: y_start, y_end = y_end, y_start
        self.set_zero(y_start, y_end, 'y')   

        self.Y_axis_numbers.set_lower_axis(y_start)
        self.Y_axis_numbers.set_upper_axis(y_end)

        self.y_boundary.clear()
        if self.scale_type[1] == 'lin':
            self.y_scale_factor = (y_end-y_start)/self.plot_dimensions[1]

            valueSize = (y_end-y_start)/num_ticks

            for i in range(num_ticks+1):
                self.y_boundary.append(y_start + i*valueSize)

        elif self.scale_type[1] == 'log':
            
            if y_start <= 0: y_start, y_end = self.log_scale('scale_y')
            self.y_scale_factor = (y_end-y_start)/self.plot_dimensions[1]
            k = (y_start-y_end)/(math.log10(y_start)-math.log10(y_end))
            c = y_end - k * math.log10(y_end)
            self.y_log_scale = [k, c]

            num_ticks = round(math.log10(y_end/y_start))

            for i in range(num_ticks+1):
                self.y_boundary.append(y_end * 10**(-num_ticks+i))

        values = self.get_axis_numbers(steps=num_ticks, start=y_start, end=y_end)
        self.Y_axis_numbers.set_axis_values(values)   

        if update: self.update_plots()

    # Updated to class system
    def update_grid(self, steps, grid, number):
        """ Inputs new #steps and grid/number 
            as x/y to update grid and axis numbers """

        try: steps = int(steps)
        except: return
        if steps == 0: steps = 1
            
        grid.set_number_of_steps(steps)
        number.set_pos(grid.get_pos())
        values = self.get_axis_numbers(steps=steps, item=number)
        number.set_axis_values(values)

    # Updated to class system
    def get_axis_numbers(self, steps=None, start=None, end=None, item=None):
        """ Returns values to be printed along the axis
            steps = number of gridlines, start/end = min/max x/y
            item = x_axis or y_axis                              """

        if self.debug: self.debug_log('get_axis_numbers %s, %s, %s' %(steps, start, end, item))
        
        if item != None:
            start = item.get_lower_axis()
            end = item.get_upper_axis()
            if steps == None: steps = len(item.get_axis_values()) - 1

        output = []
        d_step = (end - start) / steps

        for i in range(steps + 1):
            val = start + d_step * i
            if self.show_axis_custom == 'time':
                hour = int(val%24)
                minute = int(60*(val%24 - hour))
                output.append(str(hour).zfill(2) + ':' + str(minute).zfill(2)) 
            elif self.show_axis_custom == 'blank':
                output.append('')
            else: 
                output.append(self.scale_unit_style.format(val))
        
        return output

    def log_scale(self, order):
        """ Find magnitude for auto-setting logarithmic scale """

        if self.debug: self.debug_log('log_scale %s' %(order))

        data_low, data_high = self.auto_focus(source = order)
        power_low = math.floor(math.log10(data_low))
        power_high = math.ceil(math.log10(data_high))
        
        return [10**power_low, 10**power_high]

    def set_axis_scale_type(self, *args):
        """
        Automatically Sets scale type:
        Options: digit, e, %, time, ''
        """
        
        if self.debug: self.debug_log('set_axis_scale_type %s' %(args))

        for name in args:

            if name == 'digit': self.__scale_unit_iter = 4
            elif name == 'e': self.__scale_unit_iter = 0
            elif name == '%': self.__scale_unit_iter = 1
            elif name == '\u231A': self.__scale_unit_iter = 2
            elif name == '': self.__scale_unit_iter = 3
            else: return

            self.set_axis_label_type()
            return
            
    # Legend

    def set_legend(self, pos=None):
        """ Specify position with pos= NW, NE, SW, SE"""

        if self.debug: self.debug_log('set_legend %s' %(pos))

        self.has_legend = True
        if   pos == None: self.legend_pos = 'NE'
        elif pos == 'NE': self.legend_pos = 'NE'
        elif pos == 'NW': self.legend_pos = 'NW'
        elif pos == 'SE': self.legend_pos = 'SE'
        elif pos == 'SW': self.legend_pos = 'SW'

        names, colors, symbol = [], [], []
        for dataset in self.data_series:
            if dataset.get_legend() != None:
                names.append(dataset.get_legend())
                colors.append(dataset.get_color())
                symbol.append(dataset.get_symbol())

        self.update_legend_offsets()
        for i in range(len(names)): self.add_to_legend(names[i], colors[i], symbol[i])

    def update_legend_offsets(self, tag=None):

        if self.debug: self.debug_log('update_legened_offsets %s' %(tag))

        names = []
        for dataset in self.data_series:
            if dataset.get_legend() != None: 
                names.append(dataset.get_legend())
        if tag != None: names.append(tag) # What does it do? Is it not already part of list through above?

        text_length = len(max(names, key=len))
        pos = self.legend_pos
        if pos[0]   == 'N': self.legend_y_offset = self.font_size
        if pos[0]   == 'S': self.legend_y_offset = (self.plot_dimensions[1] 
                                                    - len(names)*2*self.font_size)
        if pos[1]   == 'W': self.legend_x_offset = 2*self.font_size
        elif pos[1] == 'E': self.legend_x_offset = (self.plot_dimensions[0] 
                                                    - 2/3*text_length*self.font_size)

    def reposition_legend(self, tag=None):
        
        if self.debug: self.debug_log('reposition_legend %s' %(tag))

        self.update_legend_offsets(tag)
        for i in range(len(self.legend_content)):
            self.plot.moveto(self.legend_content[i], self.legend_x_offset, 
                             self.legend_y_offset + 2*i*self.font_size)

        for i in range(len(self.legend_markers)):
            self.plot.moveto(self.legend_markers[i], self.legend_x_offset
                             - 3/2*self.font_size, self.legend_y_offset 
                             + (2*i+1/4)*self.font_size)

    def add_to_legend(self, name, color, symbol):

        if self.debug: self.debug_log('add_to_legend %s, %s, %s' %(name, color, symbol[1:]))

        i = len(self.legend_content)

        p1 = self.legend_x_offset
        p2 = self.legend_y_offset + 2*i*self.font_size

        self.legend_content.append(self.plot.create_text(p1, p2, anchor=NW, 
                                   fill=self.fg_color, text=name))

        self.legend_markers.append(self.plot.create_text(p1 - 3/2*self.font_size, 
                                   p2, fill=color, text=symbol, anchor=NW))

    def update_legend(self, tag, text=None, color=None, symbol=None):
        
        if self.debug: self.debug_log('update_legend %s, %s, %s, %s' %(tag, text, color, symbol))

        dataset = self.dataset_find(tag)
        if dataset == None: return

        tex = dataset.get_legend()
        i = self.find_legend(text=tex)

        if text != None:
            self.plot.itemconfig(self.legend_content[i], text=name)
        if color != None:
            self.plot.itemconfig(self.legend_markers[i], fill=color)
        if symbol != None:
            self.plot.itemconfig(self.legend_markers[i], text=symbol)

    def find_legend(self, item=None, text=None):
        """ Returns index of legend item, Content = widget to search"""

        if self.debug: self.debug_log('find_legend %s, %s' %(item, text))

        if text == None: text = self.plot.itemcget(item, 'text')
        for i in range(len(self.legend_content)):
            if self.plot.itemcget(self.legend_content[i], 'text') == text:
                return i    

    def switch_legend_index(self, index, order):

        if self.debug: self.debug_log('switch_legend_index %s, %s' %(index, order))

        item_change = self.plot.coords(self.legend_content[index])[1]
        marker_change = self.plot.coords(self.legend_markers[index])[1]
        item_move = self.plot.coords(self.legend_content[index+order])[1]
        marker_move = self.plot.coords(self.legend_markers[index+order])[1]

        item_delta = (item_change - item_move)
        marker_delta = (marker_change - marker_move)

        self.plot.move(self.legend_content[index], 0, -item_delta)
        self.plot.move(self.legend_content[index+order], 0, item_delta)

        self.plot.move(self.legend_markers[index], 0, -marker_delta)
        self.plot.move(self.legend_markers[index+order], 0, marker_delta)
        
        self.legend_content[index], self.legend_content[index+order] = self.legend_content[index+order], self.legend_content[index]
        self.legend_markers[index], self.legend_markers[index+order] = self.legend_markers[index+order], self.legend_markers[index]

    # Data validation for plotted objects

    def scale_vector(self, data, *args):

        if self.debug: self.debug_log('scale_vector %s, %s' %(data, args))
        
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

        if self.debug: self.debug_log('anti_scale_vector %s, %s' %(data, args))

        data = np.array(data)

        for name in args:
            if name == 'x':
                if self.scale_type[0] == 'log': 
                    return 10**((data*self.x_scale_factor 
                                - self.x_log_scale[1]) / self.x_log_scale[0])
                elif self.scale_type[0] == 'lin':
                    return (data-self.x0) * self.x_scale_factor
            elif name == 'y':
                if self.scale_type[1] == 'log':
                    return 10**(((-data + self.plot_dimensions[1])*self.y_scale_factor 
                                - self.y_log_scale[1]) / self.y_log_scale[0])
                elif self.scale_type[1] == 'lin':
                    return (self.y0 - data) * self.y_scale_factor
            
    def get_scale_factor(self):

        if self.debug: self.debug_log('get_scale_factor')

        return [self.x_scale_factor, self.y_scale_factor]

    # Plot Data

    def graph(self, x, y, tag, style=None, scale=None, grid=None, legend=None, 
             animate=None, color=None):
        """
        Main 2D plotter. 
        Style: line, scatter, dot, +, x, *, circle etc.
        Scale: log,
        grid: on, x, y
        legend: 'name',
        animate: on,
        color: #xxxxxx, only hex colors
        """

        if self.debug: self.debug_log('graph %s, %s, %s, %s, %s, %s, %s, %s, %s' 
                    %(x, y, tag, style, scale, grid, legend, animate, color))

        dataset = self.dataset_find(tag, create='new')

        # Plotting Parameters
        plot_range = range(np.size(x))
        if grid == 'on': 
            self.x_grid.set_line_visibility(True)
            self.y_grid.set_line_visibility(True)
        elif grid =='x': self.x_grid.set_line_visibility(True)
        elif grid =='y': self.y_grid.set_line_visibility(True)

        if scale == 'log': 
            self.x_grid.set_style('log')
            self.y_grid.set_style('log')
            self.scale_type = ['log', 'log']
        elif scale == 'lin': 
            self.x_grid.set_style('lin')
            self.y_grid.set_style('lin')
            self.scale_type = ['lin', 'lin']

        if style != None: 
            style = self.find_data_marker(style)
            if style != None:
                dataset.set_plot_type('scatter')
                dataset.set_symbol(style)
        
        if animate == 'on': 
            self.enable_animator(len(x)-1)
            self.animation_tags.append(tag)
            dataset.set_animation(True)
            plot_range = 0
        if legend != None: dataset.set_legend(legend)
        if color != None:
            if self.is_hex_color(color): dataset.set_color(color)
            

        dataset.add_points(x,y)
        self.auto_focus()
        dataset.add_scaled_points(self.scale_vector(x, 'x'), 
                                  self.scale_vector(y, 'y'))

        if dataset.is_colored() == False:
            dataset.set_color(self.next_plot_color())
        
        dataset.draw(plot_range)

    def find_data_marker(self, marker):
        
        if self.debug: self.debug_log('find_data_marker %s' %(marker))

        # Returning None -> line graph
        if marker == 'line': return None
        elif marker == 'dot' or marker == '.': return '\u25cf'
        elif marker == '+': return '+'
        elif marker == 'o': return '\u20dd'
        elif marker == 'scatter': return '\u25cf'
        elif marker == 'x': return 'x'
        elif marker == '*': return '*'
        elif marker == 'square': return '\u25a0'
        else: return None


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
                    xPoints.append(self.X_axis_numbers.get_lower_axis() + i*(1+j))
            return xPoints
    def plotBestFit(self, *args):
        
        dataset = self.dataset_find('bFit')
        if dataset != None: 
            # num = self.dataset_find('bFit')
            for i in range(dataset.getNumberOfPoints()):
                y = self.lineApproximations[0] + self.lineApproximations[1]*math.exp(self.lineApproximations[2]*dataset.getPoint(i)[0])
                dataset.appendPoint([dataset.getPoint(i)[0],y], i)
            
            self.update_plots('bFit')
    

  


    def enable_animator(self, length):

        if self.debug: self.debug_log('enable_animator %s' %(length))
        
        if self.has_animation == False:
            self.animationScrollbar = Scale(self.canvas, from_=1, to=length, 
                        resolution=1, bg=self.bg_color, command=self.animate)
            self.animationScrollbar.place(x = self.canvas_boundary[2] 
                        + self.font_size , y = self.canvas_boundary[1])
            self.animationScrollbar.config(length = self.canvas_boundary[3]
                        - self.canvas_boundary[1] - self.font_size)
            self.has_animation = True

    def animate(self, value):

        if self.debug: self.debug_log('animate %s' %(value))

        value = int(value)-1
        for tag in self.animation_tags: self.dataset_find(tag).move_item(value)

    def right_arrow_key_command(self, event):

        if self.debug: self.debug_log('right_arrow_key_command %s' %(event))

        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            x_scale = (self.X_axis_numbers.get_upper_axis()-self.X_axis_numbers.get_lower_axis())/100
            self.plotted_text_position[txt_index][0] += x_scale
            self.update_text_pos(txt_index)
            
        elif self.has_animation == True:
            self.animationScrollbar.set(self.animationScrollbar.get()
                                        + self.animation_speed)

    def left_arrow_key_command(self, event):

        if self.debug: self.debug_log('left_arrow_key_command %s' %(event))

        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            x_scale = (self.X_axis_numbers.get_upper_axis()-self.X_axis_numbers.get_lower_axis())/100
            self.plotted_text_position[txt_index][0] -= x_scale
            self.update_text_pos(txt_index)
        elif self.has_animation == True:
            self.animationScrollbar.set(self.animationScrollbar.get() 
                                        - self.animation_speed)
    
    def up_arrow_key_command(self, event):

        if self.debug: self.debug_log('up_arrow_key_command %s' %(event))

        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index != None: 
                y_scale = (self.Y_axis_numbers.get_upper_axis()-self.Y_axis_numbers.get_lower_axis())/100
                self.plotted_text_position[txt_index][1] += y_scale
                self.update_text_pos(txt_index)

            legend_index = self.find_legend(item=self.plot_editor_selected_item)
            if legend_index != None and legend_index > 0:
                self.switch_legend_index(legend_index, -1)
    
    def down_arrow_key_command(self, event):

        if self.debug: self.debug_log('down_arrow_key_command %s' %(event))

        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index != None:
                y_scale = (self.Y_axis_numbers.get_upper_axis()-self.Y_axis_numbers.get_lower_axis())/100
                self.plotted_text_position[txt_index][1] -= y_scale
                self.update_text_pos(txt_index)
                return
            
            legend_index = self.find_legend(item=self.plot_editor_selected_item)
            if legend_index != None and legend_index+1 < len(self.legend_content):
                self.switch_legend_index(legend_index, 1)
                
    def delete_key_command(self, event):

        if self.debug: self.debug_log('delete_key_command %s' %(event))

        if self.plot_editor_selected_item != None:
            txt_index = self.find_text(self.plot_editor_selected_item)
            if txt_index == None: return
            self.plot.delete(self.plotted_text[txt_index])
            self.plotted_text.pop(txt_index)
            self.plotted_text_tags.pop(txt_index)
            self.plotted_text_position.pop(txt_index)
            self.__select_item()

    def escape_key_command(self, event):

        if self.debug: self.debug_log('escape_key_command %s' %(event))

        if self.plot_editor_selected_item != None: self.__select_item()

    # Markers

    def set_markerbar(self, size_array, tag):

        if self.debug: self.debug_log('set_markerbar %s, %s' %(size_array, tag))

        dataset = self.dataset_find(tag, create='new')
        dataset.set_markerbar(size_array)

    def update_markers(self, tag):

        if self.debug: self.debug_log('update_makers %s' %(tag))

        dataset = self.dataset_find(tag)
        if dataset == None: return
        dataset.update_markers()
    
    # Colors

    def next_plot_color(self): 

        if self.debug: self.debug_log('next_plot_color')

        cur_color = self.default_plot_colors[self.default_plot_color_iterator]
        self.default_plot_color_iterator +=1
        self.default_plot_color_iterator %= len(self.default_plot_colors)
        return cur_color

    def get_color(self, dataset):

        if self.debug: self.debug_log('get_color %s' %(dataset))

        colors = dataset.get_color()
        data_range = range(dataset.getNumberOfPoints())
        if isinstance(colors, str): 
            colors = [dataset.get_color() for n in data_range]
        return colors

    def update_colors(self, tag):

        if self.debug: self.debug_log('update_colors %s' %(tag))

        dataset = self.dataset_find(tag)
        if dataset == None: return
        dataset.update_colors()

    def set_color(self, color, tag):
        """ Set color for dataseries in hex code """

        if self.debug: self.debug_log('set_color %s, %s' %(color, tag))

        if self.is_hex_color(color): 
            dataset = self.dataset_find(tag, create='new')
            dataset.set_color(color)
            dataset.update_colors()
            if dataset.get_legend() and self.has_legend: 
                        self.update_legend(tag, color=color)

    def set_colorbar(self, color_array, tag):

        if self.debug: self.debug_log('set_colorbar %s, %s' %(color_array, tag))

        dataset = self.dataset_find(tag, create='new')
        dataset.set_colorbar(color_array)

    def add_colorbar(self, color_start, color_end, *args):   

        if self.debug: self.debug_log('add_colorbar %s, %s, %s' %(color_start, color_end, args))

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

                scaled_pos = [self.canvas_boundary[2] + 50, 
                              self.canvas_boundary[3] - i*dH - self.font_size]
                self.color_bar_text.append(self.canvas.create_text(scaled_pos, 
                                anchor=NW, text=args[0][i], fill=self.fg_color))

    def get_colorbar(self): 

        if self.debug: self.debug_log('get_colorbar')

        return np.flip(self.colorbar_colors)

    def is_hex_color(self, color):

        if self.debug: self.debug_log('is_hex_color %s' %(color))

        hex_colors = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        regexp = re.compile(hex_colors)
        if regexp.search(color): return True
        return False

    def get_image(self, file):

        if self.debug: self.debug_log('get_image %s' %(file))

        image_file = self.file_image_location + '\\' + file + '.png'
        return ImageTk.PhotoImage(Image.open(image_file)) 

    # Is this even in use???
    def clear_plot_data(self, tag):
        plotPos = self.dataset_find(tag)
        if plotPos != None: 
            for item in self.plotted_items[plotPos]:
                self.canvas.delete(item)

    def get_plot_x_values(self, index, tag):
        dataset = self.dataset_find(tag)
        if dataset != None: return dataset.get_point(index)

    def get_plot_y_values(self, index, tag):
        dataset = self.dataset_find(tag)
        if dataset != None: return dataset.get_point(index)

    # Save Data

    def __save_data(self, *args):
        
        if self.debug: self.debug_log('__save_data %s' %(args))

        for i in args:
            dataset = self.dataset_find(i)
            if dataset == None: return

            cur_time = str(datetime.now().time())[0:8]
            cur_time = cur_time.replace(':', '_')
            
            data_name = self.file_save_location + '\\' + str(i) + '_' + cur_time
            data = dataset.get_points()
            np.save(data_name, data, allow_pickle=True, fix_imports=True)
    
    def __load_data(self):

        if self.debug: self.debug_log('__load_data')

        tag = self.om_load_variable.get()
        if tag == '': return 

        data_name = self.file_save_location + '\\' + str(tag)
        if os.path.exists(data_name):
            
            self.dataset_add(tag)
            dataset = self.dataset_find(tag)
            dataset.set_color(self.load_data_color)
            dataset.set_legend(tag)

            data = np.load(data_name)    
            self.graph(data[0,:], data[1,:], str(tag), self.load_data_type)

            if self.load_data_legend: 
                self.add_to_legend(tag, self.load_data_color, dataset.get_symbol())
                self.reposition_legend(tag=tag)

            self.update_plots(tag=tag)

            self.raise_items()

    def load_data(self, tag):
        """ Opens saved data and returns it as x, y """

        if self.debug: self.debug_log('load_data %s' %(tag))

        data_name = self.file_save_location + '\\' + str(tag) + '.npy'
        if os.path.exists(data_name): return np.load(data_name)    

    def save_data(self, filename, tag):

        if self.debug: self.debug_log('save_data %s, %s' %(filename, tag))

        dataset = self.dataset_find(tag)
        if dataset == None: return

        data_name = self.file_save_location + '\\' + str(filename)
        data = dataset.get_points()
        np.save(data_name, data, allow_pickle=True, fix_imports=True)


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
        
        self.__load_button_images()

        # Load Text Edit
        self.__editor_title()
        self.__editor_labels()
        self.__editor_text()

        # Load Axis Edit
        self.__editor_x_axis()
        self.__editor_y_axis()

        # Functions
        self.__editor_animation()
        # self.__editor_best_fit()
        
        # Save and Load Data
        self.__editor_save_data()
        self.__editor_load_data()
        self.__editor_load_selections()


    ## Initializers

    def __editor_title(self):

        self.editor_canvas.create_text(10, 10, anchor=W, text='Title', 
                                       fill=self.fg_color, font=self.editor_font)
        self.editor_canvas.create_line(10,16,200,16)
        self.title_input = Entry(self.editor_canvas, fg='gray')
        self.title_input.insert(0, 'Title')
        self.title_input.place(x=10,y=22, anchor=NW)
        self.__add_focus_listeners(self.title_input)
        self.title_input.bind("<Return>", lambda event: 
                              self.set_title(self.title_input.get()))

    def __editor_x_axis(self):
        
        self.editor_canvas.create_text(10, 60, anchor=W, text='X Axis',
                                       fill=self.fg_color, font=self.editor_font)
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
                                self.update_grid(self.x_scale_steps.get(), 
                                self.x_grid, self.X_axis_numbers))

        self.x_grid_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__enable_grid('x'), 
                    bg=self.bg_color, image=self.button_image_on)
        self.x_grid_button.place(x=145,y=70, anchor=NW)

        self.x_linlog_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__switch_linlog('x'), bg=self.bg_color, 
                    image=self.button_image_lin)
        self.x_linlog_button.place(x=145,y=105, anchor=NW)

    def __editor_y_axis(self):
        
        self.editor_canvas.create_text(10, 150, anchor=W, text='Y Axis', 
                                       fill=self.fg_color, font=self.editor_font)
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
                                self.update_grid(self.y_scale_steps.get(), 
                                self.y_grid, self.Y_axis_numbers))

        self.y_grid_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__enable_grid('y'), 
                    bg=self.bg_color, image=self.button_image_on)
        self.y_grid_button.place(x=145,y=160, anchor=NW)
        
        self.y_linlog_button = Button(self.editor_canvas, width=25, height=25, 
                    command=lambda: self.__switch_linlog('y'), bg=self.bg_color, 
                    image=self.button_image_lin)
        self.y_linlog_button.place(x=145,y=195, anchor=NW)

    def __editor_labels(self):
        
        self.editor_canvas.create_text(230, 10, anchor=W, text='Labels', 
                                       fill=self.fg_color, font=self.editor_font)
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

    def __editor_text(self):
        
        self.editor_canvas.create_text(230, 80, anchor=W, text='Text Editor', 
                                       fill=self.fg_color, font=self.editor_font)
        self.editor_canvas.create_line(230,86,420,86)

        self.select_item_text_input = Entry(self.editor_canvas, fg='gray')
        self.select_item_text_input.insert(0, 'Text Editor')
        self.select_item_text_input.place(x=230,y=96, anchor=NW)
        self.__add_focus_listeners(self.select_item_text_input)
        self.select_item_text_input.bind("<Return>", self.__select_item_change)

        self.select_item_button = Button(self.editor_canvas, bg=self.bg_color, 
                        width = 25, height=25, image=self.button_image_item_sel,
                        command=self.__select_item)
        self.select_item_button.place(x= 360, y = 92)

    def __editor_animation(self):
         
        self.editor_canvas.create_text(230, 130, anchor=W, text='Animation', 
                                       fill=self.fg_color, font=self.editor_font)
        self.editor_canvas.create_line(230,136,420,136)

        self.animation_speed_input = Entry(self.editor_canvas, fg='gray')
        self.animation_speed_input.insert(0, 'Animation Speed')
        self.animation_speed_input.place(x=230,y=142, anchor=NW)
        self.__add_focus_listeners(self.animation_speed_input)
        self.animation_speed_input.bind("<Return>", self.__set_animation_speed)

    def __editor_save_data(self):
        
        self.editor_canvas.create_text(450, 10, anchor=W, text='Save Data', 
                                       fill=self.fg_color, font=self.editor_font)
        self.editor_canvas.create_line(450,16,680,16)

        self.om_save_variable = StringVar()
        self.om_save_variable.trace('w', self.__update_save_tag)
        self.save_data_tag_selector = OptionMenu(self.editor_canvas, 
                                            self.om_save_variable, '')
        self.save_data_tag_selector.config(bg=self.bg_color, width=1, font='bold')                                            
        self.save_data_tag_selector.place(x=580, y=22)
 
        self.save_data_button = Button(self.editor_canvas, width=25, height=25, 
                                command=lambda: self.__save_data(self.om_save_variable.get()), 
                                bg=self.bg_color, image=self.button_image_save_data)
        self.save_data_button.place(x=640,y=22, anchor=NW)

        self.save_data_name_color = self.editor_canvas.create_oval(450, 36, 
                                        458, 44, state='hidden')
        self.save_data_name_selection = self.editor_canvas.create_text(465, 40, 
                                        anchor=W, text='', fill=self.fg_color, 
                                        font=self.editor_font)

    def __editor_load_data(self):
        
        self.editor_canvas.create_text(450, 62, anchor=W, text='Load Data', 
                                       fill=self.fg_color, font=self.editor_font)
        self.editor_canvas.create_line(450,68,680,68)

        self.om_load_variable = StringVar()
        self.om_load_variable.trace('w', self.__update_load_tag)
        self.load_data_tag_selector = OptionMenu(self.editor_canvas, 
                                            self.om_load_variable, '')
        self.load_data_tag_selector.config(bg=self.bg_color, width=1, font='bold')                                            
        self.load_data_tag_selector.place(x=580, y=74)

        self.load_data_button = Button(self.editor_canvas, width=25, height=25, 
                                command=lambda:self.__load_data(), 
                                bg=self.bg_color, image=self.button_image_load_data)
        self.load_data_button.place(x=640,y=74, anchor=NW)

        self.load_data_name_selection = self.editor_canvas.create_text(465, 128,
                                        anchor=W, text='', fill=self.fg_color, 
                                        font=self.editor_font)

    def __editor_load_selections(self):

        self.load_data_type = 'scatter'
        self.load_data_type_button = Button(self.editor_canvas, width = 25, 
                                height = 25, command=self.__change_plot_type, 
                                bg = self.bg_color, 
                                image = self.button_image_data_scatter)
        self.load_data_type_button.place(x=450,y=74, anchor=NW)

        index = self.default_plot_color_iterator
        self.load_data_color = self.default_plot_colors[index]
        self.load_data_color_button = Button(self.editor_canvas, width = 25, 
                                height = 25, command=self.__change_plot_color, 
                                bg = self.load_data_color, image=self.button_image_color)
        self.load_data_color_button.place(x=485,y=74, anchor=NW)

        self.load_data_legend = True
        self.load_data_legend_button = Button(self.editor_canvas, width = 25, 
                                height = 25, command=self.__change_plot_legend, 
                                bg = self.bg_color, image=self.button_image_legend_on)
        self.load_data_legend_button.place(x=520, y=74, anchor=NW)

    def __editor_best_fit(self):
        # Best Fit, not in use
        self.bestFitButton = Button(self.editor_canvas, text='Best Fit', command=self.__bestFit)
        self.bestFitButton.place(x= 450, y = 10)
        self.edit_buttons = []
        self.edit_buttons.append(Scale(self.editor_canvas, from_=0, to=10, 
                                resolution=0.01, command=self.__changeA))
        self.edit_buttons.append(Scale(self.editor_canvas, from_=0, to=10, 
                                resolution=0.01, command=self.__changeB))
        self.edit_buttons.append(Scale(self.editor_canvas, from_=0, to=100, 
                                resolution=0.01, command=self.__changeC))
        for i in range(len(self.edit_buttons)):
            self.edit_buttons[i].place(x = (i+2)*120 + 300, y =30)

    ## Listeners

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


    ## Updaters

    def __load_button_images(self):

        self.button_image_on = self.get_image('setting_on')
        self.button_image_off = self.get_image('setting_off')

        self.button_image_save_data = self.get_image('save')
        self.button_image_load_data = self.get_image('load')

        self.button_image_data_scatter = self.get_image('scatter')
        self.button_image_data_line = self.get_image('line')

        self.button_image_legend_on = self.get_image('legend_on')
        self.button_image_legend_off = self.get_image('legend_off')

        self.button_image_lin = self.get_image('lin')
        self.button_image_log = self.get_image('log')

        self.button_image_item_sel = self.get_image('item_select')
        self.button_image_item_selected = self.get_image('item_selected')
        self.button_image_item_desel = self.get_image('item_deselect')
        self.button_image_color = self.get_image('color')

    def __update_editor_buttons(self, *args):
        for button in args:
            if button == 'x_grid':
                if self.x_grid.get_line_visibility():
                    self.x_grid_button.config(image = self.button_image_on)
                else:
                    self.x_grid_button.config(image = self.button_image_off)
                if self.scale_type[0] == 'log': self.x_scale_steps.config(state='disabled')
                elif self.scale_type[0] == 'lin': self.x_scale_steps.config(state='normal')
            elif button == 'y_grid':
                if self.y_grid.get_line_visibility(): 
                    self.y_grid_button.config(image=self.button_image_on)
                else: 
                    self.y_grid_button.config(image=self.button_image_off)
                if self.scale_type[1] == 'log': self.y_scale_steps.config(state='disabled')
                elif self.scale_type[1] == 'lin': self.y_scale_steps.config(state='normal')
            elif button == 'x_linlog':              
                if self.x_grid.get_type() == 'lin':
                    self.x_linlog_button.config(image=self.button_image_log)
                elif self.x_grid.get_type() == 'log':
                    self.x_linlog_button.config(image=self.button_image_lin)
            elif button == 'y_linlog': 
                if self.y_grid.get_type() == 'lin':
                    self.y_linlog_button.config(image=self.button_image_log)    
                elif self.y_grid.get_type() == 'log':
                     self.y_linlog_button.config(image=self.button_image_lin)                   
            elif button == 'sel_item': 
                if self.plot_editor_selected_counter == 0: 
                    self.select_item_button.config(image=self.button_image_item_sel)    
                elif self.plot_editor_selected_counter == 1:
                    self.select_item_button.config(image=self.button_image_item_selected)
                elif self.plot_editor_selected_counter == 2:
                    self.select_item_button.config(image=self.button_image_item_desel)
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
        tag_color = self.dataset_find(tag).get_color()

        self.editor_canvas.itemconfig(self.save_data_name_selection, text=tag)
        self.editor_canvas.itemconfig(self.save_data_name_color, fill=tag_color, state='normal')
        self.om_save_variable.set(tag)

    def __update_load_tag(self, *args):
        
        tag = self.om_load_variable.get()
        self.editor_canvas.itemconfig(self.load_data_name_selection, text=tag)

    def __change_plot_type(self):

        if self.load_data_type == 'line':
            self.load_data_type_button.config(image = self.button_image_data_scatter)
            self.load_data_type = 'scatter'
        else:
            self.load_data_type_button.config(image = self.button_image_data_line)
            self.load_data_type = 'line'
        
    def __change_plot_color(self):
        
        self.load_data_color = self.next_plot_color()
        self.load_data_color_button.config(bg = self.load_data_color)

    def __change_plot_legend(self):
        
        self.load_data_legend = False if self.load_data_legend else True
        if self.load_data_legend:
            self.load_data_legend_button.config(image=self.button_image_legend_on)
        else:
            self.load_data_legend_button.config(image=self.button_image_legend_off)

    def __switch_linlog(self, order):
        
        if order == 'x':
            if self.x_grid.get_type() == 'lin': 
                self.set_x_axis('keep', 'keep', axis='log')
            elif self.x_grid.get_type() == 'log': 
                self.set_x_axis('keep', 'keep', axis='lin')
                
        elif order == 'y':
            if self.y_grid.get_type() == 'lin': 
                self.set_y_axis('keep', 'keep', axis='log')
            elif self.y_grid.get_type() == 'log': 
                self.set_y_axis('keep', 'keep', axis='lin')
        
        self.auto_focus()
        self.update_plots()
        self.__update_editor_buttons('x_grid', 'x_linlog', 
                                     'y_grid', 'y_linlog')
        
    def __enable_grid(self, order):
        if order =='x': self.x_grid.invert_line_visibility()
        if order =='y': self.y_grid.invert_line_visibility()
        self.raise_items()
        self.__update_editor_buttons('x_grid', 'y_grid')

    def __change_axis(self, order, direction, value):
        try:
            value = float(value)
            if order == 'x':
                if direction == 'low':
                    lower_x = value
                    upper_x = self.X_axis_numbers.get_upper_axis()
                elif direction == 'high':
                    lower_x = self.X_axis_numbers.get_lower_axis()
                    upper_x = value
                self.set_x_axis(lower_x, upper_x)
            elif order == 'y':
                if direction == 'low':
                    lower_y = value
                    upper_y = self.Y_axis_numbers.get_upper_axis()
                elif direction == 'high':
                    lower_y = self.Y_axis_numbers.get_lower_axis()
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

    ## Item Change

    def __bestFit(self):
        if not self.lineApproximations:
            try: 
                for i in range(3): self.lineApproximations.append(0)
                if self.scale_type[0] == 'lin':  
                    x = self.gen_x_path(50, self.X_axis_numbers.get_lower_axis(), self.X_axis_numbers.get_upper_axis()) 
                elif self.scale_type[0] == 'log':
                    x = self.gen_x_path(50, self.X_axis_numbers.get_lower_axis(), self.X_axis_numbers.get_upper_axis())
                y = [0.1 for i in range(len(x))]
                
                dataset = self.dataset_find('bFit')
                for i in range(len(x)): dataset.addPoint([x[i], y[i]])

                markSize = dataset.getMarkerSize()/2
                colors = self.get_color(dataset)
                num = self.dataset_find('bFit')


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
            
            # If Legend, autosets new legend position
            legend_index = self.find_legend(item=self.plot_editor_selected_item)
            content = self.select_item_text_input.get()
            if legend_index != None:
                for item in self.data_series:
                    if item.get_legend() == self.plot.itemcget(self.legend_content[legend_index], 'text'):
                        item.set_legend(content)
                        self.update_legend_offsets()
                        self.reposition_legend()

            self.plot.itemconfig(self.plot_editor_selected_item, text=content)
                