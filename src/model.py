class Gasto:
    def __init__(self, id, descripcion, importe):
        self.id = id 
        self.descripcion = descripcion
        self.importe = importe

class Amigo: 
    def __init__(self, id, nombre, saldo):
        self.id = id 
        self.nombre = nombre
        self.saldo = saldo

class Model: 

    def get_gastos(self):
        print("MODELO: Obteniendo gastos...")

        gastos_prueba = [
            Gasto(1, "Cena equipo", 50.0),
            Gasto(2, "Viaje Madrid", 100.0),
            Gasto(3, "Compra supermercado", 80.0),
            Gasto(4, "Entradas partido", 40.0),
        ]
        return gastos_prueba

    def get_amigos(self):
        print("MODELO: Obteniendo amigos...")

        amigos_prueba = [
            Amigo(1, "Pablo", 20.0),
            Amigo(2, "Joel", 15.5),
            Amigo(3, "Nico", 12.0),
            Amigo(4, "Sebastian", 6.75),
        ]
        return amigos_prueba