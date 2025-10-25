#main.py
import sys
import signal
from view import App, VistaPrincipal
from model import Model
from presenter import Presenter

def main():
    def signal_handler(sig, frame):
        print("\nCerrando aplicación...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

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