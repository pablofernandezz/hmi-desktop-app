# Diseño de Software: SplitWithMe

## 1. Patrón Arquitectónico: Model-View-Presenter (MVP)

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

## 2. Diseño Estático (Diagrama de Clases)

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

## 3. Diseño Dinámico (Diagramas de Secuencia)

Estos diagramas ilustran la colaboración entre los objetos para llevar a cabo los casos de uso principales. En esta fase inicial, las operaciones se modelan de forma síncrona.
1️⃣ Añadir un Gasto

Objetivo: Mostrar cómo el usuario ingresa los datos de un gasto, se asignan amigos y se guarda en el servidor.

```mermaid
sequenceDiagram
    actor User
    participant View
    participant Presenter
    participant Model
    participant Server

    User->>View: Clica botón "Añadir Gasto"
    View->>Presenter: on_add_expense_clicked()
    Presenter->>View: show_add_expense_dialog()

    User->>View: Rellena datos y clica "Confirmar"
    View->>Presenter: on_confirm_add_expense()
    activate Presenter
    Presenter->>View: get_expense_form_data()
    View-->>Presenter: devuelve datos del formulario
    Presenter->>View: show_loading(True)

    Presenter->>Model: add_expense(data)
    activate Model
    Model->>Server: POST /expenses (data)
    activate Server

    alt Petición Exitosa
        Server-->>Model: 201 Created (new_expense)
        Model-->>Presenter: on_add_success(new_expense)
        
        Note right of Presenter: Se recargan los gastos para refrescar la lista.
        Presenter->>Model: get_expenses()
        Model->>Server: GET /expenses
        Server-->>Model: 200 OK (updated_list)
        Model-->>Presenter: on_expenses_reloaded(updated_list)
        
        Presenter->>View: update_expense_list(updated_list)
        Presenter->>View: close_add_expense_dialog()

    else Error del Servidor
        Server-->>Model: 4xx/5xx Error (error_details)
        Model-->>Presenter: on_add_error(error_details)
        Presenter->>View: show_error_dialog("Error: No se pudo añadir el gasto.")
    end
    deactivate Server
    deactivate Model

    Presenter->>View: show_loading(False)
    deactivate Presenter
```
