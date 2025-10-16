#main.py
import sys
from view import App, VistaPrincipal
from model import Model
from presenter import Presenter

def main():
    modelo = Model()
    app = App(modelo)

    def on_activate(application):
        win = VistaPrincipal(application=application)
        presentador = Presenter(win, modelo)
        presentador.iniciar()
        win.present()
    
    app.connect('activate', on_activate)
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())