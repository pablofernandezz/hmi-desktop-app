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
        self.amigos_checkboxes = {}

        content_area = self.get_content_area()
        grid = Gtk.Grid(margin_start=10, margin_end=10, margin_top=10, margin_bottom=10, row_spacing=10, column_spacing=10)
        content_area.append(grid)

        grid.attach(Gtk.Label(label="Descripción:"), 0, 0, 1, 1)
        self.entry_desc = Gtk.Entry()
        grid.attach(self.entry_desc, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Importe (€):"), 0, 1, 1, 1)
        self.entry_importe = Gtk.SpinButton.new_with_range(0, 999999, 5.00)
        self.entry_importe.set_digits(2)
        grid.attach(self.entry_importe, 1, 1, 1, 1)

        label_amigos = Gtk.Label(label="Amigos:")
        grid.attach(label_amigos, 0, 2, 1, 1)
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        for amigo in amigos:
            cb = Gtk.CheckButton(label=amigo.name)
            self.amigos_checkboxes[amigo.id] = cb
            amigos_box.append(cb)
        scrolled_window = Gtk.ScrolledWindow(height_request=150)
        scrolled_window.set_child(amigos_box)
        grid.attach(scrolled_window, 1, 2, 1, 1)

        self.connect("response", self._on_response)

    def _on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            form_data = self.get_form_data()
            if self.on_accept_callback:
                self.on_accept_callback(form_data)
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

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        header.pack_end(menu_button)

        menu_popover = Gtk.PopoverMenu()
        menu_popover.set_has_arrow(False)
        menu_button.set_popover(menu_popover)
        
        about_button=Gtk.Button(label="Acerca de...")
        about_button.connect('clicked', self.on_about_clicked)
        menu_popover.set_child(about_button)

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
        gastos_box.append(gastos_label)

        icon= Gtk.Image.new_from_icon_name("list-add-symbolic")
        icon.set_pixel_size(24)
        self.add_gasto_button = Gtk.Button()
        self.add_gasto_button.set_child(icon)
        self.add_gasto_button.set_halign(Gtk.Align.START)
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
        about.set_version("1.0")
        about.set_authors(["Pablo Fernández Martí", "Joel Ramos Carro", "Nicolás Dominguez Souto"])
        about.set_comments("Aplicación de escritorio para la gestión de gastos compartidos.")
        try:
            logo = Gtk.Picture.new_for_filename("../assets/images/logo.png")
            about.set_logo(logo.get_paintable())
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
            label = Gtk.Label(label=f"<b>{amigo.name}</b>\nSaldo: {amigo.saldo:.2f}€", xalign=0, hexpand=True, use_markup=True)
            self.lista_amigos.append(label)

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
        self.details_button = Gtk.Button.new_from_icon_name("go-down-symbolic") # Botón para desplegar
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
        
        details_grid.attach(Gtk.Label(label="<b>Fecha:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        details_grid.attach(Gtk.Label(label=gasto_con_amigos.date, xalign=0), 1, 0, 1, 1)
        details_grid.attach(Gtk.Label(label="<b>Amigos:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        details_grid.attach(Gtk.Label(label=nombres_amigos, xalign=0, wrap=True), 1, 1, 1, 1)

        # Aquí iría la lógica para "realizar aporte"
        aporte_button = Gtk.Button(label="Realizar Aporte")
        # aporte_button.connect('clicked', ...)
        details_grid.attach(aporte_button, 0, 2, 2, 1)

        self.revealer.set_child(details_grid)
        self.revealer.set_reveal_child(True)

    def show_edit_view(self):
        # Llama al presenter para que inicie el flujo de modificación
        self.presenter.on_modify_gasto_clicked(self.gasto.id, self)

    def update_edit_view(self, todos_amigos: List[Amigo]):
        # Muestra el formulario de edición
        edit_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=5, column_spacing=10)
        
        # ... construir el formulario con Entry, SpinButton, CheckButtons ...
        # (similar a como se hacía en DialogoGasto)
        
        save_button = Gtk.Button(label="Guardar")
        cancel_button = Gtk.Button(label="Cancelar")
        
        # Conectar señales de save y cancel
        # save_button.connect('clicked', ...)
        cancel_button.connect('clicked', lambda w: self.revealer.set_reveal_child(False))

        self.revealer.set_child(edit_grid)
        self.revealer.set_reveal_child(True)


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