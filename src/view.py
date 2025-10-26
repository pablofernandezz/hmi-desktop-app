import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")
from gi.repository import Gtk, GLib, Gio
from typing import List, Optional, Callable
from datetime import datetime
import gettext
import locale

from model import Gasto, Amigo, AmigoEnGasto

#alias para las traducciones
_ = gettext.gettext

#funciones auxilixares para el formateo
def format_currency(amount: float) -> str:
    try:
        return locale.currency(amount, grouping=True)
    except ValueError:
        return f"{amount:.2f} €" #default
    
def format_date(date_str: str) ->str:
    if not date_str:
        return _("N/A")
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%x")  #x es el formato de fecha local
    except (ValueError, TypeError):
        return date_str # si falla fecha original
    
#Clases de view
class DialogoAporte(Gtk.Dialog):
    def __init__(self, parent, amigos_participantes: List['AmigoEnGasto']):
        super().__init__(transient_for=parent, modal=True, title=_("Realizar Aporte"))
        self.add_buttons(_("_Cancelar"), Gtk.ResponseType.CANCEL, _("_Aceptar"), Gtk.ResponseType.OK)
        self.amigos_participantes = amigos_participantes

        content_area = self.get_content_area()
        grid = Gtk.Grid(margin_start=10, margin_end=10, margin_top=10, margin_bottom=10, row_spacing=10, column_spacing=10)
        content_area.append(grid)

        grid.attach(Gtk.Label(label=_("Amigo:")), 0, 0, 1, 1)
        self.combo_amigos = Gtk.ComboBoxText()
        for amigo in self.amigos_participantes:
            if amigo.debit_balance > 0.01:
                deuda_formateada = format_currency(amigo.debit_balance)
                texto_combo = _("{name} (debe {deuda})").format(name=amigo.name, deuda=deuda_formateada)
                self.combo_amigos.append(str(amigo.id), texto_combo)
        grid.attach(self.combo_amigos, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label=_("Cantidad:")), 0, 1, 1, 1)
        self.spin_cantidad = Gtk.SpinButton.new_with_range(0.01, 10000, 2.50)
        self.spin_cantidad.set_digits(2)
        grid.attach(self.spin_cantidad, 1, 1, 1, 1)

        self.combo_amigos.connect("changed", self.on_amigo_selected)
        if self.combo_amigos.get_active() == -1 and any(a.debit_balance > 0.01 for a in self.amigos_participantes):
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
        self.add_buttons(_("_Cancelar"), Gtk.ResponseType.CANCEL, _("_Aceptar"), Gtk.ResponseType.OK)
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
        grid.attach(Gtk.Label(label=_("Descripción:")), 0, 0, 1, 1)
        grid.attach(self.entry_desc, 1, 0, 1, 1)

        self.entry_importe = Gtk.SpinButton.new_with_range(0, 999999, 2.50)
        self.entry_importe.set_digits(2)
        grid.attach(Gtk.Label(label=_("Importe:")), 0, 1, 1, 1)
        grid.attach(self.entry_importe, 1, 1, 1, 1)

        label_amigos = Gtk.Label(label=_("Amigos:"), valign=Gtk.Align.START)
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
                self._show_error_dialog(_("El campo 'Descripción' no puede estar vacío."))
                return 
            elif amount <= 0:
                self._show_error_dialog(_("El importe debe ser mayor que cero."))
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

    def run_on_ui_thread(self, func, *args, **kwargs):
        GLib.idle_add(func, *args, **kwargs)

    def show_row_loading(self, gasto_id: int, is_loading: bool):
        row = self.get_gasto_row_by_id(gasto_id)
        if row:
            row.show_row_loading(is_loading)

    def show_amigo_row_loading(self, amigo_id: int, is_loading: bool):
        row = self.get_amigo_row_by_id(amigo_id)
        if row:
            row.show_row_loading(is_loading)

    def update_initial_data(self, gastos, amigos):
        if gastos is None or amigos is None:
            self.show_connection_error(True)
        else:
            self.show_connection_error(False)
            self.mostrar_gastos(gastos)
            self.mostrar_amigos(amigos)
        
        self.show_loading(False)

    def show_gasto_details_or_error(self, gasto_id: int, gasto_con_detalles: Gasto, amigos: List[Amigo]):
        row = self.get_gasto_row_by_id(gasto_id)
        if gasto_con_detalles and amigos and row:
            row.show_unified_view(gasto_con_detalles, amigos)
        elif not gasto_con_detalles:
            self.show_connection_error(True)
        
        if row:
            row.show_row_loading(False)

    def show_gasto_edit_or_error(self, gasto_id: int, gasto: Gasto, amigos: List[Amigo]):
        row = self.get_gasto_row_by_id(gasto_id)
        if gasto and amigos and row:
            row.update_edit_view(gasto, amigos)
        elif not (gasto and amigos):
            self.show_connection_error(True)

        if row:
            row.show_row_loading(False)
    
    def show_amigo_details_or_error(self, amigo_id: int, amigo: Amigo, gastos: List[Gasto]):
        row = self.get_amigo_row_by_id(amigo_id)
        if amigo and gastos is not None and row:
            row.show_details_view(amigo, gastos)
        elif not (amigo and gastos is not None):
            self.show_connection_error(True)
        
        if row:
            row.show_row_loading(False)

    def reload_data_or_error(self, success: bool, gasto_id: int = None, amigo_id: int = None):
        if success:
            self.presenter.cargar_datos_principales()
        else:
            self.show_connection_error(True)
            if gasto_id:
                self.show_row_loading(gasto_id, False)
            if amigo_id:
                self.show_amigo_row_loading(amigo_id, False)
            self.show_loading(False)

    def set_presenter(self, p):
        self.presenter = p

    def _build_header(self):
        header = Gtk.HeaderBar()
        self.set_titlebar(header)
        
        self.header_spinner = Gtk.Spinner(spinning=False, visible=False)
        header.pack_start(self.header_spinner)
        
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        header.pack_end(menu_button)
        
        menu_model = Gio.Menu()
        menu_section = Gio.Menu()
        menu_model.append_section(None, menu_section)
        menu_section.append(_("Refrescar"), "win.refresh")
        menu_section.append(_("Acerca de..."), "win.about")
        
        refresh_action = Gio.SimpleAction.new("refresh", None)
        refresh_action.connect("activate", lambda a, p: self.presenter.on_refresh_clicked())
        self.add_action(refresh_action)
        
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about_clicked)
        self.add_action(about_action)
        
        menu_button.set_menu_model(menu_model)

    def _build_gastos_panel(self):
        gastos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        label = Gtk.Label(xalign=0, use_markup=True, hexpand=True)
        label.set_markup(f"<span size='xx-large' weight='bold'>{_('GASTOS')}</span>")
        
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
        label.set_markup(f"<span size='xx-large' weight='bold'>{_('AMIGOS')}</span>")
        
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
        
        error_label = Gtk.Label(label=_("No es posible conectarse con el servidor"))
        self.retry_button = Gtk.Button(label=_("Reintentar"))
        
        error_box.append(error_label)
        error_box.append(self.retry_button)
        return error_box

    def _build_ui(self):
        self._build_header()
        
        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        self.set_child(self.stack)

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        main_box.append(self._build_gastos_panel())
        main_box.append(self._build_amigos_panel())
        
        error_page = self._build_error_page()

        self.stack.add_named(main_box, "main_content")
        self.stack.add_named(error_page, "error_screen")

    def _on_about_clicked(self, action, parameter):        
        about = Gtk.AboutDialog(transient_for=self, modal=True, program_name="SplitWithMe", version=_("Versión 1.0"))
        about.set_authors(["Pablo Fernández Martí", "Joel Ramos Carro", "Nicolás Dominguez Souto"])
        about.set_comments(_("Aplicación de escritorio para la gestión de gastos compartidos con amigos."))
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
        self.header_spinner.set_visible(is_loading)
        self.header_spinner.set_spinning(is_loading)

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
        dialog = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.WARNING,
                                   buttons=Gtk.ButtonsType.YES_NO, text=_("¿Estás seguro de que quieres eliminar este gasto?"))
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
            gasto_row_widget = current_row.get_child()
            if isinstance(gasto_row_widget, GastoRow) and gasto_row_widget.gasto_id == gasto_id:
                return gasto_row_widget
            idx += 1
            current_row = self.lista_gastos.get_row_at_index(idx)
        return None
    
    def get_amigo_row_by_id(self, amigo_id: int) -> Optional['AmigoRow']:
        current_row = self.lista_amigos.get_row_at_index(0)
        idx = 0
        while current_row:
            amigo_row_widget = current_row.get_child()
            if isinstance(amigo_row_widget, AmigoRow) and amigo_row_widget.amigo.id == amigo_id:
                return amigo_row_widget
            idx += 1
            current_row = self.lista_amigos.get_row_at_index(idx)
        return None
    
    def show_error_dialog(self, message: str):
        error_dialog = Gtk.MessageDialog(
            transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK, text=message # el mensaje ya viene traducido
        )
        error_dialog.connect("response", lambda d, r: d.destroy())
        error_dialog.present()


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
        importe_formateado = format_currency(gasto.amount)
        info_label.set_markup(f"<b>{gasto.description}</b>\n{_('Importe Total')}: {importe_formateado}")
        
        buttons_box = Gtk.Box(spacing=5, halign=Gtk.Align.END)
        self.details_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        self.delete_button = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        self.delete_button.get_style_context().add_class("destructive-action")
        
        self.row_spinner = Gtk.Spinner(spinning=False, visible=False)
        buttons_box.append(self.row_spinner)
        
        buttons_box.append(self.details_button)
        buttons_box.append(self.delete_button)
        
        main_row_box.append(info_label)
        main_row_box.append(buttons_box)
        self.append(main_row_box)

    def show_row_loading(self, is_loading: bool):
        self.row_spinner.set_visible(is_loading)
        self.row_spinner.set_spinning(is_loading)
        self.details_button.set_sensitive(not is_loading)
        self.delete_button.set_sensitive(not is_loading)

    def _connect_signals(self):
        self.details_button.connect('clicked', self.on_details_clicked)
        self.delete_button.connect('clicked', lambda w: self.presenter.on_delete_gasto_clicked(self.gasto_id))

    def on_details_clicked(self, widget):
        if not self.revealer.get_child_revealed():
            self.presenter.on_details_gasto_clicked(self.gasto_id)
        else:
            self.revealer.set_reveal_child(False)

    def _build_unified_view(self, gasto: Gasto, todos_amigos: List[Amigo]):
        unified_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15, 
                            margin_start=20, margin_end=20, margin_bottom=10)
        
        # Crear ventanas
        notebook = Gtk.Notebook(margin_top=10, margin_bottom=10, 
                            margin_start=10, margin_end=10)
        unified_box.append(notebook)

        # ventana 1: Información (editable)
        info_tab = self._build_info_tab(gasto, todos_amigos)
        # markup para el color del texto de la venta, ns pq no se adapta al tema ocuro y de normal se ve fondo blanco y letras blancas
        tab1_label = Gtk.Label()
        tab1_label.set_markup(f"<span color='black' weight='bold'>{_('Información')}</span>")
        notebook.append_page(info_tab, tab1_label)

        # ventana 2: Aportes (solo lectura)
        aportes_tab = self._build_aportes_tab(gasto)
        #  markup para el color del texto
        tab2_label = Gtk.Label()
        tab2_label.set_markup(f"<span color='black' weight='bold'>{_('Aportes')}</span>")
        notebook.append_page(aportes_tab, tab2_label)
        
        return unified_box

    def _build_info_tab(self, gasto: Gasto, todos_amigos: List[Amigo]):
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        edit_grid = Gtk.Grid(row_spacing=10, column_spacing=10)
        
        # campo Descripción 
        edit_grid.attach(Gtk.Label(label=_("Descripción:"), xalign=0), 0, 0, 1, 1)
        self.entry_desc = Gtk.Entry(text=gasto.description, hexpand=True)
        edit_grid.attach(self.entry_desc, 1, 0, 1, 1)
        
        # logica del calendario para la fecha
        edit_grid.attach(Gtk.Label(label=_("Fecha:"), xalign=0), 0, 1, 1, 1)
        date_button = Gtk.MenuButton(label=format_date(gasto.date) or _("Seleccionar fecha"))
        
        popover = Gtk.Popover()
        calendar = Gtk.Calendar()
        popover.set_child(calendar)
        
        date_button.set_popover(popover)
        
        # estado inicial del calendario
        if gasto.date:
            try:
                fecha_dt = datetime.strptime(gasto.date, "%Y-%m-%d")
                year = fecha_dt.year
                month = fecha_dt.month
                day = fecha_dt.day
                datetime_obj = GLib.DateTime.new_local(year, month, day, 0, 0, 0)
                calendar.select_day(datetime_obj)
            except (ValueError, TypeError) as e:
                print(f"Error al parsear la fecha inicial del gasto: {e}")

        # conectar la señal para cuando el usuario selecciona un día
        def on_day_selected(cal):
            date = cal.get_date()  
            new_date_str = f"{date.get_year()}-{date.get_month():02d}-{date.get_day_of_month():02d}"
            date_button.set_label(format_date(new_date_str))
            popover.popdown()
            
        calendar.connect("day-selected", on_day_selected)
        
        edit_grid.attach(date_button, 1, 1, 1, 1)
        
        # campo importe total
        self.spin_importe = Gtk.SpinButton.new_with_range(0.01, 10000, 2.50)
        self.spin_importe.set_digits(2)
        self.spin_importe.set_value(gasto.amount)
        edit_grid.attach(Gtk.Label(label=_("Importe Total (€):"), xalign=0), 0, 2, 1, 1)
        edit_grid.attach(self.spin_importe, 1, 2, 1, 1)
        
        info_box.append(edit_grid)
        
        # checkboxes para amigos
        amigos_label = Gtk.Label(label=f"<b>{_('Amigos participantes')}:</b>", use_markup=True, xalign=0, margin_top=10)
        info_box.append(amigos_label)
        amigos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin_start=10)
        self.amigos_checkboxes = {}
        amigos_actuales_dict = {amigo.id: amigo.credit_balance for amigo in gasto.friends}
        for amigo in todos_amigos:
            cb = Gtk.CheckButton(label=amigo.name)
            self.amigos_checkboxes[amigo.id] = cb
            if amigo.id in amigos_actuales_dict:
                cb.set_active(True)
                if amigos_actuales_dict[amigo.id] > 0.01:
                    cb.set_sensitive(False)
                    cb.set_tooltip_text(_("No se puede eliminar este amigo porque ya ha realizado pagos en este gasto"))
            amigos_box.append(cb)
        scrolled_window = Gtk.ScrolledWindow(height_request=120, child=amigos_box)
        info_box.append(scrolled_window)
        
        # botones de acción
        buttons_box = Gtk.Box(spacing=10, halign=Gtk.Align.END, margin_top=10)
        cancel_button = Gtk.Button(label=_("Cancelar"))
        save_button = Gtk.Button(label=_("Guardar cambios"))
        buttons_box.append(cancel_button)
        buttons_box.append(save_button)
        info_box.append(buttons_box)
        
        cancel_button.connect('clicked', lambda w: self.revealer.set_reveal_child(False))
        
        save_button.connect('clicked', lambda w: self.presenter.on_save_changes_clicked(
            gasto, 
            self.entry_desc.get_text(), 
            self.spin_importe.get_value(),
            datetime.strptime(date_button.get_label(), "%x").strftime("%Y-%m-%d"),
            {amigo_id: cb.get_active() for amigo_id, cb in self.amigos_checkboxes.items()}
        ))
        
        return info_box

    def _build_aportes_tab(self, gasto: Gasto):
        aportes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        
        # campo para importes (solo lectura)
        amounts_grid = Gtk.Grid(row_spacing=5, column_spacing=10)
        importe_pendiente = gasto.amount - gasto.credit_balance
        
        amounts_grid.attach(Gtk.Label(label=f"<b>{_('Importe Total')}:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        amounts_grid.attach(Gtk.Label(label=format_currency(gasto.amount), xalign=0), 1, 0, 1, 1)
        amounts_grid.attach(Gtk.Label(label=f"<b>{_('Importe Pagado')}:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        amounts_grid.attach(Gtk.Label(label=f"<span weight='bold' color='green'>{format_currency(gasto.credit_balance)}</span>", use_markup=True, xalign=0), 1, 1, 1, 1) 
        amounts_grid.attach(Gtk.Label(label=f"<b>{_('Pendiente')}:</b>", use_markup=True, xalign=0), 0, 2, 1, 1)
        amounts_grid.attach(Gtk.Label(label=f"<span weight='bold' color='red'>{format_currency(importe_pendiente)}</span>", use_markup=True, xalign=0), 1, 2, 1, 1) 
        
        aportes_box.append(amounts_grid)
        aportes_box.append(Gtk.Separator())
        
        # lista de amigos participantes y sus deudas
        friends_label = Gtk.Label(label=f"<b>{_('Participantes y Deudas')}:</b>", use_markup=True, xalign=0)
        aportes_box.append(friends_label)
        
        friends_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, margin_start=10)
        if not gasto.friends:
            friends_box.append(Gtk.Label(label=_("Ningún amigo participa en este gasto."), xalign=0))
        else:
            for amigo in gasto.friends:
                friend_label = Gtk.Label(xalign=0)
                friend_label.set_markup(_("{name} (Debe: <span weight='bold' color='red'>{deuda}</span>)").format(name=amigo.name, deuda=format_currency(amigo.debit_balance)))
                friends_box.append(friend_label)
        
        aportes_box.append(friends_box)
        
        # botón de realizar aporte
        aporte_button = Gtk.Button(label=_("Realizar Aporte"), margin_top=10)
        aporte_button.set_sensitive(importe_pendiente >= 0.01)
        aporte_button.connect('clicked', lambda w: self.presenter.on_open_aporte_dialog_clicked(gasto))
        aportes_box.append(aporte_button)
        
        return aportes_box

    def show_unified_view(self, gasto_con_detalles: Gasto, amigos: List[Amigo]):
        if self.revealer.get_child():
            self.revealer.set_child(None)
        
        unified_widget = self._build_unified_view(gasto_con_detalles, amigos)
        self.revealer.set_child(unified_widget)
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
        saldo_formateado = format_currency(amigo.saldo)
        label.set_markup(f"<b>{amigo.name}</b>\n{_('Saldo')}: {saldo_formateado}")
        
        self.details_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        self.row_spinner = Gtk.Spinner(spinning=False, visible=False)

        main_row_box.append(label)
        main_row_box.append(self.row_spinner)
        main_row_box.append(self.details_button)
        self.append(main_row_box)
    
    def show_row_loading(self, is_loading: bool):
        self.row_spinner.set_visible(is_loading)
        self.row_spinner.set_spinning(is_loading)
        self.details_button.set_sensitive(not is_loading)
    
    def on_details_clicked(self, widget):
        if not self.revealer.get_child_revealed():
            self.presenter.on_details_amigo_clicked(self.amigo.id)
        else:
            self.revealer.set_reveal_child(False)

    def show_details_view(self, amigo_con_detalles: Amigo, gastos_asociados: List[Gasto]):
        if self.revealer.get_child():
            self.revealer.set_child(None)

        details_grid = Gtk.Grid(margin_start=20, margin_bottom=10, row_spacing=5, column_spacing=10)
        gastos_str = "\n".join([f"- {g.description}" for g in gastos_asociados]) or "Ninguno"
        
        details_grid.attach(Gtk.Label(label=f"<b>{_('Crédito')}:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        details_grid.attach(Gtk.Label(label=format_currency(amigo_con_detalles.credit_balance), xalign=0), 1, 0, 1, 1)
        details_grid.attach(Gtk.Label(label=f"<b>{_('Débito')}:</b>", use_markup=True, xalign=0), 0, 1, 1, 1)
        details_grid.attach(Gtk.Label(label=format_currency(amigo_con_detalles.debit_balance), xalign=0), 1, 1, 1, 1)
        details_grid.attach(Gtk.Label(label=f"<b>{_('Gastos')}:</b>", use_markup=True, xalign=0, valign=Gtk.Align.START), 0, 2, 1, 1)
        details_grid.attach(Gtk.Label(label=gastos_str, xalign=0, wrap=True), 1, 2, 1, 1)

        self.revealer.set_child(details_grid)
        self.revealer.set_reveal_child(True)

class App(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id="com.example.splitwithme", **kwargs)