#main.py
import sys
from view import App, VistaPrincipal
from model import Model
from presenter import Presenter

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