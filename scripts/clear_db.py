# scripts/clear_db.py

import requests

# --- Configuración ---
API_URL = "http://127.0.0.1:8000"
# ---------------------

def limpiar_gastos():
    """Obtiene todos los gastos y los elimina uno por uno."""
    print("--- Limpiando gastos... ---")
    try:
        response = requests.get(f"{API_URL}/expenses")
        response.raise_for_status()
        gastos = response.json()
        
        if not gastos:
            print("No hay gastos que limpiar.")
            return

        for gasto in gastos:
            gasto_id = gasto['id']
            try:
                del_response = requests.delete(f"{API_URL}/expenses/{gasto_id}")
                del_response.raise_for_status()
                print(f"Gasto ID {gasto_id} eliminado.")
            except requests.exceptions.RequestException as e:
                print(f"Error al eliminar gasto ID {gasto_id}: {e}")
        print("Limpieza de gastos completada.")
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la lista de gastos: {e}")

def limpiar_amigos():
    """Obtiene todos los amigos y los elimina uno por uno."""
    print("\n--- Limpiando amigos... ---")
    try:
        response = requests.get(f"{API_URL}/friends")
        response.raise_for_status()
        amigos = response.json()

        if not amigos:
            print("No hay amigos que limpiar.")
            return

        for amigo in amigos:
            amigo_id = amigo['id']
            try:
                del_response = requests.delete(f"{API_URL}/friends/{amigo_id}")
                del_response.raise_for_status()
                print(f"Amigo ID {amigo_id} eliminado.")
            except requests.exceptions.RequestException as e:
                print(f"Error al eliminar amigo ID {amigo_id}: {e}")
        print("Limpieza de amigos completada.")
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la lista de amigos: {e}")


if __name__ == "__main__":
    print("=============================================")
    print("=    Script para Limpiar la Base de Datos   =")
    print("=============================================\n")
    
    confirmacion = input("¿Estás seguro de que quieres borrar TODOS los gastos y amigos? (s/N): ")
    
    if confirmacion.lower() == 's':
        # Es importante borrar los gastos primero, por si existen relaciones
        # o restricciones de clave externa en la base de datos.
        limpiar_gastos()
        limpiar_amigos()
        print("\n¡Limpieza finalizada!")
    else:
        print("\nOperación cancelada.")