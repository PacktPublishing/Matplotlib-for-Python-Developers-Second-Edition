#Same old, importing Gtk module, we are also importing some other stuff this time
#such as numpy and the backends of matplotlib
import gi, numpy as np, matplotlib.cm as cm
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#From here, we are importing some essential backend tools from matplotlib
#namely the NavigationToolbar2GTK3 and the FigureCanvasGTK3Agg
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure

#Some numpy functions to create the polar plot
from numpy import arange, pi, random, linspace

#Here we define our own class MatplotlibEmbed
#By simply instantiating this class through the __init__() function,
#A polar plot will be drawn by using Matplotlib, and embedded to GTK3+ window
class MatplotlibEmbed(Gtk.Window):

    #Instantiation
    def __init__(self):
        #Creating the Gtk Window
        Gtk.Window.__init__(self, title="Embedding Matplotlib")
        #Setting the size of the GTK window as 400,400
        self.set_default_size(400,400)

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

        #Here comes the magic, a Vbox is created
        #VBox is a containder subclassed from Gtk.Box, and it organizes its child widgets into a single column
        self.vbox = Gtk.VBox()
        #After creating the Vbox, we have to add it to the window object itself!
        self.add(self.vbox)

        #Creating Canvas which store the matplotlib figure
        self.canvas = FigureCanvas(self.fig)  # a Gtk.DrawingArea
        # Add canvas to vbox
        self.vbox.pack_start(self.canvas, True, True, 0)

        # Creating toolbar, which enables the save function!
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.vbox.pack_start(self.toolbar, False, False, 0)

#The code here should be self-explanatory by now! Or refer to earlier examples for in-depth explanation
window = MatplotlibEmbed()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
