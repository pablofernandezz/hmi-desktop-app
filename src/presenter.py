from datetime import date
from model import Gasto
from gi.repository import GLib

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
                print("PRESENTER: Error de conexión detectado. Mostrando pantalla de error.")
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

    def on_refresh_clicked(self):
        print("PRESENTER: El usuario ha pulsado Refrescar.")
        self.cargar_datos_principales()

    def on_gasto_row_activated(self, listbox, row):
        gasto_id = row.gasto_id
        self.on_details_gasto_clicked(gasto_id, row)

    def on_details_gasto_clicked(self, gasto_id: int, row_widget: 'GastoRow'):
        print(f"PRESENTER: Usuario quiere ver detalles del gasto {gasto_id}")
        gasto_con_detalles = self.modelo.get_gasto_details(gasto_id)
        if gasto_con_detalles:
            row_widget.show_details_view(gasto_con_detalles)
        else:
            self.vista.show_connection_error(True)

    def on_add_gasto_clicked(self):
        print("PRESENTER: El usuario quiere añadir un nuevo gasto.")
        amigos = self.modelo.get_amigos()
        if amigos is None:
            self.vista.show_connection_error(True)
            return

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
            row_widget.update_edit_view(gasto_actual, todos_amigos)
        else:
            self.vista.show_connection_error(True)

    def on_save_changes_clicked(self, gasto_original, new_desc, new_amount, amigos_checked_status):
        print(f"PRESENTER: Guardando cambios para el gasto {gasto_original.id}")
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
            if self.modelo.delete_gasto(gasto_id):
                self.cargar_datos_principales()
            else:
                self.vista.show_loading(False)
                self.vista.show_connection_error(True)
        finally:
            self.vista.show_loading(False)
    
    def on_amigo_row_activated(self, listbox, row):
        amigo_id = row.amigo.id
        self.on_details_amigo_clicked(amigo_id, row)

    def on_details_amigo_clicked(self, amigo_id: int, row_widget: 'AmigoRow'):
        print(f"PRESENTER: Usuario quiere ver detalles del amigo {amigo_id}")
        
        amigo_con_detalles = self.modelo.get_amigo_details(amigo_id)
        gastos_asociados = self.modelo.get_gastos_por_amigo(amigo_id)

        if amigo_con_detalles is not None:
            row_widget.show_details_view(amigo_con_detalles, gastos_asociados)
        else:
            self.vista.show_connection_error(True)

    def on_open_aporte_dialog_clicked(self, gasto: Gasto):
        print(f"PRESENTER: Abriendo diálogo de aporte para el gasto {gasto.id}")
        
        def al_aceptar_aporte(amigo_id, amount):
            self.on_make_payment_clicked(gasto.id, amigo_id, amount)
            
        self.vista.mostrar_dialogo_aporte(gasto.friends, al_aceptar_aporte)

    def on_make_payment_clicked(self, gasto_id: int, amigo_id: int, amount: float):
        print(f"PRESENTER: Procesando pago de {amount}€ del amigo {amigo_id} para el gasto {gasto_id}")
        
        success = self.modelo.make_payment_for_friend(gasto_id, amigo_id, amount)
        
        if success:
            self.cargar_datos_principales()

            def reopen_details_with_fresh_data():
                row_widget_refrescada = self.vista.get_gasto_row_by_id(gasto_id)
                if row_widget_refrescada:
                    print(f"PRESENTER: Forzando reapertura de detalles para el gasto {gasto_id} con datos frescos.")
                    row_widget_refrescada.on_details_clicked(None)
            
            GLib.idle_add(reopen_details_with_fresh_data)
        else:
            self.vista.show_connection_error(True)
            
    def on_add_aporte_clicked(self, gasto_id: int, row_widget: 'GastoRow'):
        print(f"PRESENTER: Petición para añadir aporte al gasto ID {gasto_id}")
        self.vista.show_loading(True)
        try:
            gasto_completo = self.modelo.get_gasto_details(gasto_id)

            if gasto_completo:
                importe_restante = gasto_completo.amount - gasto_completo.credit_balance
                importe_maximo_aporte = max(0.01, importe_restante)

                row_widget.show_add_aporte_view(
                    gasto_completo.id,
                    gasto_completo.friends,
                    importe_maximo_aporte
                )
            else:
                self.vista.show_connection_error(True)
        finally:
            self.vista.show_loading(False)

    def on_save_new_aporte(self, gasto_id: int, amigo_id: int, amount: float):
        print(f"PRESENTER: Guardando nuevo aporte para gasto {gasto_id}")
        self.vista.show_loading(True)
        try:
            if self.modelo.add_aporte_a_gasto(gasto_id, amigo_id, amount):
                self.cargar_datos_principales()
            else:
                self.vista.show_connection_error(True)
        finally:
            self.vista.show_loading(False)