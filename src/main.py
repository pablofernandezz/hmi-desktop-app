import sys
from view import App 
from model import Model 

def main():
    modelo = Model()

    app = App(modelo)

    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())