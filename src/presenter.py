# presenter.py
from datetime import date

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


# --- Logica para ver detalles

    def on_retry_clicked(self, widget):
        print("PRESENTER: El usuario ha pulsado Reintentar.")
        self.cargar_datos_principales() 

    def on_gasto_row_activated(self, listbox, row):
        gasto_id = row.gasto_id
        self.on_details_gasto_clicked(gasto_id)

    def on_amigo_row_activated(self, listbox, row):
        amigo_id = row.amigo_id
        self.on_details_amigo_clicked(amigo_id)

    def on_details_gasto_clicked(self, gasto_id: int, row_widget):
        print(f"PRESENTER: Usuario quiere ver detalles del gasto {gasto_id}")
        gasto_con_detalles = self.modelo.get_gasto_details(gasto_id)
        if gasto_con_detalles:
            row_widget.show_details_view(gasto_con_detalles)
        else:
            self.vista.show_connection_error(True)


    def on_details_amigo_clicked(self, amigo_id: int, row_widget):
        print(f"PRESENTER: Usuario quiere ver detalles del amigo {amigo_id}")
        amigo = self.modelo.get_amigo_details(amigo_id)
        gastos_asociados = self.modelo.get_gastos_por_amigo(amigo_id)
        if amigo and gastos_asociados is not None:
            row_widget.show_details_view(amigo, gastos_asociados)
        else:
            self.vista.show_connection_error(True)


# --- Logica para añadir, modificar y eliminar gasto
    def on_add_gasto_clicked(self):
        print(f"PRESENTER: El usuario quiere añadir un nuevo gasto.")
        amigos = self.modelo.get_amigos()
        if amigos is None:
            self.vista.show_connection_error(True); return

        def al_aceptar(datos_gasto):
            datos_gasto['date'] = date.today().strftime("%Y-%m-%d")
            print(f"PRESENTER: Enviando al modelo los datos completos: {datos_gasto}")
            if self.modelo.create_gasto_with_friends(datos_gasto):
                self.cargar_datos_principales()
            else:
                self.vista.show_connection_error(True)

        self.vista.mostrar_dialogo_gasto(amigos, al_aceptar)
    
    def on_modify_gasto_clicked(self, gasto_id: int, row_widget):
        print(f"PRESENTER: El usuario quiere modificar el gasto {gasto_id}.")
        gasto_actual = self.modelo.get_gasto_details(gasto_id)
        todos_amigos = self.modelo.get_amigos()
        if gasto_actual and todos_amigos:
            # Le pasamos a la fila los datos que necesita para construir su formulario
            row_widget.update_edit_view(gasto_actual, todos_amigos)
        else:
            self.vista.show_connection_error(True)

    def on_save_changes_clicked(self, gasto_original, new_desc, new_amount, amigos_checked_status):
        # Lógica de guardado que ya tenías, ahora en un método dedicado
        ids_amigos_originales = {amigo.id for amigo in gasto_original.friends}
        ids_amigos_nuevos = {amigo_id for amigo_id, is_checked in amigos_checked_status.items() if is_checked}
        
        ids_anadir = ids_amigos_nuevos - ids_amigos_originales
        ids_quitar = ids_amigos_originales - ids_amigos_nuevos

        for amigo_id in ids_anadir: self.modelo.add_amigo_a_gasto(gasto_original.id, amigo_id)
        for amigo_id in ids_quitar: self.modelo.remove_amigo_de_gasto(gasto_original.id, amigo_id)

        datos_gasto_basico = {"description": new_desc, "amount": new_amount, "date": gasto_original.date}
        self.modelo.update_gasto(gasto_original.id, datos_gasto_basico)
        
        self.cargar_datos_principales()

    def on_delete_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere eliminar el gasto {gasto_id}.")
        self.vista.show_confirm_delete_dialog(gasto_id)

    def on_confirm_delete(self, gasto_id: int):
        self.vista.show_loading(True)
        try:
            # La vista llama a este método solo si el usuario confirma
            if self.modelo.delete_gasto(gasto_id):
                self.cargar_datos_principales()
            else:
                self.vista.show_loading(False)
                self.vista.show_connection_error(True)
        finally:
            self.vista.show_loading(False)