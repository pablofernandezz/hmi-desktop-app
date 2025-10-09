# Diseño de Software: SplitWithMe

## **1. Patrón Arquitectónico: Model-View-Presenter (MVP)**

Para esta aplicación hemos optado por el patrón **Model-View-Presenter (MVP)**. Lo elegimos porque nos permite separar la lógica de la aplicación de la interfaz de usuario, lo que hace que las interfaces sean más simples y el código mucho más fácil de mantener.

### Justificación de la elección del patrón MVP

1. **Separación de responsabilidades**: MVP divide la aplicación en tres capas:
    * La **Vista** se encarga solo de mostrar datos y capturar las acciones del usuario. No toma decisiones ni maneja lógica del programa, así que está totalmente desacoplada del modelo.
    * El **Modelo** gestiona toda la información y se comunica con el servidor. No sabe nada de cómo se muestran los datos en pantalla.
    * El **Presentador** hace de intermediario: recibe las acciones de la Vista, solicita datos al Modelo y luego actualiza la Vista. Así, Vista y Modelo no dependen directamente entre sí.

2. **Se adapta a nuestro entorno**:
    * **Python**: el patrón encaja muy bien con la programación orientada a objetos que usamos.
    * **GTK 4**: perfecto para librerías de GUI basadas en eventos. La Vista emite señales que el Presentador captura y procesa.
    * **Facilidad para pruebas**: como la lógica está separada en Presentador y Modelo, podemos hacer tests unitarios fácilmente sin tener que abrir la interfaz gráfica.

### Qué hace cada componente

* **Modelo (`model.py`)**: Se encarga de las llamadas a la API, convierte los datos en objetos de Python y maneja toda la lógica de acceso a datos.
* **Vista (`view.py`)**: Construye la interfaz con GTK 4, muestra los datos que recibe del Presentador y le avisa cuando el usuario hace algo (por ejemplo, clic en un botón).
* **Presentador (`presenter.py`)**: Recibe las acciones de la Vista, pide los datos al Modelo, los procesa si hace falta y luego actualiza la Vista.

---

## **2. Diseño Estático (Diagrama de Clases)**

El siguiente diagrama UML muestra las clases principales de la aplicación y cómo se relacionan entre sí dentro de la arquitectura MVP.

```mermaid
---
config:
  layout: elk
---
classDiagram
    class View {
        <<GTK Widget>>
        - presenter: Presenter
        + set_presenter(p)
        + build_ui()
        + show_expenses(expenses: list)
        + show_friends(friends: list)
        + show_loading(is_visible: bool)
        + show_error_dialog(message: string)
        + get_expense_form_data(): dict
        + connect_signals()
    }
    class Presenter {
        - model: Model
        - view: View
        + __init__(model, view)
        + start()
        + on_add_expense_clicked()
        + on_confirm_add_expense()
        + on_delete_expense_clicked()
        + on_assign_friend_to_expense(expense_id: int, friend_id: int)
    }
    class Model {
        - api_url: string
        + get_expenses() : list[Expense]
        + get_friends() : list[Friend]
        + add_expense(data: dict) : Expense
        + delete_expense(expense_id: int) : bool
        + assign_friend_to_expense(expense_id: int, friend_id: int)
    }
    class Expense {
        + id: int
        + description: string
        + amount: float
        + friends: list[Friend]
    }
    class Friend {
        + id: int
        + name: string
        + expenses: list[Expense]
    }
    Presenter "1" o-- "1" Model : uses
    Presenter "1" o-- "1" View : controls
    View ..> Presenter : signals
    Model ..> Expense : creates
    Model ..> Friend : creates
    Expense "0..*" -- "0..*" Friend : involved

```
---

## **3. Diseño Dinámico (Diagramas de Secuencia)**

Estos diagramas ilustran la colaboración entre los objetos para llevar a cabo los casos de uso principales.

### **3.1 Añadir un Gasto Nuevo**

Objetivo: Mostrar cómo el usuario ingresa los datos de un gasto, se asignan amigos y se guarda.

```mermaid
sequenceDiagram
    actor User
    participant View
    participant Presenter
    participant Model

    User->>View: Clica botón "Añadir Gasto"
    View->>Presenter: on_add_expense_clicked()
    
    Presenter->>Model: get_friends()
    activate Model
    Model-->>Presenter: devuelve lista_de_amigos
    deactivate Model
    
    Presenter->>View: show_add_expense_dialog(lista_de_amigos)
    activate View
    View-->>User: Muestra diálogo para añadir gasto
    deactivate View
    
    User->>View: Rellena datos y clica "Confirmar"
    View->>Presenter: on_confirm_add_expense()
    
    Presenter->>View: get_expense_dialog_data()
    activate View
    View-->>Presenter: devuelve datos_del_gasto
    deactivate View
    
    Presenter->>View: show_loading(True)
    
    Presenter->>Model: add_expense(datos_del_gasto)
    activate Model
    Model-->>Presenter: devuelve resultado_operacion
    deactivate Model
    
    Presenter->>Model: get_expenses()
    activate Model
    Model-->>Presenter: devuelve lista_actualizada
    deactivate Model
    
    Presenter->>View: update_expense_list(lista_actualizada)
    Presenter->>View: show_loading(False)
```

### **3.2 Añadir un Gasto Nuevo**

Objetivo: Mostrar cómo el usuario selecciona un gasto y la aplicación muestra su información detallada.

```mermaid
sequenceDiagram
    actor User
    participant View
    participant Presenter
    participant Model

    User->>View: Selecciona un gasto y clica "Ver Detalles"
    View->>Presenter: on_view_details_clicked(gasto_id)

    Presenter->>View: show_loading(True)

    Presenter->>Model: get_expense_details(gasto_id)
    activate Model
    Model-->>Presenter: devuelve detalles_del_gasto
    deactivate Model

    Presenter->>View: show_expense_details_dialog(detalles_del_gasto)
    Presenter->>View: show_loading(False)
```

#### **3.3 Modificar Datos de un Gasto**

**Objetivo:** Mostrar el flujo para editar un gasto existente, desde la selección hasta el guardado de los cambios.

```mermaid
sequenceDiagram
    actor User
    participant View
    participant Presenter
    participant Model

    User->>View: Selecciona un gasto y clica "Modificar"
    View->>Presenter: on_modify_expense_clicked(gasto_id)

    Presenter->>View: show_loading(True)

    Presenter->>Model: get_expense_details(gasto_id)
    activate Model
    Model-->>Presenter: devuelve datos_actuales_gasto
    deactivate Model

    Presenter->>Model: get_friends()
    activate Model
    Model-->>Presenter: devuelve lista_de_amigos
    deactivate Model

    Presenter->>View: show_modify_expense_dialog(datos_actuales_gasto, lista_de_amigos)
    Presenter->>View: show_loading(False)
    
    User->>View: Modifica datos y clica "Confirmar"
    View->>Presenter: on_confirm_modify_expense(gasto_id)

    Presenter->>View: get_expense_dialog_data()
    activate View
    View-->>Presenter: devuelve datos_modificados
    deactivate View

    Presenter->>View: show_loading(True)

    Presenter->>Model: update_expense(gasto_id, datos_modificados)
    activate Model
    Model-->>Presenter: devuelve resultado_operacion
    deactivate Model

    Presenter->>Model: get_expenses()
    activate Model
    Model-->>Presenter: devuelve lista_actualizada
    deactivate Model

    Presenter->>View: update_expense_list(lista_actualizada)
    Presenter->>View: show_loading(False)
```

### **3.4. Eliminar un Gasto**

Objetivo: Mostrar el proceso de eliminación de un gasto, incluyendo el paso de confirmación por parte del usuario.

```mermaid
sequenceDiagram
    actor User
    participant View
    participant Presenter
    participant Model

    User->>View: Selecciona un gasto y clica "Eliminar"
    View->>Presenter: on_delete_expense_clicked(gasto_id)

    Presenter->>View: show_confirm_delete_dialog("¿Estás seguro?")
    
    alt Usuario confirma
        User->>View: Clica "Sí"
        View->>Presenter: on_confirm_delete(gasto_id)

        Presenter->>View: show_loading(True)

        Presenter->>Model: delete_expense(gasto_id)
        activate Model
        Model-->>Presenter: devuelve resultado_operacion
        deactivate Model

        Presenter->>Model: get_expenses()
        activate Model
        Model-->>Presenter: devuelve lista_actualizada
        deactivate Model

        Presenter->>View: update_expense_list(lista_actualizada)
        Presenter->>View: show_loading(False)

    else Usuario cancela
        User->>View: Clica "No"
        Note over View, Presenter: El diálogo se cierra. Fin del caso de uso.
    end
```

### **3.5. Ver Detalles de un Amigo**

Objetivo: Mostrar cómo el usuario selecciona un amigo para ver su información detallada, como su balance y los gastos en los que participa.

```mermaid
sequenceDiagram
    actor User
    participant View
    participant Presenter
    participant Model

    User->>View: Selecciona un amigo de la lista
    View->>Presenter: on_friend_selected(amigo_id)

    Presenter->>View: show_loading(True)

    Presenter->>Model: get_friend_details(amigo_id)
    activate Model
    Note right of Model: Petición a GET /friends/{id}
    Model-->>Presenter: devuelve detalles_del_amigo
    deactivate Model

    Presenter->>Model: get_expenses_for_friend(amigo_id)
    activate Model
    Note right of Model: Petición a GET /friends/{id}/expenses
    Model-->>Presenter: devuelve gastos_del_amigo
    deactivate Model

    Presenter->>View: update_friend_details_panel(detalles_del_amigo, gastos_del_amigo)
    Presenter->>View: show_loading(False)
```
