# src/view.py

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import List, Optional, Callable

from model import Gasto, Amigo

class DialogoGasto(Gtk.Dialog):
    def __init__(self, parent, amigos: List[Amigo], on_accept_callback, gasto_existente: Optional[Gasto] = None):
        super().__init__(transient_for=parent, modal=True)
        self.on_accept_callback = on_accept_callback
        self.add_buttons("_Cancelar", Gtk.ResponseType.CANCEL, "_Aceptar", Gtk.ResponseType.OK)
        boton_aceptar = self.get_widget_for_response(Gtk.ResponseType.OK)
        boton_cancelar = self.get_widget_for_response(Gtk.ResponseType.CANCEL)
        boton_aceptar.set_margin_end(15)
        boton_cancelar.set_margin_end(5)
        boton_aceptar.set_margin_bottom(10)
        boton_cancelar.set_margin_bottom(10)
        
        self.set_default_size(400, 450)

        self.amigos_checkboxes = {}

        content_area = self.get_content_area()
        grid = Gtk.Grid(margin_start=20, margin_end=20, margin_top=20, margin_bottom=10, row_spacing=15, column_spacing=10)
        content_area.append(grid)

        grid.attach(Gtk.Label(label="Descripción:"), 0, 0, 1, 1)
        self.entry_desc = Gtk.Entry()
        self.entry_desc.set_hexpand(True)
        grid.attach(self.entry_desc, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Importe (€):"), 0, 1, 1, 1)
        self.entry_importe = Gtk.SpinButton.new_with_range(0, 999999, 5.00)
        self.entry_importe.set_digits(2)
        grid.attach(self.entry_importe, 1, 1, 1, 1)

        label_amigos = Gtk.Label(label="Amigos:")
        label_amigos.set_valign(Gtk.Align.START)
        grid.attach(label_amigos, 0, 2, 1, 1)
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for amigo in amigos:
            cb = Gtk.CheckButton(label=amigo.name)
            self.amigos_checkboxes[amigo.id] = cb
            amigos_box.append(cb)
        scrolled_window = Gtk.ScrolledWindow(height_request=150)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_child(amigos_box)
        grid.attach(scrolled_window, 1, 2, 1, 1)

        self.connect("response", self._on_response)

    def _show_error_dialog(self, message: str):
        """Crea y muestra un diálogo de error estándar con un mensaje."""
        error_dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        error_dialog.connect("response", lambda d, r: d.destroy())
        error_dialog.present()

    def _on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            description = self.entry_desc.get_text().strip()
            amount = self.entry_importe.get_value()

            if not description:
                self._show_error_dialog("El campo 'Descripción' no puede estar vacío.")
            elif amount <= 0:
                self._show_error_dialog("El importe debe ser mayor que cero.")
            else:
                form_data = self.get_form_data()
                if self.on_accept_callback:
                    self.on_accept_callback(form_data)
                self.destroy()
        else:
            self.destroy()

    def get_form_data(self) -> dict:
        amigos_seleccionados = [amigo_id for amigo_id, cb in self.amigos_checkboxes.items() if cb.get_active()]
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
        #cabecera
        header = Gtk.HeaderBar()
        self.set_titlebar(header)

        about_button = Gtk.Button.new_from_icon_name("help-about-symbolic") 
        about_button.connect('clicked', self.on_about_clicked)
        header.pack_end(about_button)
        
        #contenido principal
        overlay = Gtk.Overlay()
        self.set_child(overlay)
        self.spinner = Gtk.Spinner(spinning=False, visible=False, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, width_request=50, height_request=50)
        overlay.add_overlay(self.spinner)

        #stack para cambiar entre vista principal y error
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        overlay.set_child(self.stack)
 
        # -- PANTALLA PRINCIPAL --
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        self.stack.add_named(main_box, "main_content")

        # panel de gastos
        gastos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        main_box.append(gastos_box)

        title_box_gastos = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        gastos_label = Gtk.Label(xalign=0, use_markup=True)
        gastos_label.set_markup("<span size='xx-large' weight='bold'>GASTOS</span>")
        gastos_label.set_hexpand(True)
        title_box_gastos.append(gastos_label)

        icon= Gtk.Image.new_from_icon_name("list-add-symbolic")
        icon.set_pixel_size(24)
        self.add_gasto_button = Gtk.Button()
        self.add_gasto_button.set_child(icon)
        self.add_gasto_button.set_halign(Gtk.Align.END)
        title_box_gastos.append(self.add_gasto_button)
        gastos_box.append(title_box_gastos)

        scrolled_window_gastos = Gtk.ScrolledWindow(vexpand=True)
        scrolled_window_gastos.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.lista_gastos = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        scrolled_window_gastos.set_child(self.lista_gastos)
        gastos_box.append(scrolled_window_gastos)

        # panel de amigos
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        main_box.append(amigos_box)
        amigos_label = Gtk.Label(xalign=0, use_markup=True)
        amigos_label.set_markup("<span size='xx-large' weight='bold'>AMIGOS</span>")
        amigos_box.append(amigos_label)
        scrolled_window_amigos = Gtk.ScrolledWindow(vexpand=True)
        scrolled_window_amigos.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.lista_amigos = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        scrolled_window_amigos.set_child(self.lista_amigos)
        amigos_box.append(scrolled_window_amigos) 

        # -- PANTALLA DE ERROR DE CONEXIÓN --
        error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, vexpand=True)
        self.stack.add_named(error_box, "error_screen")
        try:
            error_image = Gtk.Image.new_from_file("../assets/images/wifi-off.png")
            error_image.set_pixel_size(128)
            error_box.append(error_image)
        except GLib.Error as e:
            print(f"Error al cargar la imagen de error: {e}")
        
        error_label = Gtk.Label(label="No es posible conectarse con el servidor")
        error_box.append(error_label)
        self.retry_button = Gtk.Button(label="Reintentar")
        error_box.append(self.retry_button)

    def on_about_clicked(self, widget):
        about = Gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_modal(True)
        about.set_program_name("SplitWithMe")
        about.set_version("Version 1.0")
        about.set_authors(["Pablo Fernández Martí", "Joel Ramos Carro", "Nicolás Dominguez Souto"])
        about.set_comments("Aplicación de escritorio para la gestión de gastos compartidos con amigos.")
        try:
            image = Gtk.Image.new_from_file("../assets/images/logo.png")
            image.set_pixel_size(200)
            about.set_logo(image.get_paintable())
        except GLib.Error as e:
            print(f"Error al cargar logo para AboutDialog: {e}")
        about.present()

    def connect_signals(self):
        self.add_gasto_button.connect('clicked', lambda w: self.presenter.on_add_gasto_clicked())
        self.retry_button.connect('clicked', self.presenter.on_retry_clicked)

    def show_connection_error(self, visible: bool):
        if visible:
            self.stack.set_visible_child_name("error_screen")
        else:
            self.stack.set_visible_child_name("main_content")

    def show_loading(self, is_loading: bool):
        self.spinner.set_visible(is_loading)
        self.spinner.set_spinning(is_loading)
        self.get_child().get_child().set_sensitive(not is_loading)

    def mostrar_gastos(self, gastos: List[Gasto]):
        while (child := self.lista_gastos.get_row_at_index(0)): self.lista_gastos.remove(child)
        for gasto in gastos:
            row_widget = GastoRow(gasto, self.presenter)
            self.lista_gastos.append(row_widget)

    def mostrar_amigos(self, amigos: List[Amigo]):
        while (child := self.lista_amigos.get_row_at_index(0)): self.lista_amigos.remove(child)
        for amigo in amigos:
            row_widget = AmigoRow(amigo, self.presenter)
            self.lista_amigos.append(row_widget)    

    def show_gasto_details(self, gasto: Gasto):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=f"Detalles del Gasto {gasto.description}")
        num_amigos = len(gasto.friends)
        
        if gasto.friends:
            nombres_amigos = ", ".join([amigo.name for amigo in gasto.friends])
            amigos_markup = f"<b>Amigos:</b> {nombres_amigos}"
        else:
            amigos_markup= "<b>Amigos:</b> Ninguno"
        
        details = (
        f"<b>ID:</b> {gasto.id}\n"
        f"<b>Importe:</b> {gasto.amount:.2f}€\n"
        f"<b>Fecha:</b> {gasto.date}\n"
        f"<b>Nº de amigos:</b> {num_amigos}\n"
        f"{amigos_markup}" # lista de nombres
        )        
        dialog.set_property("secondary_text", details)
        dialog.set_property("secondary_use_markup", True)
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.present()

    def show_amigo_details(self, amigo: Amigo, gastos_asociados: List[Gasto]):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=f"Detalles del Amigo {amigo.name}")
        gastos_str = "\n".join([f"- {gasto.description}: {gasto.amount:.2f}€" for gasto in gastos_asociados])
        if not gastos_str: gastos_str = "No participa en ningún gasto."
        details = (f"<b>ID:</b> {amigo.id}\n<b>Saldo:</b> {amigo.saldo:.2f}€\n<b>Crédito:</b> {amigo.credit_balance:.2f}€\n<b>Débito:</b> {amigo.debit_balance:.2f}€\n<b><u>Gastos en los que participa:</u></b>\n{gastos_str}")
        dialog.set_property("secondary_text", details)
        dialog.set_property("secondary_use_markup", True)
        dialog.connect("response", lambda d, response_id: d.destroy())
        dialog.present()

    def mostrar_dialogo_gasto(self, amigos: List[Amigo], on_accept_callback, gasto_existente: Optional[Gasto] = None) -> DialogoGasto:
        dialog = DialogoGasto(self, amigos, on_accept_callback, gasto_existente)
        dialog.present()
        return dialog

    def show_confirm_delete_dialog(self, gasto_id: int):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO, text="¿Estás seguro de que quieres eliminar este gasto?")
        dialog.connect("response", lambda d, response_id: self._on_delete_dialog_response(d, response_id, gasto_id))
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response_id, gasto_id):
        dialog.destroy()
        if response_id == Gtk.ResponseType.YES: self.presenter.on_confirm_delete(gasto_id)



class GastoRow(Gtk.Box):
    """Widget de fila personalizado para un Gasto, con su propio Revealer."""
    def __init__(self, gasto: Gasto, presenter):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.gasto = gasto
        self.presenter = presenter

        # Caja principal visible
        main_row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin_top=8, margin_bottom=8, margin_start=8, margin_end=8)
        info_label = Gtk.Label(label=f"<b>{gasto.description}</b>\nImporte Total: {gasto.amount:.2f}€", xalign=0, hexpand=True, use_markup=True)
        
        buttons_box = Gtk.Box(spacing=5, halign=Gtk.Align.END)
        self.details_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        modify_button = Gtk.Button.new_from_icon_name("document-edit-symbolic")
        delete_button = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        delete_button.get_style_context().add_class("destructive-action")
        
        buttons_box.append(self.details_button)
        buttons_box.append(modify_button)
        buttons_box.append(delete_button)
        main_row_box.append(info_label)
        main_row_box.append(buttons_box)
        
        self.append(main_row_box)
        
        # Revealer para detalles y edición
        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.append(self.revealer)

        # Conexiones
        self.details_button.connect('clicked', self.on_details_clicked)
        modify_button.connect('clicked', lambda w: self.show_edit_view())
        delete_button.connect('clicked', lambda w: self.presenter.on_delete_gasto_clicked(self.gasto.id))

    def on_details_clicked(self, widget):
        is_revealed = self.revealer.get_child_revealed()
        if not is_revealed:
            # Pedimos los detalles actualizados al presenter
            self.presenter.on_details_gasto_clicked(self.gasto.id, self)
        else:
            self.revealer.set_reveal_child(False)

    def show_details_view(self, gasto_con_amigos: Gasto):
        # Muestra la información detallada
        details_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=5, column_spacing=10)
        nombres_amigos = ", ".join([amigo.name for amigo in gasto_con_amigos.friends]) or "Ninguno"
    
        details_grid.attach(Gtk.Label(label="<b>Nombre del Gasto:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        details_grid.attach(Gtk.Label(label=gasto_con_amigos.description, xalign=0, wrap=True), 1, 0, 1, 1)

        details_grid.attach(Gtk.Label(label="<b>Importe Total:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        details_grid.attach(Gtk.Label(label=f"{gasto_con_amigos.amount:.2f}€", xalign=0), 1, 1, 1, 1)

        details_grid.attach(Gtk.Label(label="<b>Fecha:</b>", use_markup=True, xalign=0), 0, 2, 1, 1)
        details_grid.attach(Gtk.Label(label=gasto_con_amigos.date, xalign=0), 1, 2, 1, 1)
        
        details_grid.attach(Gtk.Label(label="<b>Número de Amigos:</b>", use_markup=True, xalign=0), 0, 3, 1, 1)
        details_grid.attach(Gtk.Label(label=str(len(gasto_con_amigos.friends)), xalign=0), 1, 3, 1, 1)

        details_grid.attach(Gtk.Label(label="<b>Amigos:</b>", use_markup=True, xalign=0), 0, 4, 1, 1)
        details_grid.attach(Gtk.Label(label=nombres_amigos, xalign=0, wrap=True), 1, 4, 1, 1)

        aporte_button = Gtk.Button(label="Realizar Aporte")
        if not gasto_con_amigos.friends:
            aporte_button.set_sensitive(False)
        else:
            aporte_button.connect('clicked', lambda w: self.presenter.on_add_aporte_clicked(self.gasto.id, self))        
        details_grid.attach(aporte_button, 0, 5, 2, 1)

        self.revealer.set_child(details_grid)
        self.revealer.set_reveal_child(True)

    def show_edit_view(self):
        # Llama al presenter para que inicie el flujo de modificación
        self.presenter.on_modify_gasto_clicked(self.gasto.id, self)

    def update_edit_view(self, gasto_editar: Gasto, todos_amigos: List[Amigo]):
        edit_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=10, column_spacing=10)
        
        # Descripción
        edit_grid.attach(Gtk.Label(label="Descripción:"), 0, 0, 1, 1)
        entry_desc = Gtk.Entry(text=gasto_editar.description)
        edit_grid.attach(entry_desc, 1, 0, 1, 1)

        # Importe
        edit_grid.attach(Gtk.Label(label="Importe (€):"), 0, 1, 1, 1)
        spin_importe = Gtk.SpinButton.new_with_range(0, 10000, 0.01)
        spin_importe.set_digits(2)
        spin_importe.set_value(gasto_editar.amount)
        edit_grid.attach(spin_importe, 1, 1, 1, 1)

        # Amigos
        label_amigos = Gtk.Label(label="Amigos:")
        edit_grid.attach(label_amigos, 0, 2, 1, 1)
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        amigos_checkboxes = {} 
        ids_amigos_actuales = {amigo.id for amigo in gasto_editar.friends}
        for amigo in todos_amigos:
            cb = Gtk.CheckButton(label=amigo.name)
            amigos_checkboxes[amigo.id] = cb
            if amigo.id in ids_amigos_actuales:
                cb.set_active(True) # Marcamos si el ID está en la lista
            amigos_box.append(cb)
        scrolled_window = Gtk.ScrolledWindow(height_request=150)
        scrolled_window.set_child(amigos_box)
        edit_grid.attach(scrolled_window, 1, 2, 1, 1)


        # Botones de acción
        buttons_box = Gtk.Box(spacing=10, halign=Gtk.Align.END)
        save_button = Gtk.Button(label="Guardar")
        cancel_button = Gtk.Button(label="Cancelar")
        buttons_box.append(cancel_button)
        buttons_box.append(save_button)
        edit_grid.attach(buttons_box, 1, 3, 1, 1)

        # Conexiones
        cancel_button.connect('clicked', lambda w: self.revealer.set_reveal_child(False))
        save_button.connect('clicked', lambda w: self.presenter.on_save_changes_clicked(
            gasto_editar,
            entry_desc.get_text(),
            spin_importe.get_value(),
            {amigo_id: cb.get_active() for amigo_id, cb in amigos_checkboxes.items()}
        ))

        self.revealer.set_child(edit_grid)
        self.revealer.set_reveal_child(True)

    def show_add_aporte_view(self, gasto_id: int, amigos_del_gasto: List[Amigo], importe_maximo: float):
        edit_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=10, column_spacing=10)
        
        edit_grid.attach(Gtk.Label(label="Amigo que aporta:"), 0, 0, 1, 1)
        combo_amigos = Gtk.ComboBoxText()
        for amigo in amigos_del_gasto: # Usa la lista de amigos pasada
            combo_amigos.append(str(amigo.id), amigo.name)
        combo_amigos.set_active(0)
        edit_grid.attach(combo_amigos, 1, 0, 1, 1)

        edit_grid.attach(Gtk.Label(label="Importe (€):"), 0, 1, 1, 1)
        spin_importe = Gtk.SpinButton.new_with_range(0.01, importe_maximo, 5.00)
        spin_importe.set_digits(2)
        spin_importe.set_value(min(1.0, importe_maximo))         
        edit_grid.attach(spin_importe, 1, 1, 1, 1)

        buttons_box = Gtk.Box(spacing=10, halign=Gtk.Align.END)
        save_button = Gtk.Button(label="Guardar Aporte")
        cancel_button = Gtk.Button(label="Cancelar")
        buttons_box.append(cancel_button)
        buttons_box.append(save_button)
        edit_grid.attach(buttons_box, 1, 2, 1, 1)

        cancel_button.connect('clicked', lambda w: self.revealer.set_reveal_child(False))
        save_button.connect('clicked', lambda w: self.presenter.on_save_new_aporte(
            gasto_id, # Usa el ID pasado
            int(combo_amigos.get_active_id()),
            spin_importe.get_value()
        ))

        self.revealer.set_child(edit_grid)
        self.revealer.set_reveal_child(True)

class AmigoRow(Gtk.Box):
    def __init__(self, amigo: Amigo, presenter):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.amigo = amigo
        self.presenter = presenter

        main_row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin_top=8, margin_bottom=8, margin_start=8, margin_end=8)
        label = Gtk.Label(label=f"<b>{amigo.name}</b>\nSaldo: {amigo.saldo:.2f}€", xalign=0, hexpand=True, use_markup=True)
        
        self.details_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        
        main_row_box.append(label)
        main_row_box.append(self.details_button)
        self.append(main_row_box)
        
        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.append(self.revealer)

        self.details_button.connect('clicked', self.on_details_clicked)

    def on_details_clicked(self, widget):
        is_revealed = self.revealer.get_child_revealed()
        if not is_revealed:
            self.presenter.on_details_amigo_clicked(self.amigo.id, self)
        else:
            self.revealer.set_reveal_child(False)

    def show_details_view(self, amigo_con_detalles: Amigo, gastos_asociados: List[Gasto]):
        details_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=5, column_spacing=10)
        gastos_str = "\n".join([f"- {g.description}" for g in gastos_asociados]) or "Ninguno"
        
        details_grid.attach(Gtk.Label(label="<b>Crédito:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        details_grid.attach(Gtk.Label(label=f"{amigo_con_detalles.credit_balance:.2f}€", xalign=0), 1, 0, 1, 1)
        details_grid.attach(Gtk.Label(label="<b>Débito:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        details_grid.attach(Gtk.Label(label=f"{amigo_con_detalles.debit_balance:.2f}€", xalign=0), 1, 1, 1, 1)
        details_grid.attach(Gtk.Label(label="<b>Gastos:</b>", use_markup=True, xalign=0), 0, 2, 1, 1)
        details_grid.attach(Gtk.Label(label=gastos_str, xalign=0, wrap=True), 1, 2, 1, 1)

        self.revealer.set_child(details_grid)
        self.revealer.set_reveal_child(True)

class App(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id="com.example.splitwithme", **kwargs)