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
        self.vista.show_loading(True)
        gastos = self.modelo.get_gastos()
        amigos = self.modelo.get_amigos()
        self.vista.mostrar_gastos(gastos)
        self.vista.mostrar_amigos(amigos)
        self.vista.show_loading(False)
        print("PRESENTER: Datos iniciales cargados en la vista.")

# --- Logica para ver detalles

    def on_details_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: Usuario quiere ver detalles del gasto {gasto_id}")
        self.vista.show_loading(True)
        gasto = self.modelo.get_gasto_details(gasto_id)
        self.vista.show_loading(False)
        if gasto:
            self.vista.show_gasto_details(gasto)
        else:
            print(f"PRESENTER: No se pudo obtener la información del gasto {gasto_id}.")

    def on_details_amigo_clicked(self, amigo_id: int):
        print(f"PRESENTER: Usuario quiere ver detalles del amigo {amigo_id}")
        self.vista.show_loading(True)
        amigo = self.modelo.get_amigo_details(amigo_id)
        gastos_asociados = self.modelo.get_gastos_por_amigo(amigo_id)
        self.vista.show_loading(False)
        if amigo and gastos_asociados is not None:
            self.vista.show_amigo_details(amigo, gastos_asociados)
        else:
            print(f"PRESENTER: No se pudo obtener la información del amigo {amigo_id}.")
        
# --- Logica para añadir, modificar y eliminar gasto (por implementar)
    def on_add_gasto_clicked(self, widget):
        print("PRESENTER: El usuario ha hecho clic en 'Añadir Gasto'.")
        #falta por añadir el muestreo del dialogo de añadir gasto
    
    def on_modify_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere modificar el gasto {gasto_id}.")

    def on_delete_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere eliminar el gasto {gasto_id}.")