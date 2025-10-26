#main.py
import sys
import signal
from view import App, VistaPrincipal
from model import Model
from presenter import Presenter

#inicializacion sistema internacionalizacion
import locale
import gettext 
import os 

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    print("Locale no soportado por el sistema, usando 'en_US.UTF-8'")
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

APP_NAME = "splitwithme"
LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'po')

gettext.bindtextdomain(APP_NAME, LOCALE_DIR)   
gettext.textdomain(APP_NAME) 
_ = gettext.gettext

def main():
    # App ya no necesita el modelo
    app = App()

    def on_activate(application):
        modelo = Model()
        win = VistaPrincipal(application=application)
        presentador = Presenter(win, modelo)
        
        presentador.iniciar()
        
        win.present()
    
    app.connect('activate', on_activate)
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())