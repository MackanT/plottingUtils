import tkinter as tk
from Plot import Plot
import numpy as np
import timeit

class Main():

    def __init__(self):

        self.root = tk.Tk()
        self.root.withdraw()
        self.plot_canvas = Plot(1000, 600, 'Testing Utils')

        a = np.random.uniform(0,90,100)
        b = np.random.uniform(0,90,100)
        c = np.random.uniform(0,90,100)
        d = np.random.uniform(0,90,100)

        self.plot_canvas.set_legend(['a', 'b'], [1,2], 'SW')
        self.plot_canvas.set_title('Schkii Schkii')
        self.plot_canvas.set_labels('xxx','yyy')
        self.plot_canvas.graph(b,a, 'testData', 'show', 'scatter')
        # self.plot_canvas.graph(d,c, 'testData2')
        # self.plot_canvas.set_x_axis(0,110)
        # self.plot_canvas.set_y_axis(-0.1,100.2)
        
        self.plot_canvas.add_text([3, 0.05], 'tatat', 'tex1')
        self.plot_canvas.update_text('Hahlelelha', 'tex1')
        self.plot_canvas.set_axis_scale_type('digit')

        self.test_code()
        # print(timeit.timeit(self.test_code, number=10000))

        self.mainloop()

    def test_code(self):
        self.plot_canvas.add_colorbar('yellow','green',[0,0.5,1])

    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()
