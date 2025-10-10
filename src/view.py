import gi 
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk 
from presenter import Presenter

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
        main_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.set_child(main_box)

        gastos_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
        main_box.append(gastos_box)

        gastos_label = Gtk.Label(label = "GASTOS")
        gastos_box.append(gastos_label)

        self.lista_gastos = Gtk.ListBox()
        self.lista_gastos.set_selection_mode(Gtk.SelectionMode.NONE)

        gastos_box.append(self.lista_gastos)

        self.add_gasto_button = Gtk.Button(label = "+")
        gastos_box.append(self.add_gasto_button)

        amigos_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
        main_box.append(amigos_box)

        amigos_label = Gtk.Label(label = "AMIGOS")
        amigos_box.append(amigos_label)

        self.lista_amigos = Gtk.ListBox()
        amigos_box.append(self.lista_amigos)

    def connect_signals(self):
        self.add_gasto_button.connect('clicked', self.presenter.on_add_gasto_clicked)

    def mostrar_gastos(self, gastos):
        while child := self.lista_gastos.get_first_child():
            self.lista_gastos.remove(child)

        for gasto in gastos:

            row = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 50)
            label_desc = Gtk.Label(label = gasto.descripcion)
            label_importe = Gtk.Label(label = f"{gasto.importe: .2f}€")
            row.append(label_desc)
            row.append(label_importe)
            self.lista_gastos.append(row)

    def mostrar_amigos(self, amigos):

        while child := self.lista_amigos.get_first_child():
            self.lista_amigos.remove(child)

        for amigo in amigos:
            label = Gtk.Label(label = f"{amigo.nombre}  (Saldo: {amigo.saldo: .2f}€)")
            self.lista_amigos.append(label)

class App(Gtk.Application):
    def __init__(self, modelo, **kwargs):
        super().__init__(application_id = "com.example.splitwithme", **kwargs)
        self.modelo = modelo
        self.win = None 

    def do_activate(self):
        if not self.win:
            self.win = VistaPrincipal(application = self)
            presentador = Presenter(self.win, self.modelo)
            presentador.iniciar()
        self.win.present()