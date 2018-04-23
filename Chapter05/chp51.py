#Again, here we import the Gtk module
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#From here, we define our own class, namely TwoClicks.
#This is a sub-class of Gtk.Window
class TwoClicks(Gtk.Window):
    
    #Instantiation operation will creates an empty object
    #Therefore, python3 uses __init__() to *construct* an object
    #__init__() will be automatically invoked when the object is being created!
    #You can call this the constructor in Python3
    #Noted that *self* here indicates the reference of the object created from this class
    #Anything below starting with self.X refers to the local function or variables of the object itself!
    def __init__(self):
        
        #In here, we are essentially constructing a Gtk.Window object
        #And parsing the information title="Hello world" to the constructor of Gtk.Window
        #Therefore, the window will have a title of "Hello World"
        Gtk.Window.__init__(self, title="Hello World")
        
        #Since we have two click buttons, we created a horizontally oriented box container
        #with 20 pixels placed in between children - the two click buttons
        self.box = Gtk.Box(spacing=100)
        
        #This assigns the box to become the child of the top-level window
        self.add(self.box)
        
        #Here we create the first button - click1, with the title "Print once!" on top of it
        self.click1 = Gtk.Button(label="Print once!")
        
        #We assign a handler and connect the *Event* (clicked) with the *callback/function* (on_click1)
        #Noted that, we are now calling the function of the object itself
        #Therefore we are using *self.onclick1 
        self.click1.connect("clicked", self.on_click1)
        
        #Gtk.Box.pack_start() has a directionality here, it positions widgets from left to right!
        self.box.pack_start(self.click1, True, True, 0)
        
        #The same applies to click 2, except that we connect it with a different function
        #which prints Hello World 5 times!
        self.click2 = Gtk.Button(label="Print 5 times!")
        self.click2.connect("clicked", self.on_click2)
        self.box.pack_start(self.click2, True, True, 0)
    
    #Here defines a function on_click1 in the Class TwoClicks
    #This function will be triggered when the button "Print once!" is clicked
    def on_click1(self, widget):
        print("Hello World")
    
    #Here defines a function on_click2 in the Class TwoClicks
    #This function will be triggered when the button "Print 5 times!" is clicked
    def on_click2(self, widget):
        for i in range(0,5):
            print("Hello World")

#Here we instantiate an object, namely window
window = TwoClicks()
#Here we want the window to be close when the user click on the close button
window.connect("delete-event", Gtk.main_quit)
#Here we display the window!
window.show_all()
#This tells the code to run the main loop until Gtk.main_quit is called
Gtk.main()
