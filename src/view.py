import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import List, Optional, Callable

from model import Gasto, Amigo, AmigoEnGasto

class DialogoAporte(Gtk.Dialog):
    def __init__(self, parent, amigos_participantes: List['AmigoEnGasto']):
        super().__init__(transient_for=parent, modal=True, title="Realizar Aporte")
        self.add_buttons("_Cancelar", Gtk.ResponseType.CANCEL, "_Aceptar", Gtk.ResponseType.OK)
        self.amigos_participantes = amigos_participantes

        content_area = self.get_content_area()
        grid = Gtk.Grid(margin_start=10, margin_end=10, margin_top=10, margin_bottom=10, row_spacing=10, column_spacing=10)
        content_area.append(grid)

        grid.attach(Gtk.Label(label="Amigo:"), 0, 0, 1, 1)
        self.combo_amigos = Gtk.ComboBoxText()
        for amigo in self.amigos_participantes:
            if amigo.debit_balance > 0.01:
                self.combo_amigos.append(str(amigo.id), f"{amigo.name} (debe {amigo.debit_balance:.2f}€)")
        grid.attach(self.combo_amigos, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Cantidad (€):"), 0, 1, 1, 1)
        self.spin_cantidad = Gtk.SpinButton.new_with_range(0.01, 10000, 0.01)
        self.spin_cantidad.set_digits(2)
        grid.attach(self.spin_cantidad, 1, 1, 1, 1)

        self.combo_amigos.connect("changed", self.on_amigo_selected)
        if self.combo_amigos.get_active() == -1 and len(self.amigos_participantes) > 0:
            self.combo_amigos.set_active(0)

    def on_amigo_selected(self, combo):
        amigo_id_str = combo.get_active_id()
        if not amigo_id_str: return
        amigo_id = int(amigo_id_str)
        
        deuda_maxima = next((amigo.debit_balance for amigo in self.amigos_participantes if amigo.id == amigo_id), 10000)
        
        ajuste = self.spin_cantidad.get_adjustment()
        ajuste.set_upper(deuda_maxima)
        self.spin_cantidad.set_value(deuda_maxima)

    def get_form_data(self) -> Optional[dict]:
        amigo_id_str = self.combo_amigos.get_active_id()
        if amigo_id_str is None: return None
        return {"amigo_id": int(amigo_id_str), "amount": self.spin_cantidad.get_value()}
 
class DialogoGasto(Gtk.Dialog):
    def __init__(self, parent, amigos: List[Amigo], on_accept_callback, gasto_existente: Optional[Gasto] = None):
        super().__init__(transient_for=parent, modal=True)
        self.on_accept_callback = on_accept_callback
        
        self.set_default_size(400, 450)
        self._build_ui(amigos)
        self.connect("response", self._on_response)

    def _build_ui(self, amigos):
        self.add_buttons("_Cancelar", Gtk.ResponseType.CANCEL, "_Aceptar", Gtk.ResponseType.OK)
        boton_aceptar = self.get_widget_for_response(Gtk.ResponseType.OK)
        boton_cancelar = self.get_widget_for_response(Gtk.ResponseType.CANCEL)
        boton_aceptar.set_margin_end(15)
        boton_cancelar.set_margin_end(5)
        boton_aceptar.set_margin_bottom(10)
        boton_cancelar.set_margin_bottom(10)

        self.amigos_checkboxes = {}
        content_area = self.get_content_area()
        grid = Gtk.Grid(margin_start=20, margin_end=20, margin_top=20, margin_bottom=10, row_spacing=15, column_spacing=10)
        content_area.append(grid)

        self.entry_desc = Gtk.Entry(hexpand=True)
        grid.attach(Gtk.Label(label="Descripción:"), 0, 0, 1, 1)
        grid.attach(self.entry_desc, 1, 0, 1, 1)

        self.entry_importe = Gtk.SpinButton.new_with_range(0, 999999, 5.00)
        self.entry_importe.set_digits(2)
        grid.attach(Gtk.Label(label="Importe (€):"), 0, 1, 1, 1)
        grid.attach(self.entry_importe, 1, 1, 1, 1)

        label_amigos = Gtk.Label(label="Amigos:", valign=Gtk.Align.START)
        grid.attach(label_amigos, 0, 2, 1, 1)
        
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        for amigo in amigos:
            cb = Gtk.CheckButton(label=amigo.name)
            self.amigos_checkboxes[amigo.id] = cb
            amigos_box.append(cb)
            
        scrolled_window = Gtk.ScrolledWindow(height_request=150, vexpand=True, hexpand=True)
        scrolled_window.set_child(amigos_box)
        grid.attach(scrolled_window, 1, 2, 1, 1)

    def _show_error_dialog(self, message: str):
        error_dialog = Gtk.MessageDialog(
            transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK, text=message
        )
        error_dialog.connect("response", lambda d, r: d.destroy())
        error_dialog.present()

    def _on_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            description = self.entry_desc.get_text().strip()
            amount = self.entry_importe.get_value()

            if not description:
                self._show_error_dialog("El campo 'Descripción' no puede estar vacío.")
                return 
            elif amount <= 0:
                self._show_error_dialog("El importe debe ser mayor que cero.")
                return

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
        self._build_ui()

    def set_presenter(self, p):
        self.presenter = p

    def _build_header(self):
        header = Gtk.HeaderBar()
        self.set_titlebar(header)
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        header.pack_end(menu_button)
        
        menu_popover = Gtk.PopoverMenu(has_arrow=False)
        menu_button.set_popover(menu_popover)
        
        menu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        menu_popover.set_child(menu_box)
        
        refresh_button = Gtk.Button(label="Refrescar")
        refresh_button.connect('clicked', lambda w: self.presenter.on_refresh_clicked())
        
        about_button = Gtk.Button(label="Acerca de...")
        about_button.connect('clicked', self._on_about_clicked)
        
        menu_box.append(refresh_button)
        menu_box.append(about_button)

    def _build_gastos_panel(self):
        gastos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        label = Gtk.Label(xalign=0, use_markup=True, hexpand=True)
        label.set_markup("<span size='xx-large' weight='bold'>GASTOS</span>")
        
        icon = Gtk.Image.new_from_icon_name("list-add-symbolic")
        icon.set_pixel_size(24)
        self.add_gasto_button = Gtk.Button(halign=Gtk.Align.END, child=icon)
        
        title_box.append(label)
        title_box.append(self.add_gasto_button)
        
        scrolled_window = Gtk.ScrolledWindow(vexpand=True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.lista_gastos = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        scrolled_window.set_child(self.lista_gastos)
        
        gastos_box.append(title_box)
        gastos_box.append(scrolled_window)
        return gastos_box

    def _build_amigos_panel(self):
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        label = Gtk.Label(xalign=0, use_markup=True)
        label.set_markup("<span size='xx-large' weight='bold'>AMIGOS</span>")
        
        scrolled_window = Gtk.ScrolledWindow(vexpand=True)
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.lista_amigos = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        scrolled_window.set_child(self.lista_amigos)
        
        amigos_box.append(label)
        amigos_box.append(scrolled_window)
        return amigos_box

    def _build_error_page(self):
        error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        try:
            error_image = Gtk.Image.new_from_file("../assets/images/wifi-off.png")
            error_image.set_pixel_size(128)
            error_box.append(error_image)
        except GLib.Error as e:
            print(f"Error al cargar la imagen de error: {e}")
        
        error_label = Gtk.Label(label="No es posible conectarse con el servidor")
        self.retry_button = Gtk.Button(label="Reintentar")
        
        error_box.append(error_label)
        error_box.append(self.retry_button)
        return error_box

    def _build_ui(self):
        self._build_header()
        
        overlay = Gtk.Overlay()
        self.set_child(overlay)
        
        self.spinner = Gtk.Spinner(spinning=False, visible=False, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, width_request=50, height_request=50)
        overlay.add_overlay(self.spinner)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        overlay.set_child(self.stack)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        main_box.append(self._build_gastos_panel())
        main_box.append(self._build_amigos_panel())
        
        error_page = self._build_error_page()

        self.stack.add_named(main_box, "main_content")
        self.stack.add_named(error_page, "error_screen")

    def _on_about_clicked(self, widget):
        about = Gtk.AboutDialog(transient_for=self, modal=True, program_name="SplitWithMe", version="Version 1.0")
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
        child_name = "error_screen" if visible else "main_content"
        self.stack.set_visible_child_name(child_name)

    def show_loading(self, is_loading: bool):
        self.spinner.set_visible(is_loading)
        self.spinner.set_spinning(is_loading)
        main_widget = self.get_child()
        if main_widget and main_widget.get_child():
             main_widget.get_child().set_sensitive(not is_loading)

    def _clear_list_box(self, list_box: Gtk.ListBox):
        while (child := list_box.get_row_at_index(0)):
            list_box.remove(child)

    def mostrar_gastos(self, gastos: List[Gasto]):
        self._clear_list_box(self.lista_gastos)
        for gasto in gastos:
            row_widget = GastoRow(gasto, self.presenter)
            self.lista_gastos.append(row_widget)

    def mostrar_amigos(self, amigos: List[Amigo]):
        self._clear_list_box(self.lista_amigos)
        for amigo in amigos:
            row_widget = AmigoRow(amigo, self.presenter)
            self.lista_amigos.append(row_widget)    

    def mostrar_dialogo_gasto(self, amigos: List[Amigo], on_accept_callback: Callable, gasto_existente: Optional[Gasto] = None) -> DialogoGasto:
        dialog = DialogoGasto(self, amigos, on_accept_callback, gasto_existente)
        dialog.present()
        return dialog

    def show_confirm_delete_dialog(self, gasto_id: int):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.YES_NO, text="¿Estás seguro de que quieres eliminar este gasto?")
        dialog.connect("response", lambda d, response_id: self._on_delete_dialog_response(d, response_id, gasto_id))
        dialog.present()

    def _on_delete_dialog_response(self, dialog, response_id, gasto_id):
        dialog.destroy()
        if response_id == Gtk.ResponseType.YES:
            self.presenter.on_confirm_delete(gasto_id)

    def mostrar_dialogo_aporte(self, amigos_participantes: List[Amigo], on_accept_callback: Callable):
        dialog = DialogoAporte(self, amigos_participantes)
        def on_response(d, response_id):
            if response_id == Gtk.ResponseType.OK:
                data = d.get_form_data()
                if data:
                    on_accept_callback(data["amigo_id"], data["amount"])
            d.destroy()
        dialog.connect("response", on_response)
        dialog.present()

    def get_gasto_row_by_id(self, gasto_id: int) -> Optional['GastoRow']:
        current_row = self.lista_gastos.get_row_at_index(0)
        idx = 0
        while current_row:
            if isinstance(current_row, Gtk.ListBoxRow):
                gasto_row_widget = current_row.get_child()
                if isinstance(gasto_row_widget, GastoRow) and gasto_row_widget.gasto_id == gasto_id:
                    return gasto_row_widget
            idx += 1
            current_row = self.lista_gastos.get_row_at_index(idx)
        return None


class GastoRow(Gtk.Box):  
    def __init__(self, gasto: Gasto, presenter):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.gasto_id = gasto.id 
        self.presenter = presenter
        
        self._build_main_row(gasto)
        
        self.revealer = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.append(self.revealer)

        self._connect_signals()

    def _build_main_row(self, gasto: Gasto):
        main_row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin_top=8, margin_bottom=8, margin_start=8, margin_end=8)
        info_label = Gtk.Label(xalign=0, hexpand=True, use_markup=True)
        info_label.set_markup(f"<b>{gasto.description}</b>\nImporte Total: {gasto.amount:.2f}€")
        
        buttons_box = Gtk.Box(spacing=5, halign=Gtk.Align.END)
        self.details_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        self.modify_button = Gtk.Button.new_from_icon_name("document-edit-symbolic")
        self.delete_button = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        self.delete_button.get_style_context().add_class("destructive-action")
        
        buttons_box.append(self.details_button)
        buttons_box.append(self.modify_button)
        buttons_box.append(self.delete_button)
        
        main_row_box.append(info_label)
        main_row_box.append(buttons_box)
        self.append(main_row_box)

    def _connect_signals(self):
        self.details_button.connect('clicked', self.on_details_clicked)
        self.modify_button.connect('clicked', lambda w: self.presenter.on_modify_gasto_clicked(self.gasto_id, self))
        self.delete_button.connect('clicked', lambda w: self.presenter.on_delete_gasto_clicked(self.gasto_id))

    def on_details_clicked(self, widget):
        if not self.revealer.get_child_revealed():
            self.presenter.on_details_gasto_clicked(self.gasto_id, self)
        else:
            self.revealer.set_reveal_child(False)

    def _build_details_view(self, gasto: Gasto):
        details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_start=20, margin_bottom=10)
        
        info_grid = Gtk.Grid(row_spacing=5, column_spacing=10)
        info_grid.attach(Gtk.Label(label="<b>Nombre:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        info_grid.attach(Gtk.Label(label=gasto.description, xalign=0, wrap=True), 1, 0, 1, 1)
        info_grid.attach(Gtk.Label(label="<b>Fecha:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        info_grid.attach(Gtk.Label(label=gasto.date or "N/A", xalign=0), 1, 1, 1, 1)
        info_grid.attach(Gtk.Label(label="<b>Nº de Amigos:</b>", use_markup=True, xalign=0), 0, 2, 1, 1)
        info_grid.attach(Gtk.Label(label=str(len(gasto.friends)), xalign=0), 1, 2, 1, 1)

        amounts_grid = Gtk.Grid(row_spacing=5, column_spacing=10)
        importe_pendiente = gasto.amount - gasto.credit_balance
        amounts_grid.attach(Gtk.Label(label="<b>Importe Inicial:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        amounts_grid.attach(Gtk.Label(label=f"{gasto.amount:.2f}€", xalign=0), 1, 0, 1, 1)
        amounts_grid.attach(Gtk.Label(label="<b>Importe Pagado:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        amounts_grid.attach(Gtk.Label(label=f"<span color='green'>{gasto.credit_balance:.2f}€</span>", use_markup=True, xalign=0), 1, 1, 1, 1) 
        amounts_grid.attach(Gtk.Label(label="<b>Pendiente:</b>", use_markup=True, xalign=0), 0, 2, 1, 1)
        amounts_grid.attach(Gtk.Label(label=f"<span weight='bold' color='red'>{importe_pendiente:.2f}€</span>", use_markup=True, xalign=0), 1, 2, 1, 1)

        friends_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        if not gasto.friends:
            friends_box.append(Gtk.Label(label="Ningún amigo participa en este gasto.", xalign=0, margin_start=10))
        else:
            for amigo in gasto.friends:
                friend_label = Gtk.Label(xalign=0, margin_start=10)
                friend_label.set_markup(f"{amigo.name} (Debe: <span weight='bold' color='red'>{amigo.debit_balance:.2f}€</span>)")
                friends_box.append(friend_label)

        aporte_button = Gtk.Button(label="Aportar Dinero")
        aporte_button.set_sensitive(importe_pendiente >= 0.01)
        aporte_button.connect('clicked', lambda w: self.presenter.on_open_aporte_dialog_clicked(gasto))
        
        details_box.append(info_grid)
        details_box.append(Gtk.Separator())
        details_box.append(amounts_grid)
        details_box.append(Gtk.Separator())
        details_box.append(Gtk.Label(label="<b>Participantes y Deudas:</b>", use_markup=True, xalign=0))
        details_box.append(friends_box)
        details_box.append(Gtk.Separator())
        details_box.append(aporte_button)
        return details_box

    def show_details_view(self, gasto_con_amigos: Gasto):
        if self.revealer.get_child():
            self.revealer.set_child(None)
        
        details_widget = self._build_details_view(gasto_con_amigos)
        self.revealer.set_child(details_widget)
        self.revealer.set_reveal_child(True)

    def _build_edit_view(self, gasto_editar: Gasto, todos_amigos: List[Amigo]):
        edit_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=10, column_spacing=10)
        
        entry_desc = Gtk.Entry(text=gasto_editar.description)
        edit_grid.attach(Gtk.Label(label="Descripción:"), 0, 0, 1, 1)
        edit_grid.attach(entry_desc, 1, 0, 1, 1)

        spin_importe = Gtk.SpinButton.new_with_range(0, 10000, 0.01)
        spin_importe.set_digits(2)
        spin_importe.set_value(gasto_editar.amount)
        edit_grid.attach(Gtk.Label(label="Importe (€):"), 0, 1, 1, 1)
        edit_grid.attach(spin_importe, 1, 1, 1, 1)

        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        amigos_checkboxes = {} 
        ids_amigos_actuales = {amigo.id for amigo in gasto_editar.friends}
        for amigo in todos_amigos:
            cb = Gtk.CheckButton(label=amigo.name)
            amigos_checkboxes[amigo.id] = cb
            if amigo.id in ids_amigos_actuales:
                cb.set_active(True)
            amigos_box.append(cb)
        scrolled_window = Gtk.ScrolledWindow(height_request=150, child=amigos_box)
        edit_grid.attach(Gtk.Label(label="Amigos:"), 0, 2, 1, 1)
        edit_grid.attach(scrolled_window, 1, 2, 1, 1)

        buttons_box = Gtk.Box(spacing=10, halign=Gtk.Align.END)
        save_button = Gtk.Button(label="Guardar")
        cancel_button = Gtk.Button(label="Cancelar")
        buttons_box.append(cancel_button)
        buttons_box.append(save_button)
        edit_grid.attach(buttons_box, 1, 3, 1, 1)

        cancel_button.connect('clicked', lambda w: self.revealer.set_reveal_child(False))
        save_button.connect('clicked', lambda w: self.presenter.on_save_changes_clicked(
            gasto_editar, entry_desc.get_text(), spin_importe.get_value(),
            {amigo_id: cb.get_active() for amigo_id, cb in amigos_checkboxes.items()}
        ))
        return edit_grid

    def update_edit_view(self, gasto_editar: Gasto, todos_amigos: List[Amigo]):
        if self.revealer.get_child():
            self.revealer.set_child(None)
            
        edit_widget = self._build_edit_view(gasto_editar, todos_amigos)
        self.revealer.set_child(edit_widget)
        self.revealer.set_reveal_child(True)

class AmigoRow(Gtk.Box):
    def __init__(self, amigo: Amigo, presenter):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.amigo = amigo
        self.presenter = presenter

        self._build_main_row(amigo)

        self.revealer = Gtk.Revealer(transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.append(self.revealer)

        self.details_button.connect('clicked', self.on_details_clicked)

    def _build_main_row(self, amigo: Amigo):
        main_row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin_top=8, margin_bottom=8, margin_start=8, margin_end=8)
        label = Gtk.Label(xalign=0, hexpand=True, use_markup=True)
        label.set_markup(f"<b>{amigo.name}</b>\nSaldo: {amigo.saldo:.2f}€")
        
        self.details_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        
        main_row_box.append(label)
        main_row_box.append(self.details_button)
        self.append(main_row_box)
        
    def on_details_clicked(self, widget):
        if not self.revealer.get_child_revealed():
            self.presenter.on_details_amigo_clicked(self.amigo.id, self)
        else:
            self.revealer.set_reveal_child(False)

    def show_details_view(self, amigo_con_detalles: Amigo, gastos_asociados: List[Gasto]):
        if self.revealer.get_child():
            self.revealer.set_child(None)

        details_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=5, column_spacing=10)
        gastos_str = "\n".join([f"- {g.description}" for g in gastos_asociados]) or "Ninguno"
        
        details_grid.attach(Gtk.Label(label="<b>Crédito:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        details_grid.attach(Gtk.Label(label=f"{amigo_con_detalles.credit_balance:.2f}€", xalign=0), 1, 0, 1, 1)
        details_grid.attach(Gtk.Label(label="<b>Débito:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        details_grid.attach(Gtk.Label(label=f"{amigo_con_detalles.debit_balance:.2f}€", xalign=0), 1, 1, 1, 1)
        details_grid.attach(Gtk.Label(label="<b>Gastos:</b>", use_markup=True, xalign=0, valign=Gtk.Align.START), 0, 2, 1, 1)
        details_grid.attach(Gtk.Label(label=gastos_str, xalign=0, wrap=True), 1, 2, 1, 1)

        self.revealer.set_child(details_grid)
        self.revealer.set_reveal_child(True)

class App(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id="com.example.splitwithme", **kwargs)