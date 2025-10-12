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
    direction LR
    class VistaPrincipal {
        <<GTK.ApplicationWindow>>
        - presenter: Presenter
        + set_presenter(p)
        + build_ui()
        + mostrar_gastos(gastos: List[Gasto])
        + mostrar_amigos(amigos: List[Amigo])
        + show_loading(is_loading: bool)
        + show_connection_error(visible: bool)
        + mostrar_dialogo_gasto(amigos, callback, gasto_existente)
        + show_confirm_delete_dialog(gasto_id: bool)
        + connect_signals()
    }
    class DialogoGasto {
        <<Gtk.Dialog>>
        - on_accept_callback: function
        + get_form_data(): dict
    }
    class Presenter {
        - model: Model
        - view: VistaPrincipal
        + __init__(vista, modelo)
        + iniciar()
        + cargar_datos_principales()
        + on_add_gasto_clicked()
        + on_modify_gasto_clicked(gasto_id: int)
        + on_delete_expense_clicked(gasto_id: int)
        + on_confirm_delete(gasto_id: int)
        + on_gasto_row_activated(row)
    }
    class Model {
        - api_url: string
        + get_gastos() : List[Gasto]
        + get_amigos() : List[Amigo]
        + get_gasto_details(gasto_id: int): Gasto
        + create_gasto(datos: dict): bool
        + update_gasto(gasto_id: int, datos: dict): bool
        + delete_gasto(gasto_id: int): bool
        + add_amigo_a_gasto(gasto_id: int, amigo_id: int): bool
        + remove_amigo_de_gasto(gasto_id: int, amigo_id: int): bool
    }
    class Gasto {
        + id: int
        + description: string
        + amount: float
        + date: string
        + friends: List[Amigo]
    }
    class Amigo {
        + id: int
        + name: string
        + credit_balance: float
        + debit_balance: float
        + saldo: float ## property ##
    }
    Presenter "1" o-- "1" Model : uses
    Presenter "1" o-- "1" VistaPrincipal : controls
    VistaPrincipal ..> Presenter : signals
    VistaPrincipal "1" *-- "1" DialogoGasto : creates
    Model ..> Gasto : creates
    Model ..> Amigo : creates
    Gasto "0..*" -- "0..*" Amigo : involved

```
---

## **3. Diseño Dinámico (Diagramas de Secuencia)**

Estos diagramas ilustran la colaboración entre los objetos para llevar a cabo los casos de uso principales.

### **3.1 Añadir un Gasto Nuevo**

Objetivo: Mostrar cómo el usuario ingresa los datos de un gasto, se asignan amigos y se guarda.

```mermaid
sequenceDiagram
    actor User
    participant VistaPrincipal
    participant Presenter
    participant DialogoGasto
    participant Model

    User->>VistaPrincipal: Clica botón "Añadir Gasto"
    VistaPrincipal->>Presenter: on_add_gasto_clicked()
    
    Presenter->>VistaPrincipal: mostrar_dialogo_gasto(amigos=[], on_accept_callback=al_aceptar)    activate Model
    activate VistaPrincipal
    VistaPrincipal->>DialogoGasto: __init__(...)
    VistaPrincipal-->>User: Muestra diálogo para añadir gasto
    deactivate VistaPrincipal
    
    User->>DialogoGasto: Rellena datos y clica "Aceptar"
    DialogoGasto->>Presenter: al_aceptar(datos_gasto) %% Invoca el callback %%

    Presenter->>VistaPrincipal: show_loading(True)
    
    Presenter->>Model: create_gasto(datos_gasto)
    activate Model
    Model-->>Presenter: devuelve True/False
    deactivate Model
    
    Presenter->>Presenter: cargar_datos_principales() %% Recarga todos los datos %%
    
    Note over Presenter, Model: Llama a get_gastos() y get_amigos()
    
    Presenter->>VistaPrincipal: mostrar_gastos(lista_actualizada)
    Presenter->>VistaPrincipal: show_loading(False)
```

### **3.2 Ver Detalles de un Gasto**

Objetivo: Mostrar cómo el usuario selecciona un gasto y la aplicación muestra su información detallada.

```mermaid
sequenceDiagram
    actor User
    participant VistaPrincipal
    participant Presenter
    participant Model

    User->>VistaPrincipal: Activa una fila de la lista de gastos
    VistaPrincipal->>Presenter: on_view_row_activated(row)

    Presenter->>VistaPrincipal: show_loading(True)

    Presenter->>Model: get_gasto_details(gasto_id)
    activate Model
    Model-->>Presenter: devuelve objeto Gasto con amigos
    deactivate Model

    Presenter->>VistaPrincipal: show_gasto_details(gasto)
    Presenter->>VistaPrincipal: show_loading(False)
```

#### **3.3 Modificar Datos de un Gasto**

**Objetivo:** Mostrar el flujo para editar un gasto existente, desde la selección hasta el guardado de los cambios.

```mermaid
sequenceDiagram
    actor User
    participant VistaPrincipal
    participant Presenter
    participant Model

    User->>VistaPrincipal: Clica botón "Modificar" en un gasto
    VistaPrincipal->>Presenter: on_modify_gasto_clicked(gasto_id)

    Presenter->>VistaPrincipal: show_loading(True)

    Presenter->>Model: get_gasto_details(gasto_id)
    activate Model
    Model-->>Presenter: devuelve gasto_actual
    deactivate Model

    Presenter->>Model: get_amigos()
    activate Model
    Model-->>Presenter: devuelve todos_amigos
    deactivate Model

    Presenter->>VistaPrincipal: mostrar_dialogo_gasto(todos_amigos, al_aceptar_modificacion, gasto_actual)
    Presenter->>VistaPrincipal: show_loading(False)
    
    User->>VistaPrincipal: Modifica datos y clica "Aceptar"
    VistaPrincipal->>Presenter: al_aceptar_modificacion(datos_nuevos) %% Invoca el callback %%

    Presenter->>VistaPrincipal: show_loading(True)

    Note over Presenter: Calcula amigos a añadir y a quitar

    loop Para cada amigo a añadir
        Presenter->>Model: add_amigo_a_gasto(gasto_id, amigo_id)
    end
    loop Para cada amigo a quitar
        Presenter->>Model: remove_amigo_de_gasto(gasto_id, amigo_id)
    end

    Presenter->>Model: update_gasto(gasto_id, datos_basicos)
    activate Model
    Model-->>Presenter: devuelve True/False
    deactivate Model

    Presenter->>Presenter: cargar_datos_principales()
    Note over Presenter, VistaPrincipal: Recarga y actualiza toda la vista
```

### **3.4. Eliminar un Gasto**

Objetivo: Mostrar el proceso de eliminación de un gasto, incluyendo el paso de confirmación por parte del usuario.

```mermaid
sequenceDiagram
    actor User
    participant VistaPrincipal
    participant Presenter
    participant Model

    User->>View: Clica botón "Eliminar" de un gasto
    VistaPrincipal->>Presenter: on_delete_gasto_clicked(gasto_id)

    Presenter->>VistaPrincipal: show_confirm_delete_dialog(...)

    alt Usuario confirma
        User->>VistaPrincipal: Clica "Sí"
        VistaPrincipal->>Presenter: on_confirm_delete(gasto_id)

        Presenter->>VistaPrincipal: show_loading(True)

        Presenter->>Model: delete_gasto(gasto_id)
        activate Model
        Model-->>Presenter: devuelve True/False
        deactivate Model

        Presenter->>Presenter: cargar_datos_principales()
        Note over Presenter, VistaPrincipal: Recarga y actualiza toda la vista

    else Usuario cancela
        User->>VistaPrincipal: Clica "No"
        Note over VistaPrincipal, Presenter: El diálogo se cierra. Fin del caso de uso.
    end
```

### **3.5. Ver Detalles de un Amigo**

Objetivo: Mostrar cómo el usuario selecciona un amigo para ver su información detallada, como su balance y los gastos en los que participa.

```mermaid
sequenceDiagram
    actor User
    participant VistaPrincipal
    participant Presenter
    participant Model

    User->>VistaPrincipal: Activa una fila de la lista de amigos
    VistaPrincipal->>Presenter: on_amigo_row_activated(row)

    Presenter->>VistaPrincipal: show_loading(True)

    Presenter->>Model: get_amigo_details(amigo_id)
    activate Model
    Model-->>Presenter: devuelve objeto Amigo
    deactivate Model

    Presenter->>Model: get_gastos_por_amigo(amigo_id)
    activate Model
    Model-->>Presenter: devuelve lista de Gastos
    deactivate Model

    Presenter->>VistaPrincipal: show_amigo_details(amigo, gastos_asociados)
    Presenter->>VistaPrincipal: show_loading(False)
```
