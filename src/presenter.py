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
        gastos = self.modelo.get_gastos()
        amigos = self.modelo.get_amigos()
        
        self.vista.show_loading(False)

        if gastos is None or amigos is None:
            print("PRESENTER: Error de conexion detectado. Mostrando pantalla de error.")
            self.vista.show_connection_error(True)
        else:
            self.vista.show_connection_error(False)
            self.vista.mostrar_gastos(gastos)
            self.vista.mostrar_amigos(amigos) 
        print("PRESENTER: Datos iniciales cargados en la vista.")

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
        
# --- Logica para añadir, modificar y eliminar gasto
    def on_add_gasto_clicked(self):
        print(f"PRESENTER: El usuario quiere añadir un nuevo gasto.")

        def al_aceptar(datos_gasto):
            datos_gasto['date'] = date.today().strftime("%Y-%m-%d")
            datos_gasto.pop('friend_ids', None) 
            print(f"PRESENTER: Enviando al modelo los datos completos: {datos_gasto}")

            if self.modelo.create_gasto(datos_gasto):
                self.cargar_datos_principales()

        self.vista.mostrar_dialogo_gasto(
            amigos=[], 
            on_accept_callback=al_aceptar
        )
    
    # ---CAMBIOS A PARTIR DE AQUÍ---
    def on_modify_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere modificar el gasto {gasto_id}.")
        # obtenemos datos de gasto actual
        gasto_actual = self.modelo.get_gasto_details(gasto_id)
        todos_amigos = self.modelo.get_amigos()

        if not gasto_actual or not todos_amigos:
            print("PRESENTER: No se pudieron obtener los datos para modificar el gasto.")
            return
        
        def al_aceptar_modificacion(datos_nuevos):
            ids_amigos_originales = {amigo.id for amigo in gasto_actual.friends}
            ids_amigos_nuevos = set(datos_nuevos['friend_ids'])

            #balance nuevos de amigos
            ids_anadir = ids_amigos_nuevos - ids_amigos_originales
            ids_quitar = ids_amigos_originales - ids_amigos_nuevos

            print(f"PRESENTER: Amigos a añadir: {ids_anadir}")
            print(f"PRESENTER: Amigos a quitar: {ids_quitar}")

            #añadir/quitar amigos del gasto
            for amigo_id in ids_anadir:
                self.modelo.add_amigo_a_gasto(gasto_id, amigo_id)
            for amigo_id in ids_quitar:
                self.modelo.remove_amigo_de_gasto(gasto_id, amigo_id)

            #actualizar datos básicos del gasto
            datos_gasto_bassico = {
                "description": datos_nuevos["description"],
                "amount": datos_nuevos["amount"],
                "date": gasto_actual.date  # La fecha no se modifica
            }
            
            #actualizar gasto
            self.modelo.update_gasto(gasto_id, datos_gasto_bassico)
            self.cargar_datos_principales()

        self.vista.mostrar_dialogo_gasto(
            todos_amigos,
            on_accept_callback=al_aceptar_modificacion,
            gasto_existente=gasto_actual
        )

    def on_delete_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere eliminar el gasto {gasto_id}.")
        self.vista.show_confirm_delete_dialog(gasto_id)

    def on_confirm_delete(self, gasto_id: int):
        # La vista llama a este método solo si el usuario confirma
        if self.modelo.delete_gasto(gasto_id):
            self.cargar_datos_principales()