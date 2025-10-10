# presenter.py
class Presenter:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo 
        self.vista.set_presenter(self)
        self.vista.connect_signals()

    def iniciar(self):
        print("PRESENTER: Iniciando aplicación...")
        self.cargar_datos_principales()

    def cargar_datos_principales(self):
        gastos = self.modelo.get_gastos()
        amigos = self.modelo.get_amigos()

        self.vista.mostrar_gastos(gastos)
        self.vista.mostrar_amigos(amigos)

        print("PRESENTER: Datos iniciales cargados en la vista.")

    def on_add_gasto_clicked(self, widget):
        print("PRESENTER: El usuario ha hecho clic en 'Añadir Gasto'.")
        #falta por añadir el muestreo del dialogo de añadir gasto