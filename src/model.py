# model.py 
import requests

### Modelos de datos
class Gasto:
    def __init__(self, id, description, amount, date=None, credit_balance=0, num_friends=0, friends=None, **kwargs):
        self.id = id 
        self.description = description
        self.amount = amount
        self.date = date
        self.credit_balance = credit_balance
        self.num_friends = num_friends
        self.friends = friends if friends is not None else []

class Amigo: 
    def __init__(self, id, name, credit_balance, debit_balance):
        self.id = id 
        self.name = name
        self.credit_balance = credit_balance
        self.debit_balance = debit_balance

    @property
    def saldo(self):
        return self.credit_balance - self.debit_balance


### Clase de lógica de negocio
class Model: 
    def __init__(self):
        self.api_url = "http://127.0.0.1:8000"

    def get_gastos(self):
        print("MODELO: Obteniendo gastos desde el servidor...")
        try:
            response = requests.get(f"{self.api_url}/expenses")
            response.raise_for_status()
            gastos_json = response.json()
            
            gastos = [Gasto(**gasto_data) for gasto_data in gastos_json]
            print(f"MODELO: {len(gastos)} gastos obtenidos.")
            return gastos
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al obtener lista de gastos: {e}")
            return None
        
    def get_gasto_details(self, gasto_id: int):
        print(f"MODELO: Obteniendo detalles del gasto {gasto_id} desde el servidor...")
        try:
            response=requests.get(f"{self.api_url}/expenses/{gasto_id}")
            response.raise_for_status()
            gasto_data=response.json()
        
            amigos_en_gastos=self.get_amigos_por_gasto(gasto_id)
            gasto= Gasto(**gasto_data)
            gasto.friends=amigos_en_gastos
            return gasto
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al obtener detalles del gasto {gasto_id}: {e}")
            return None


    def get_amigos(self):
        print("MODELO: Obteniendo amigos desde el servidor...")
        try:
            response = requests.get(f"{self.api_url}/friends")
            response.raise_for_status()
            amigos_json = response.json()

            amigos = [Amigo(**amigo_data) for amigo_data in amigos_json]
            print(f"MODELO: {len(amigos)} amigos obtenidos.")
            return amigos
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al obtener lista de amigos: {e}")
            return None
        
    def get_amigo_details(self, amigo_id: int):
        print(f"MODELO: Obteniendo detalles del amigo {amigo_id} desde el servidor...")
        try:
            response = requests.get(f"{self.api_url}/friends/{amigo_id}")
            response.raise_for_status()
            return Amigo(**response.json())
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al obtener detalles del amigo {amigo_id}: {e}")
            return None
        
    def get_gastos_por_amigo(self, amigo_id: int):
        print(f"MODELO: Obteniendo gastos asociados a amigo {amigo_id} desde el servidor...")
        try:
            response = requests.get(f"{self.api_url}/friends/{amigo_id}/expenses")
            response.raise_for_status()
            gastos_json = response.json()
            return [Gasto(**gasto_data) for gasto_data in gastos_json]
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al obtener gastos del amigo {amigo_id}: {e}")
            return []

    def get_amigos_por_gasto(self, gasto_id: int) -> list[Amigo]:
        print(f"MODELO: Obteniendo amigos asociados al gasto {gasto_id} desde el servidor...")
        try:
            response = requests.get(f"{self.api_url}/expenses/{gasto_id}/friends")
            response.raise_for_status()
            amigos_json = response.json()
            return [Amigo(**amigo_data) for amigo_data in amigos_json]
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al obtener amigos del gasto {gasto_id}: {e}")
            return []
    
    def add_amigo_a_gasto(self, gasto_id: int, amigo_id: int) -> bool:
        print(f"MODELO: Asociando amigo {amigo_id} al gasto {gasto_id}...")
        try:
            url = f"{self.api_url}/expenses/{gasto_id}/friends" 
            response = requests.post(url, params={"friend_id": amigo_id})
            response.raise_for_status()
            print(f"MODELO: Amigo {amigo_id} asociado al gasto {gasto_id} con éxito.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al asociar amigo {amigo_id} al gasto {gasto_id}: {e}")
            return False
    
    def remove_amigo_de_gasto(self, gasto_id: int, amigo_id: int) -> bool:
        print(f"MODELO: Desasociando amigo {amigo_id} del gasto {gasto_id}...")
        try:
            response = requests.delete(f"{self.api_url}/expenses/{gasto_id}/friends/{amigo_id}")
            response.raise_for_status()
            print(f"MODELO: Amigo {amigo_id} desasociado del gasto {gasto_id} con éxito.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al desasociar amigo {amigo_id} del gasto {gasto_id}: {e}")
            return False

    def create_gasto(self, datos_gasto: dict) -> Optional[Gasto]:
        print(f"MODELO: Creando nuevo gasto con datos: {datos_gasto}")
        try:
            response = requests.post(f"{self.api_url}/expenses", json=datos_gasto)
            response.raise_for_status()
            return Gasto(**response.json)
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al crear el gasto: {e}")
            return None

    def update_gasto(self, gasto_id: int, datos_gasto: dict) -> bool:
        print(f"MODELO: Actualizando gasto {gasto_id} con datos: {datos_gasto}")
        try:
            response = requests.put(f"{self.api_url}/expenses/{gasto_id}", json=datos_gasto)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al actualizar el gasto {gasto_id}: {e}")
            return False

    def delete_gasto(self, gasto_id: int) -> bool:
        print(f"MODELO: Eliminando gasto {gasto_id}")
        try:
            response = requests.delete(f"{self.api_url}/expenses/{gasto_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al eliminar el gasto {gasto_id}: {e}")
            return False

            