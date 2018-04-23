#In here, we import the GTK module in order to access GTK+3's classes and functions
#We want to make sure we are importing GTK+3 and not any other version of the library
#Therefore we require_version('Gtk','3.0')
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
#This line uses the GTK+3 functions and creates an empty window
window = Gtk.Window(title="Hello World!")
#We created a handler that connects window's delete event to ensure the application
#is terminated if we click on the close button
window.connect("destroy",Gtk.main_quit)
#Here we display the window
window.show_all()
#This tells the code to run the main loop until Gtk.main_quit is called
Gtk.main()
