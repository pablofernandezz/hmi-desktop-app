# presenter.py
from datetime import date

class Presenter:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo 

    def iniciar(self):
        print("PRESENTER: Iniciando aplicación...")
        self.vista.connect_signals()
        self.cargar_datos_principales()

    def cargar_datos_principales(self):
        self.vista.show_loading(True)
        try:
            gastos = self.modelo.get_gastos()
            amigos = self.modelo.get_amigos()
        
            if gastos is None or amigos is None:
                print("PRESENTER: Error de conexion detectado. Mostrando pantalla de error.")
                self.vista.show_connection_error(True)
            else:
                self.vista.show_connection_error(False)
                self.vista.mostrar_gastos(gastos)
                self.vista.mostrar_amigos(amigos) 
            print("PRESENTER: Datos iniciales cargados en la vista.")
        finally:
             self.vista.show_loading(False)

    def on_retry_clicked(self, widget):
        print("PRESENTER: El usuario ha pulsado Reintentar.")
        self.cargar_datos_principales() 

    def on_add_gasto_clicked(self):
        print("PRESENTER: El usuario quiere añadir un nuevo gasto.")
        # Primero obtenemos todos los amigos para mostrarlos en el diálogo
        todos_amigos = self.modelo.get_amigos()
        if todos_amigos is None:
            self.vista.show_connection_error(True)
            return
        
        def al_aceptar(datos_gasto):
        # obtenemos datos de gasto actual
        self.vista.show_loading(True)
        try:
            #Extraer datos del gasto y amigos a asociar
            amigos_a_asociar_ids = datos_gasto.pop('friend_ids', [])
            datos_gasto['date'] = date.today().strftime("%Y-%m-%d")

            #Crear el gasto
            nuevo_gasto = self.modelo.create_gasto(datos_gasto)
            if nuevo_gasto:
                print(f"PRESENTER: Gasto creado con ID: {nuevo_gasto.id}")
                #Asociar amigos a gasto
                for amigo_id in amigos_a_asociar_ids:
                    self.modelo.add_amigo_a_gasto(nuevo_gasto.id, amigo_id)
                self.cargar_datos_principales()
            else:
                self.vista.show_loading(False)
                self.vista.show_connection_error(True)
        finally:   
            self.vista.show_loading(False)

        self.vista.mostrar_dialogo_gasto(
            todos_amigos=todos_amigos, 
            on_accept_callback=al_aceptar
        )

    def on_modify_gasto_clicked(self, gasto_id: int, datos_nuevos: dict):
        print(f"PRESENTER: El usuario quiere modificar el gasto {gasto_id}.")
        self.vista.show_loading(True)
        try:
            gasto_actual = self.modelo.get_gasto_details(gasto_id)
            if not gasto_actual:
                self.vista.show_connection_error(True)
                return
            
            datos_gasto_basico = {
                "description": datos_nuevos["description"],
                "amount": datos_nuevos["amount"],
                "date": gasto_actual.date
            }
            if self.modelo.update_gasto(gasto_id, datos_gasto_basico):
                self.cargar_datos_principales()
            else:
                self.vista.show_loading(False)
                self.vista.show_connection_error(True)
        finally:
            self.vista.show_loading(False)
    

    def on_delete_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere eliminar el gasto {gasto_id}.")
        self.vista.show_confirm_delete_dialog(gasto_id)

    def on_confirm_delete(self, gasto_id: int):
        self.vista.show_loading(True)
        try:
            if self.modelo.delete_gasto(gasto_id):
                self.cargar_datos_principales()
            else:
                self.vista.show_loading(False)
                self.vista.show_connection_error(True)
        finally:
            self.vista.show_loading(False)