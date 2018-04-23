#Same old, importing Gtk module, we are also importing some other stuff this time
#such as numpy and the backends of matplotlib
import gi, numpy as np, matplotlib.cm as cm
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#From here, we are importing some essential backend tools from matplotlib
#namely the NavigationToolbar2GTK3 and the FigureCanvasGTK3Agg
from numpy import random
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

#Here we created a class named DrawPoints
class DrawPoints:
    
    #Upon initiation, we create 4 randomized numpy array, those are for the coordinates, colors and size of dots
    #on the scatter plot. After that we create a figure object, put in two subplots and create a canvas to store
    #the figure.
    def __init__(self):
        #Namely we are creating 20 dots, therefore n = 20
        self.n = 20
        #X and Y coordinates
        self.xrand = random.rand(1,self.n)*10
        self.yrand = random.rand(1,self.n)*10
        #Sizes
        self.randsize = random.rand(1,self.n)*200
        #Colors
        self.randcolor = random.rand(self.n,3)
        
        #Here creates the figure, with a size 10x10 and resolution of 80dpi
        self.fig = Figure(figsize=(10,10), dpi=80)
        #Stating that we are creating two plots side by side and adding 
        #self.ax as the first plot by add_subplot(121)
        self.ax = self.fig.add_subplot(121)
        #Adding the second subplot by stating add_subplot(122)
        self.axzoom = self.fig.add_subplot(122)
        #Create a canvas to store the figure object
        self.canvas = FigureCanvas(self.fig)
        
    #Here draw the scatterplot on the left
    def draw(self):
        #Here is the key - cla(), when we invoke the draw() function, we have to clear the
        #figure and redraw it again
        self.ax.cla()
        #Setting the elements of the left subplot, in this case - grid
        self.ax.grid(True)
        #Set the maximum value of X and Y-axis in the left subplot
        self.ax.set_xlim(0,10)
        self.ax.set_ylim(0,10)
        #Draw the scatter plot with the randomized numpy array that we created earlier in __init__(self)
        self.ax.scatter(self.xrand, self.yrand, marker='o', s=self.randsize, c=self.randcolor, alpha=0.5)
    
    #This zoom function is invoked by updatezoom() function outside of the class Drawpoints
    #This function is responsible for things:
    #1. Update X and Y coordinates based on the click
    #2. invoke the draw() function to redraw the plot on the left, this is essential to update the position
    # of the grey rectangle 
    #3. invoke the drawzoom() function below, which will "Zoom-in" the designated area by the grey rectangle
    # and will redraw the subplot on the right based on the updated X & Y coordinates
    #4. draw a transparent grey rectangle based on the mouse click on the left subplot
    #5. Update the canvas
    def zoom(self, x, y):
        #Here updates the X & Y coordinates
        self.x = x
        self.y = y
        #invoke the draw() funciton to update the subplot on the left
        self.draw()
        #invoke the drawzoom() function to update the subplot on the right
        self.drawzoom()
        #Draw the transparent grey rectangle at the subplot on the left
        self.ax.add_patch(Rectangle((x - 1, y - 1), 2, 2, facecolor="grey", alpha=0.2))
        #Update the canvas
        self.fig.canvas.draw()
    
    #This drawzoom function is being called in the zoom funciton right above.
    #The idea is that, when the user picked a region (rectangle) to zoom, we need to redraw the zoomed panel,
    #which is the subplot on the right
    def drawzoom(self):
        #Again, we use the cla() function to clear the figure, and getting ready for a redraw!
        self.axzoom.cla()
        #Setting the grid
        self.axzoom.grid(True)
        #Do not be confused! Remeber that we invoke this function from zoom, therefore self.x and self.y
        #are already updated in that function. In here, we are simply changing the X & Y-axis minimum and 
        #maximum value, and redraw the graph without changing any element!
        self.axzoom.set_xlim(self.x-1, self.x+1)
        self.axzoom.set_ylim(self.y-1, self.y+1)
        #By changing the X & Y-axis minimum and maximum value, the dots that are out of range will automatically
        #disappear!
        self.axzoom.scatter(self.xrand, self.yrand, marker='o', s=self.randsize*5, c=self.randcolor, alpha=0.5)
    

def updatecursorposition(event):
    '''When cursor inside plot, get position and print to statusbar'''
    if event.inaxes:
        x = event.xdata
        y = event.ydata
        statbar.push(1, ("Coordinates:" + " x= " + str(round(x,3)) + "  y= " + str(round(y,3))))

def updatezoom(event):
    '''When mouse is right-clicked on the canvas get the coordiantes and send them to points.zoom'''
    if event.button!=1: return
    if (event.xdata is None): return
    x,y = event.xdata, event.ydata
    points.zoom(x,y)

    
#Readers should be familiar with this now, here is the standard opening of the Gtk.Window()
window = Gtk.Window()
window.connect("delete-event", Gtk.main_quit)
window.set_default_size(800, 500)
window.set_title('Interactive zoom')

#Creating a vertical box, will have the canvas, toolbar and statbar being packed into it from top to bottom
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
#Adding the vertical box to the window
window.add(box)

#Instantiate the object points from the Class DrawPoints()
#Remember that at this point, __init__() of DrawPoints() are invoked upon construction!
points = DrawPoints()
#Invoke the draw() function in the object points
points.draw()

#Packing the canvas now to the vertical box
box.pack_start(points.canvas, True, True, 0)

#Creating and packing the toolbar to the vertical box
toolbar = NavigationToolbar(points.canvas, window)
box.pack_start(toolbar, False, True, 0)

#Creating and packing the statbar to the vertical box
statbar = Gtk.Statusbar()
box.pack_start(statbar, False, True, 0)

#Here is the magic that makes it happens, we are using mpl_connect to link the event and the canvas!
#'motion_notify_event' is responsible for the mouse motion sensing and position updating
points.fig.canvas.mpl_connect('motion_notify_event', updatecursorposition)
#'button_press_event' is slightly misleading, in fact it is referring to the mouse button being pressed, 
#instead of a GTK+3 button being pressed in this case
points.fig.canvas.mpl_connect('button_press_event', updatezoom)

window.show_all()
Gtk.main()
