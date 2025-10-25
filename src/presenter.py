from datetime import date
from model import Gasto
import threading

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
        def worker():
            gastos = self.modelo.get_gastos()
            amigos = self.modelo.get_amigos()
            self.vista.run_on_ui_thread(self.vista.update_initial_data, gastos, amigos)

        self.vista.show_loading(True)
        thread = threading.Thread(target=worker)
        thread.start()

    def on_retry_clicked(self, widget):
        print("PRESENTER: El usuario ha pulsado Reintentar.")
        self.cargar_datos_principales() 

    def on_refresh_clicked(self):
        print("PRESENTER: El usuario ha pulsado Refrescar.")
        self.cargar_datos_principales()

    def on_gasto_row_activated(self, listbox, row):
        gasto_id = row.gasto_id
        self.on_details_gasto_clicked(gasto_id)

    def on_details_gasto_clicked(self, gasto_id: int):
        def worker():
            gasto_con_detalles = self.modelo.get_gasto_details(gasto_id)
            amigos = self.modelo.get_amigos()
            self.vista.run_on_ui_thread(self.vista.show_gasto_details_or_error, gasto_id, gasto_con_detalles, amigos)

        self.vista.show_row_loading(gasto_id, True)
        thread = threading.Thread(target=worker)
        thread.start()

    def on_add_gasto_clicked(self):
        def worker():
            amigos = self.modelo.get_amigos()
            self.vista.run_on_ui_thread(ui_update, amigos)

        def ui_update(amigos):
            if amigos is None:
                self.vista.show_connection_error(True)
                self.vista.show_loading(False)
                return
            
            self.vista.show_loading(False)
            self.vista.mostrar_dialogo_gasto(amigos, self._on_accept_new_gasto)
        
        self.vista.show_loading(True)
        thread = threading.Thread(target=worker)
        thread.start()

    def _on_accept_new_gasto(self, datos_gasto):
        def worker():
            datos_gasto['date'] = date.today().strftime("%Y-%m-%d")
            success = self.modelo.create_gasto_with_friends(datos_gasto)
            self.vista.run_on_ui_thread(self.vista.reload_data_or_error, success)

        self.vista.show_loading(True)
        thread = threading.Thread(target=worker)
        thread.start()
    
    def on_modify_gasto_clicked(self, gasto_id: int):
        def worker():
            gasto = self.modelo.get_gasto_details(gasto_id)
            amigos = self.modelo.get_amigos()
            self.vista.run_on_ui_thread(self.vista.show_gasto_edit_or_error, gasto_id, gasto, amigos)

        self.vista.show_row_loading(gasto_id, True)
        thread = threading.Thread(target=worker)
        thread.start()

    def on_save_changes_clicked(self, gasto_original, new_desc, new_amount, new_date, amigos_checked_status):
        gasto_id = gasto_original.id
        def worker():
            ids_amigos_originales = {amigo.id for amigo in gasto_original.friends}
            ids_amigos_nuevos = {amigo_id for amigo_id, is_checked in amigos_checked_status.items() if is_checked}
            ids_anadir = ids_amigos_nuevos - ids_amigos_originales
            ids_quitar = ids_amigos_originales - ids_amigos_nuevos
            for amigo_id in ids_anadir: 
                self.modelo.add_amigo_a_gasto(gasto_id, amigo_id)
            for amigo_id in ids_quitar: 
                self.modelo.remove_amigo_de_gasto(gasto_id, amigo_id) 
            
            datos_basicos = {
                "description": new_desc, 
                "amount": new_amount, 
                "date": new_date # Usamos la fecha que viene de la vista
            }
            success = self.modelo.update_gasto(gasto_id, datos_basicos)
            
            self.vista.run_on_ui_thread(self.vista.reload_data_or_error, success, gasto_id=gasto_id)

        self.vista.show_row_loading(gasto_id, True)
        thread = threading.Thread(target=worker)
        thread.start()

    def on_delete_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere eliminar el gasto {gasto_id}.")
        self.vista.show_confirm_delete_dialog(gasto_id)

    def on_confirm_delete(self, gasto_id: int):
        def worker():
            success = self.modelo.delete_gasto(gasto_id)
            self.vista.run_on_ui_thread(self.vista.reload_data_or_error, success, gasto_id)

        self.vista.show_row_loading(gasto_id, True)
        thread = threading.Thread(target=worker)
        thread.start()
    
    def on_amigo_row_activated(self, listbox, row):
        amigo_id = row.amigo.id
        self.on_details_amigo_clicked(amigo_id)

    def on_details_amigo_clicked(self, amigo_id: int):
        def worker():
            amigo = self.modelo.get_amigo_details(amigo_id)
            gastos = self.modelo.get_gastos_por_amigo(amigo_id)
            self.vista.run_on_ui_thread(self.vista.show_amigo_details_or_error, amigo_id, amigo, gastos)

        self.vista.show_amigo_row_loading(amigo_id, True)
        thread = threading.Thread(target=worker)
        thread.start()

    def on_open_aporte_dialog_clicked(self, gasto: Gasto):
        self.vista.mostrar_dialogo_aporte(gasto.friends, 
            lambda amigo_id, amount: self.on_make_payment_clicked(gasto.id, amigo_id, amount))

    def on_make_payment_clicked(self, gasto_id: int, amigo_id: int, amount: float):
        def worker():
            success = self.modelo.make_payment_for_friend(gasto_id, amigo_id, amount)
            if success:
                amigos_en_gasto = self.modelo.get_amigos_por_gasto(gasto_id)
                amigo_actualizado = next((a for a in amigos_en_gasto if a.id == amigo_id), None)
                if amigo_actualizado and amigo_actualizado.debit_balance < 0.01:
                    self.modelo.remove_amigo_de_gasto(gasto_id, amigo_id)
            
            self.vista.run_on_ui_thread(self.vista.reload_data_or_error, success, gasto_id)
        self.vista.show_row_loading(gasto_id, True)
        thread = threading.Thread(target=worker)
        thread.start()