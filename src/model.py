import requests
import time

class Gasto:
    def __init__(self, id, description, amount, date=None, credit_balance=0, num_friends=0, friends: list['AmigoEnGasto'] = None, **kwargs):
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

class AmigoEnGasto: 
    def __init__(self, id, name, credit_balance, debit_balance, **kwargs):
        self.id = id 
        self.name = name
        self.credit_balance = credit_balance
        self.debit_balance = debit_balance

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

    def get_amigos_por_gasto(self, gasto_id: int) -> list['AmigoEnGasto']:
        print(f"MODELO: Obteniendo amigos asociados al gasto {gasto_id} desde el servidor...")
        try:
            response = requests.get(f"{self.api_url}/expenses/{gasto_id}/friends")
            response.raise_for_status()
            amigos_json = response.json()
            
            # Obtener detalles del gasto para conocer el importe total
            gasto_response = requests.get(f"{self.api_url}/expenses/{gasto_id}")
            gasto_response.raise_for_status()
            gasto_data = gasto_response.json()
            importe_total = gasto_data['amount']
            
            # Obtener el crédito pagado del gasto
            credito_total_gasto = gasto_data.get('credit_balance', 0)
            
            # Calcular débitos actualizados
            amigos_actualizados = []
            num_amigos = len(amigos_json) + 1 # Incluye al usuario principal
            
            for amigo_data in amigos_json:
                # Calcular la parte que le corresponde a cada amigo
                parte_proporcional = importe_total / num_amigos
                 
                # Calcular el débito actualizado
                debito_actualizado = parte_proporcional - amigo_data.get('credit_balance', 0)
                
                # Actualizar el débito en los datos del amigo
                amigo_data['debit_balance'] = debito_actualizado
                amigos_actualizados.append(AmigoEnGasto(**amigo_data))
            
            return amigos_actualizados
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al obtener amigos del gasto {gasto_id}: {e}")
            return []
    
    def add_amigo_a_gasto(self, gasto_id: int, amigo_id: int) -> bool:
        print(f"MODELO: Asociando amigo {amigo_id} al gasto {gasto_id}...")
        try:
            response = requests.post(f"{self.api_url}/expenses/{gasto_id}/friends", params={"friend_id": amigo_id})
            response.raise_for_status()
            print(f"MODELO: Amigo {amigo_id} asociado al gasto {gasto_id} con éxito.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al asociar amigo {amigo_id} al gasto {gasto_id}: {e}")
            if e.response is not None:
                print(f"MODELO: Respuesta del servidor ({e.response.status_code}): {e.response.text}")
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
            if e.response is not None:
                print(f"MODELO: Respuesta del servidor ({e.response.status_code}): {e.response.text}")
            return False

    def create_gasto(self, datos_gasto: dict) -> bool:
        print(f"MODELO: Creando nuevo gasto con datos: {datos_gasto}")
        try:
            response = requests.post(f"{self.api_url}/expenses", json=datos_gasto)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al crear el gasto: {e}")
            return False

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
            
    def create_gasto_with_friends(self, datos_gasto: dict) -> bool:
        friend_ids = datos_gasto.pop('friend_ids', [])
    
        gastos_previos = self.get_gastos()
        if gastos_previos is None: return False
        ids_previos = {g.id for g in gastos_previos}

        if not self.create_gasto(datos_gasto):
            return False

        gastos_nuevos = self.get_gastos()
        if gastos_nuevos is None: return False
        ids_nuevos = {g.id for g in gastos_nuevos}

        nuevos_ids_encontrados = ids_nuevos - ids_previos
        if not nuevos_ids_encontrados:
            print("MODELO: No se pudo determinar el ID del nuevo gasto.")
            return False
        
        nuevo_gasto_id = nuevos_ids_encontrados.pop()

        for friend_id in friend_ids:
            self.add_amigo_a_gasto(nuevo_gasto_id, friend_id)

        return True
    
    def add_aporte_a_gasto(self, gasto_id: int, amigo_id: int, amount: float) -> bool:
        print(f"MODELO: Añadiendo aporte de {amount}€ por amigo {amigo_id} al gasto {gasto_id}")
        url = f"{self.api_url}/expenses/{gasto_id}/contributions"
        payload = {"friend_id": amigo_id, "amount": amount}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print("MODELO: Aporte añadido con éxito.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al añadir el aporte: {e}")
            if e.response is not None:
                print(f"MODELO: Respuesta del servidor ({e.response.status_code}): {e.response.text}")
            return False
    
    def make_payment_for_friend(self, gasto_id: int, amigo_id: int, amount: float) -> bool:
        print(f"MODELO: Amigo {amigo_id} va a pagar {amount}€ para el gasto {gasto_id}")
        try:
            response = requests.put(
                f"{self.api_url}/expenses/{gasto_id}/friends/{amigo_id}",
                params={"amount": amount}
            )
            response.raise_for_status()
            print("MODELO: Aporte realizado con éxito.")
            
            time.sleep(0.5)  # Pequeña pausa para asegurar la persistencia en el servidor
            return True
        except requests.exceptions.RequestException as e:
            print(f"MODELO: Error al realizar el aporte: {e}")
            if e.response is not None:
                print(f"MODELO: Respuesta del servidor ({e.response.status_code}): {e.response.text}")
            return False