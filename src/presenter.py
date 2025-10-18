from datetime import date
from model import Gasto
from gi.repository import GLib
import threading

class Presenter:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo 
        self.vista.set_presenter(self)
        self.vista.connect_signals()

    def _execute_in_thread(self, target_func, *args):
        self.vista.show_loading(True)
        thread = threading.Thread(target=target_func, args=args)
        thread.start()

    def iniciar(self):
        print("PRESENTER: Iniciando aplicación...")
        self.cargar_datos_principales()

    def cargar_datos_principales(self):
        def worker():
            gastos = self.modelo.get_gastos()
            amigos = self.modelo.get_amigos()
            GLib.idle_add(ui_update, gastos, amigos)

        def ui_update(gastos, amigos):
            if gastos is None or amigos is None:
                self.vista.show_connection_error(True)
            else:
                self.vista.show_connection_error(False)
                self.vista.mostrar_gastos(gastos)
                self.vista.mostrar_amigos(amigos)
            self.vista.show_loading(False)
            print("PRESENTER: Datos iniciales cargados.")
        
        self._execute_in_thread(worker)

    def on_retry_clicked(self, widget):
        print("PRESENTER: El usuario ha pulsado Reintentar.")
        self.cargar_datos_principales() 

    def on_refresh_clicked(self):
        print("PRESENTER: El usuario ha pulsado Refrescar.")
        self.cargar_datos_principales()

    def on_gasto_row_activated(self, listbox, row):
        gasto_id = row.gasto_id
        self.on_details_gasto_clicked(gasto_id, row)

    def on_details_gasto_clicked(self, gasto_id: int, row_widget):
        def worker():
            gasto_con_detalles = self.modelo.get_gasto_details(gasto_id)
            GLib.idle_add(ui_update, gasto_con_detalles)

        def ui_update(gasto_con_detalles):
            if gasto_con_detalles:
                row_widget.show_details_view(gasto_con_detalles)
            else:
                self.vista.show_connection_error(True)
            self.vista.show_loading(False)

        self._execute_in_thread(worker)

    def on_add_gasto_clicked(self):
        def worker():
            amigos = self.modelo.get_amigos()
            GLib.idle_add(ui_update, amigos)

        def ui_update(amigos):
            if amigos is None:
                self.vista.show_connection_error(True); self.vista.show_loading(False); return
            
            self.vista.show_loading(False)
            self.vista.mostrar_dialogo_gasto(amigos, self._on_accept_new_gasto)
        
        self._execute_in_thread(worker)

    def _on_accept_new_gasto(self, datos_gasto):
        def worker():
            datos_gasto['date'] = date.today().strftime("%Y-%m-%d")
            success = self.modelo.create_gasto_with_friends(datos_gasto)
            GLib.idle_add(ui_update, success)

        def ui_update(success):
            if success: 
                self.cargar_datos_principales()
            else: 
                self.vista.show_connection_error(True); self.vista.show_loading(False)

        self._execute_in_thread(worker)
    
    def on_modify_gasto_clicked(self, gasto_id: int, row_widget):
        def worker():
            gasto = self.modelo.get_gasto_details(gasto_id)
            amigos = self.modelo.get_amigos()
            GLib.idle_add(ui_update, gasto, amigos)

        def ui_update(gasto, amigos):
            if gasto and amigos:
                row_widget.update_edit_view(gasto, amigos)
            else:
                self.vista.show_connection_error(True)
            self.vista.show_loading(False)

        self._execute_in_thread(worker)

    def on_save_changes_clicked(self, gasto_original, new_desc, new_amount, amigos_checked_status):
        def worker():
            # (La lógica de validación se mantiene igual y se ejecuta aquí)
            ids_amigos_originales = {amigo.id for amigo in gasto_original.friends}
            ids_amigos_nuevos = {amigo_id for amigo_id, is_checked in amigos_checked_status.items() if is_checked}
            ids_anadir = ids_amigos_nuevos - ids_amigos_originales; ids_quitar = ids_amigos_originales - ids_amigos_nuevos
            for amigo_id in ids_anadir: 
                self.modelo.add_amigo_a_gasto(gasto_original.id, amigo_id)
            for amigo_id in ids_quitar: 
                self.modelo.remove_amigo_de_gasto(gasto_original.id, amigo_id) 
            datos_basicos = {"description": new_desc, "amount": new_amount, "date": gasto_original.date}
            success = self.modelo.update_gasto(gasto_original.id, datos_basicos)
            GLib.idle_add(ui_update, success)
        
        def ui_update(success): 
            if success: self.cargar_datos_principales()
            else: self.vista.show_connection_error(True); self.vista.show_loading(False)
        
        self._execute_in_thread(worker)

    def on_delete_gasto_clicked(self, gasto_id: int):
        print(f"PRESENTER: El usuario quiere eliminar el gasto {gasto_id}.")
        self.vista.show_confirm_delete_dialog(gasto_id)

    def on_confirm_delete(self, gasto_id: int):
        def worker():
            success = self.modelo.delete_gasto(gasto_id)
            GLib.idle_add(ui_update, success)

        def ui_update(success):
            if success: self.cargar_datos_principales()
            else: self.vista.show_connection_error(True); self.vista.show_loading(False)
        
        self._execute_in_thread(worker)
    
    def on_amigo_row_activated(self, listbox, row):
        amigo_id = row.amigo.id
        self.on_details_amigo_clicked(amigo_id, row)

    def on_details_amigo_clicked(self, amigo_id: int, row_widget):
        def worker():
            amigo = self.modelo.get_amigo_details(amigo_id)
            gastos = self.modelo.get_gastos_por_amigo(amigo_id)
            GLib.idle_add(ui_update, amigo, gastos)

        def ui_update(amigo, gastos):
            if amigo and gastos is not None:
                row_widget.show_details_view(amigo, gastos)
            else:
                self.vista.show_connection_error(True)
            self.vista.show_loading(False)
        
        self._execute_in_thread(worker)

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
            GLib.idle_add(ui_update, success)

        def ui_update(success):
            if success: self.cargar_datos_principales()
            else: self.vista.show_connection_error(True); self.vista.show_loading(False)
        
        self._execute_in_thread(worker)
            
    def on_add_aporte_clicked(self, gasto_id: int, row_widget):
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