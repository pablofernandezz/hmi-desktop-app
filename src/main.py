#main.py

import sys
import signal
import gettext
import locale
from pathlib import Path

from view import App, VistaPrincipal
from model import Model
from presenter import Presenter

def main():
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error as e:
        print(f"Advertencia: No se pudo establecer el locale del sistema. Se usará el por defecto. Error: {e}")

    APP_NAME = "splitwithme"
    LOCALE_DIR = Path(__file__).parent.parent / "locale"
    gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
    gettext.textdomain(APP_NAME)
    
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