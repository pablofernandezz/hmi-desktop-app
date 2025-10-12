# scripts/populate_db.py

import requests
import random
from faker import Faker
from typing import List

# --- Configuración ---
API_URL = "http://127.0.0.1:8000"
NUM_AMIGOS = 8
NUM_GASTOS = 20
# ---------------------

# Inicializa Faker para generar datos en español
fake = Faker('es_ES')

def crear_amigos(n: int) -> List[int]:
    """Crea 'n' amigos en el servidor y devuelve sus IDs."""
    print(f"--- Creando {n} amigos... ---")
    ids_amigos = []
    for i in range(n):
        nombre = fake.name()
        try:
            response = requests.post(f"{API_URL}/friends", json={"name": nombre})
            response.raise_for_status()  # Lanza un error si la petición falla
            nuevo_amigo = response.json()
            ids_amigos.append(nuevo_amigo['id'])
            print(f"[{i+1}/{n}] Amigo creado: {nuevo_amigo['name']} (ID: {nuevo_amigo['id']})")
        except requests.exceptions.RequestException as e:
            print(f"Error al crear amigo '{nombre}': {e}")
    return ids_amigos

def crear_gastos(n: int) -> List[int]:
    """Crea 'n' gastos en el servidor y devuelve sus IDs."""
    print(f"\n--- Creando {n} gastos... ---")
    ids_gastos = []
    for i in range(n):
        gasto_data = {
            "description": fake.sentence(nb_words=4).capitalize().replace('.', ''),
            "amount": round(random.uniform(5.5, 280.0), 2),
            "date": str(fake.date_this_year())
        }
        try:
            response = requests.post(f"{API_URL}/expenses", json=gasto_data)
            response.raise_for_status()
            nuevo_gasto = response.json()
            ids_gastos.append(nuevo_gasto['id'])
            print(f"[{i+1}/{n}] Gasto creado: '{nuevo_gasto['description']}' (ID: {nuevo_gasto['id']})")
        except requests.exceptions.RequestException as e:
            print(f"Error al crear gasto: {e}")
    return ids_gastos

def asociar_amigos_a_gastos(ids_gastos: List[int], ids_amigos: List[int]):
    """Asocia un número aleatorio de amigos a cada gasto."""
    print("\n--- Asociando amigos a gastos... ---")
    if not ids_amigos:
        print("No hay amigos para asociar.")
        return

    for i, gasto_id in enumerate(ids_gastos):
        # Selecciona un número aleatorio de amigos para este gasto (entre 2 y 5)
        max_participantes = min(len(ids_amigos), 5)
        num_participantes = random.randint(2, max_participantes)
        
        # Elige amigos al azar de la lista de IDs
        amigos_a_asociar = random.sample(ids_amigos, k=num_participantes)
        
        print(f"[{i+1}/{len(ids_gastos)}] Asociando {num_participantes} amigos al gasto ID {gasto_id}...")
        
        for amigo_id in amigos_a_asociar:
            try:
                # La API asocia un amigo a un gasto
                url = f"{API_URL}/expenses/{gasto_id}/friends"
                response = requests.post(url, params={"friend_id": amigo_id})
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"  - Error al asociar amigo {amigo_id} a gasto {gasto_id}: {e}")
    print("\nAsociación completada.")


if __name__ == "__main__":
    print("=============================================")
    print("=      Script para Poblar la Base de Datos  =")
    print("=============================================\n")
    
    # Paso 1: Crear amigos
    lista_ids_amigos = crear_amigos(NUM_AMIGOS)
    
    # Paso 2: Crear gastos
    lista_ids_gastos = crear_gastos(NUM_GASTOS)
    
    # Paso 3: Asociar amigos a gastos
    if lista_ids_amigos and lista_ids_gastos:
        asociar_amigos_a_gastos(lista_ids_gastos, lista_ids_amigos)
    else:
        print("\nNo se crearon suficientes datos para realizar asociaciones.")

    print("\n¡Proceso finalizado!")