import tkinter as tk
from Plot import Plot
import numpy as np

class Main():

    def __init__(self):

        self.root = tk.Tk()
        self.root.withdraw()
        self.plot_canvas = Plot(1000, 600, 'wtf')

        a = np.random.uniform(0,1,100)
        b = np.random.uniform(0,90,100)
        c = np.random.uniform(0,1,100)
        d = np.random.uniform(0,90,100)

        self.plot_canvas.graph(b,a, 'testData', 'show')
        self.plot_canvas.graph(d,c, 'testData2')
        self.plot_canvas.set_legend(['a', 'b'], [1,2], 'NE')
        self.plot_canvas.set_title('Tada')
        self.plot_canvas.set_labels('xxx','yyy')
        self.plot_canvas.set_x_axis(0,100)
        self.plot_canvas.set_y_axis(0,1)
        self.plot_canvas.colorbar(['red','green','blue'],[0,0.5,1], 3, 'cb')
        self.plot_canvas.add_text([3, 0.05], 'tatat', 'tex1')
        self.plot_canvas.update_text('wopp wopp', 'tex1')

        self.mainloop()

    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()
