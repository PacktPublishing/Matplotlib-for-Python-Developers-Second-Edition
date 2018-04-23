#Same old, importing Gtk module, we are also importing some other stuff this time
#such as numpy and the backends of matplotlib
import gi, numpy as np, matplotlib.cm as cm
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from matplotlib.figure import Figure
from numpy import arange, pi, random, linspace
import matplotlib.cm as cm
#Possibly this rendering backend is broken currently
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

#New class, here is to invoke Gtk.main_quit() when the window is being destroyed
#Necessary to quit the Gtk.main()
class Signals:
    def on_window1_destroy(self, widget):
        Gtk.main_quit()

class MatplotlibEmbed(Gtk.Window):

    #Instantiation, we just need the canvas to store the figure!
    def __init__(self):

        #Readers should find it familiar, as we are creating a matplotlib figure here with a dpi(resolution) 100
        self.fig = Figure(figsize=(5,5), dpi=100)
        #The axes element, here we indicate we are creating 1x1 grid and putting the subplot in the only cell
        #Also we are creating a polar plot, therefore we set projection as 'polar
        self.ax = self.fig.add_subplot(111, projection='polar')

        #Here, we borrow one example shown in the matplotlib gtk3 cookbook
        #and show a beautiful bar plot on a circular coordinate system
        self.theta = linspace(0.0, 2 * pi, 30, endpoint=False)
        self.radii = 10 * random.rand(30)
        self.width = pi / 4 * random.rand(30)
        self.bars = self.ax.bar(self.theta, self.radii, width=self.width, bottom=0.0)

        #Here defines the color of the bar, as well as setting it to be transparent
        for r, bar in zip(self.radii, self.bars):
            bar.set_facecolor(cm.jet(r / 10.))
            bar.set_alpha(0.5)
        #Here we generate the figure
        self.ax.plot()

        #Creating Canvas which store the matplotlib figure
        self.canvas = FigureCanvas(self.fig)  # a Gtk.DrawingArea

#Here is the magic, we create a GTKBuilder that reads textual description of a user interface
#and instantiates the described objects
builder = Gtk.Builder()
#We ask the GTKBuilder to read the file and parse the information there
builder.add_objects_from_file('/Users/aldrinyim/Dropbox/Matplotlib for Developer/Jupyter notebook/ch05/window1_glade.glade', ('window1', '') )
#And we connect the terminating signals with Gtk.main_quit()
builder.connect_signals(Signals())

#We create the first object window1
window1 = builder.get_object('window1')
#We create the second object scrollwindow
scrolledwindow1 = builder.get_object('scrolledwindow1')

#Instantiate the object and start the drawing!
polar_drawing = MatplotlibEmbed()
#Add the canvas to the scrolledwindow1 object
scrolledwindow1.add(polar_drawing.canvas)

#Show all and keep the Gtk.main() active!
window1.show_all()
Gtk.main()
