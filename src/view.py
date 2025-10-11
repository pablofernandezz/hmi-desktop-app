# view.py

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import List, Optional

# Importamos las clases de datos para que el editor nos ayude (type hinting)
from model import Gasto, Amigo

class DialogoGasto(Gtk.Dialog):
    def __init__(self, parent, amigos: List[Amigo], on_accept_callback, gasto_existente: Optional[Gasto] = None):
        super().__init__(transient_for=parent, modal=True)
        
        self.on_accept_callback = on_accept_callback

        if gasto_existente:
            self.set_title("Modificar Gasto")
        else:
            self.set_title("Añadir Gasto")

        self.add_buttons(
            "_Cancelar", Gtk.ResponseType.CANCEL,
            "_Aceptar", Gtk.ResponseType.OK
        )

        self.amigos_checkboxes = {}

        content_area = self.get_content_area()
        grid = Gtk.Grid(margin_start=10, margin_end=10, margin_top=10, margin_bottom=10, row_spacing=10, column_spacing=10)
        content_area.append(grid)

        # --- Widgets que se muestran SIEMPRE ---
        grid.attach(Gtk.Label(label="Descripción:"), 0, 0, 1, 1)
        self.entry_desc = Gtk.Entry()
        grid.attach(self.entry_desc, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Importe (€):"), 0, 1, 1, 1)
        self.entry_importe = Gtk.SpinButton.new_with_range(0, 10000, 0.01)
        self.entry_importe.set_digits(2)
        grid.attach(self.entry_importe, 1, 1, 1, 1)

        # --- Widgets y lógica que solo se ejecutan si estamos MODIFICANDO ---
        if gasto_existente:
            # 1. Creamos y mostramos la lista de amigos
            label_amigos = Gtk.Label(label="Amigos:")
            grid.attach(label_amigos, 0, 2, 1, 1)
            
            amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            for amigo in amigos:
                checkbox = Gtk.CheckButton(label=amigo.name)
                self.amigos_checkboxes[amigo.id] = checkbox
                amigos_box.append(checkbox)

            scrolled_window = Gtk.ScrolledWindow(height_request=150)
            scrolled_window.set_child(amigos_box)
            grid.attach(scrolled_window, 1, 2, 1, 1)

            # 2. Rellenamos los campos con los datos del gasto
            self.entry_desc.set_text(gasto_existente.description)
            self.entry_importe.set_value(gasto_existente.amount)

            # 3. Marcamos los checkboxes de los amigos que ya participan
            if gasto_existente.friends:
                ids_amigos_actuales = {amigo.id for amigo in gasto_existente.friends}
                for amigo_id, checkbox in self.amigos_checkboxes.items():
                    if amigo_id in ids_amigos_actuales:
                        checkbox.set_active(True)
        
        # La conexión de la señal se hace siempre
        self.connect("response", self._on_response)

    def _on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            # Si el usuario acepta, obtiene los datos y ejecuta el callback
            form_data = self.get_form_data()
            if self.on_accept_callback:
                self.on_accept_callback(form_data)
        self.destroy()

    def get_form_data(self) -> dict:
        amigos_seleccionados = [amigo_id for amigo_id, cb in self.amigos_checkboxes.items() if cb.get_active()]
        # CORRECCIÓN: Devolvemos las claves en inglés para ser consistentes
        return {
            "description": self.entry_desc.get_text(),
            "amount": self.entry_importe.get_value(),
            "friend_ids": amigos_seleccionados
        }



class VistaPrincipal(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.presenter = None
        self.set_title("SplitWithMe")
        self.set_default_size(800, 600)
        self.build_ui()

    def set_presenter(self, p):
        self.presenter = p

    def build_ui(self):
        # Usamos un Overlay para poder mostrar un spinner de carga encima de la UI
        overlay = Gtk.Overlay()
        self.set_child(overlay)
        self.spinner = Gtk.Spinner(spinning=False, visible=False)
        self.spinner.set_halign(Gtk.Align.CENTER)
        self.spinner.set_valign(Gtk.Align.CENTER)
        self.spinner.set_size_request(50, 50)
        overlay.add_overlay(self.spinner)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.set_margin_top(10); main_box.set_margin_bottom(10)
        main_box.set_margin_start(10); main_box.set_margin_end(10)
        overlay.set_child(main_box)

        # --- Panel de Gastos ---
        gastos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        main_box.append(gastos_box)

        gastos_label = Gtk.Label(label="GASTOS", xalign=0)
        gastos_box.append(gastos_label)

        scrolled_window_gastos = Gtk.ScrolledWindow(vexpand=True)
        self.lista_gastos = Gtk.ListBox()
        scrolled_window_gastos.set_child(self.lista_gastos)
        gastos_box.append(scrolled_window_gastos)

        self.add_gasto_button = Gtk.Button(label="Añadir Gasto")
        gastos_box.append(self.add_gasto_button)

        # --- Panel de Amigos ---
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        main_box.append(amigos_box)

        amigos_label = Gtk.Label(label="AMIGOS", xalign=0)
        amigos_box.append(amigos_label)

        scrolled_window_amigos = Gtk.ScrolledWindow(vexpand=True)
        self.lista_amigos = Gtk.ListBox()
        scrolled_window_amigos.set_child(self.lista_amigos)
        amigos_box.append(scrolled_window_amigos)

    def connect_signals(self):
        # La lambda evita pasar el argumento 'widget' al presentador
        self.add_gasto_button.connect('clicked', lambda w: self.presenter.on_add_gasto_clicked())

    def show_loading(self, is_loading: bool):
        self.spinner.set_visible(is_loading)
        self.spinner.set_spinning(is_loading)
        # Hacemos la ventana principal no-interactiva mientras carga
        self.get_child().get_child().set_sensitive(not is_loading)


    def mostrar_gastos(self, gastos: List[Gasto]):
        while (child := self.lista_gastos.get_row_at_index(0)):
            self.lista_gastos.remove(child)
        for gasto in gastos:
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin_top=5, margin_bottom=5)
            # CORRECCIÓN: Usamos 'description' y 'amount'
            info_label = Gtk.Label(label=f"{gasto.description}\n{gasto.amount:.2f}€", xalign=0, hexpand=True)
            
            buttons_box = Gtk.Box(spacing=5)

            details_button = Gtk.Button(label="Detalles")
            details_button.connect('clicked', lambda w, g_id=gasto.id: self.presenter.on_details_gasto_clicked(g_id))

            modify_button = Gtk.Button(label="Modificar")
            modify_button.connect('clicked', lambda w, g_id=gasto.id: self.presenter.on_modify_gasto_clicked(g_id))
            
            delete_button = Gtk.Button(label="Eliminar")
            delete_button.get_style_context().add_class("destructive-action")
            delete_button.connect('clicked', lambda w, g_id=gasto.id: self.presenter.on_delete_gasto_clicked(g_id))

            buttons_box.append(details_button)
            buttons_box.append(modify_button)
            buttons_box.append(delete_button)

            row_box.append(info_label)
            row_box.append(buttons_box)
            
            self.lista_gastos.append(row_box)


    def mostrar_amigos(self, amigos: List[Amigo]):
        while (child := self.lista_amigos.get_row_at_index(0)):
            self.lista_amigos.remove(child)

        for amigo in amigos:
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin_top=5, margin_bottom=5)
            label = Gtk.Label(label=f"{amigo.name}\nSaldo: {amigo.saldo:.2f}€", xalign=0, hexpand=True)
            details_button = Gtk.Button(label="Detalles")
            details_button.connect('clicked', lambda w, a_id=amigo.id: self.presenter.on_details_amigo_clicked(a_id))
            
            row_box.append(label)
            row_box.append(details_button)
            self.lista_amigos.append(row_box)


    def show_gasto_details(self, gasto: Gasto):
        dialog=Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=f"Detalles del Gasto {gasto.description}",
        )

        details = (
            f"<b>ID:</b> {gasto.id}\n"
            f"<b>Importe:</b> {gasto.amount:.2f}€\n"
            f"<b>Fecha:</b> {gasto.date}\n"
            f"<b>Nº de amigos:</b> {gasto.num_friends}\n"
        )
        dialog.set_property("secondary_text", details)
        dialog.set_property("secondary_use_markup", True)
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.present()


    def show_amigo_details(self, amigo: Amigo, gastos_asociados: List[Gasto]):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=f"Detalles del Amigo {amigo.name}",
        )
        gastos_str = "\n".join([f"- {gasto.description}: {gasto.amount:.2f}€" for gasto in gastos_asociados])
        if not gastos_str:
            gastos_str = "No participa en ningún gasto."

        details = (
            f"<b>ID:</b> {amigo.id}\n"
            f"<b>Saldo:</b> {amigo.saldo:.2f}€\n"
            f"<b>Crédito:</b> {amigo.credit_balance:.2f}€\n"
            f"<b>Débito:</b> {amigo.debit_balance:.2f}€\n"
            f"<b><u>Gastos en los que participa:</u></b>\n{gastos_str}"
        )
        dialog.set_property("secondary_text", details)
        dialog.set_property("secondary_use_markup", True)
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.present()


    def mostrar_dialogo_gasto(self, amigos: List[Amigo], on_accept_callback, gasto_existente: Optional[Gasto] = None) -> DialogoGasto:
        dialog = DialogoGasto(self, amigos, on_accept_callback, gasto_existente)
        dialog.present()
        return dialog


    def show_confirm_delete_dialog(self, gasto_id: int):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="¿Estás seguro de que quieres eliminar este gasto?",
        )
        dialog.connect("response", lambda d, response_id: self._on_delete_dialog_response(d, response_id, gasto_id))
        dialog.present()


    def _on_delete_dialog_response(self, dialog, response_id, gasto_id):
        dialog.destroy()
        if response_id == Gtk.ResponseType.YES:
            self.presenter.on_confirm_delete(gasto_id)



class App(Gtk.Application):
    def __init__(self, modelo, **kwargs):
        super().__init__(application_id="com.example.splitwithme", **kwargs)
        self.modelo = modelo
        self.win = None

    def do_activate(self):
        from presenter import Presenter
        if not self.win:
            self.win = VistaPrincipal(application=self)
            presentador = Presenter(self.win, self.modelo)
            presentador.iniciar()
        self.win.present()