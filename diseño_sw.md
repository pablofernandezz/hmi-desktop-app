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
        + mostrar_gastos(gastos: List[Gasto])
        + mostrar_amigos(amigos: List[Amigo])
        + show_loading(is_loading: bool)
        + show_connection_error(visible: bool)
        + mostrar_dialogo_gasto(amigos, on_accept)
        + mostrar_dialogo_aporte(amigos, on_accept)
        + show_confirm_delete_dialog(gasto_id: bool)
        + connect_signals()
    }

    class DialogoGasto {
        <<Gtk.Dialog>>
        - on_accept: function
    }

    class GastoRow {
        <<Gtk.ListBoxRow>>
        - gasto: Gasto
        - presenter: Presenter
        + show_details_view(gasto_con_detalles: Gasto)
        + update_edit_view(gasto: Gasto, amigos: List[Amigo])
    }

    class AmigoRow {
        <<Gtk.ListBoxRow>>
        - amigo: Amigo
        - presenter: Presenter
        + show_details_view(amigo: Amigo, gastos: List[Gasto])
    }

    class DialogoAporte {
        <<Gtk.Dialog>>
        - on_accept: function
    }

    class Presenter {
        - model: Model
        - view: VistaPrincipal
        + iniciar()
        + cargar_datos_principales()
        + on_add_gasto_clicked()
        + _on_accept_new_gasto(datos: dict)
        + on_gasto_row_activated(listbox, row)
        + on_details_gasto_clicked(gasto_id: int, row)
        + on_modify_gasto_clicked(gasto_id: int, row)
        + on_save_changes_clicked(gasto, new_desc, new_amount, amigos_status)
        + on_delete_gasto_clicked(gasto_id: int)
        + on_confirm_delete(gasto_id: int)
        + on_amigo_row_activated(listbox, row)
        + on_details_amigo_clicked(amigo_id: int, row)
        + on_open_aporte_dialog_clicked(gasto: Gasto)
        + on_make_payment_clicked(gasto_id, amigo_id, amount)
    }

    class Model {
        - api_url: string
        + get_gastos() : List[Gasto]
        + get_amigos() : List[Amigo]
        + get_gasto_details(gasto_id: int): Gasto
        + get_amigo_details(id: int): Amigo
        + get_gastos_por_amigo(id: int): List[Gasto]
        + get_amigos_por_gasto(id: int): List[AmigoEnGasto]
        + create_gasto_with_friends(datos: dict): bool
        + update_gasto(id: int, datos: dict): bool
        + delete_gasto(id: int): bool
        + add_amigo_a_gasto(gasto_id: int, amigo_id: int): bool
        + remove_amigo_de_gasto(gasto_id: int, amigo_id: int): bool
        + make_payment_for_friend(gasto_id, amigo_id, amount): bool
    }

    class Gasto {
        + id: int
        + description: string
        + amount: float
        + date: string
        + credit_balance: float
        + friends: List[AmigoenGasto]
    }
    class Amigo {
        + id: int
        + name: string
        + credit_balance: float
        + debit_balance: float
        + saldo: float ## property ##
    }
    class AmigoEnGasto {
        + id: int
        + name: string
        + credit_balance: float
        + debit_balance: float
    }

    Presenter "1" o-- "1" Model : uses
    Presenter "1" o-- "1" VistaPrincipal : controls
    VistaPrincipal ..> Presenter : signals
    VistaPrincipal "1" *-- "n" GastoRow : contains
    VistaPrincipal "1" *-- "n" AmigoRow : contains
    VistaPrincipal "1" *-- "1" DialogoGasto : creates
    VistaPrincipal "1" *-- "1" DialogoAporte : creates
    GastoRow ..> Presenter : signals
    AmigoRow ..> Presenter : signals
    Model ..> Gasto : creates
    Model ..> Amigo : creates
    Model ..> AmigoEnGasto : creates
    Gasto "1" *-- "0..*" AmigoEnGasto : contains

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
    
    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Presenter->>Model: get_amigos()
        activate Model
        Model-->>Presenter: devuelve lista de amigos
        deactivate Model
        
        Presenter->>VistaPrincipal: GLib.idle_add(ui_update, amigos)
    and Main Thread (UI)
        Presenter->>VistaPrincipal: show_loading(True)
        VistaPrincipal->>DialogoGasto: __init__(...)
        DialogoGasto-->>User: Muestra diálogo
        User->>DialogoGasto: Rellena datos y clica "Aceptar"
        DialogoGasto->>Presenter: _on_accept_new_gasto(datos_gasto)
    end

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Presenter->>Model: create_gasto_with_friends(datos_gasto)
        activate Model
        Model-->>Presenter: devuelve True/False
        deactivate Model
        
        Presenter->>Presenter: GLib.idle_add(ui_update, success)
    and Main Thread (UI)
        Presenter->>VistaPrincipal: show_loading(True)
        Note over Presenter, VistaPrincipal: Si success es True, se recargan los datos.
    
        Presenter->>Presenter: cargar_datos_principales()
    end
    
```

### **3.2 Ver Detalles de un Gasto**

Objetivo: Mostrar cómo el usuario selecciona un gasto y la aplicación muestra su información detallada.

```mermaid
sequenceDiagram
    actor User
    participant GastoRow
    participant Presenter
    participant Model

    User->>GastoRow: Activa una fila de la lista de gastos
    GastoRow->>Presenter: on_gasto_row_activated(listbox, self)
    Note over Presenter: El presentador llama a on_details_gasto_clicked(gasto_id, row)

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Presenter->>Model: get_gasto_details(gasto_id)
        activate Model
        Model-->>Presenter: devuelve Gasto con amigos
        deactivate Model
        
        Presenter->>GastoRow: GLib.idle_add(ui_update, gasto_con_detalles)
    and Main Thread (UI)
        Presenter->>GastoRow: show_loading(True)
        Presenter->>GastoRow: show_gasto_details(gasto_con_detalles)
        Presenter->>GastoRow: show_loading(False)
    end
```

### **3.3 Modificar Datos de un Gasto**

**Objetivo:** Mostrar el flujo para editar un gasto existente, desde la selección hasta el guardado de los cambios.

```mermaid
sequenceDiagram
    actor User
    participant GastoRow
    participant Presenter
    participant Model

    User->>GastoRow: Clica botón "Modificar"
    GastoRow->>Presenter: on_modify_gasto_clicked(gasto_id, self)

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Presenter->>Model: get_gasto_details(gasto_id)
        activate Model
        Model-->>Presenter: devuelve gasto_actual
        deactivate Model
        
        Presenter->>Model: get_amigos()
        activate Model
        Model-->>Presenter: devuelve todos_amigos
        deactivate Model
        
        Presenter->>GastoRow: GLib.idle_add(ui_update, gasto_actual, todos_amigos)
    and Main Thread (UI)
        Presenter->>GastoRow: show_loading(True)
        GastoRow->>GastoRow: update_edit_view(gasto, amigos)
        GastoRow-->>User: Muestra formulario de edición en la fila
        GastoRow->>GastoRow: show_loading(False)
    end
    
    User->>GastoRow: Modifica datos y clica "Guardar"
    GastoRow->>Presenter: on_save_changes_clicked(datos_nuevos)

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Note over Presenter: Calcula amigos a añadir/quitar
        loop Para cada amigo a añadir/quitar
            Presenter->>Model: add/remove_amigo_de_gasto(...)
        end
        Presenter->>Model: update_gasto(gasto_id, datos_basicos)
        
        Presenter->>GastoRow: GLib.idle_add(ui_update, success)
    and Main Thread (UI)
        Presenter->>GastoRow: show_loading(True)
        Note over Presenter, GastoRow: Si success es True, se recargan los datos.
        Presenter->>Presenter: cargar_datos_principales()
    end
```

### **3.4. Eliminar un Gasto**

Objetivo: Mostrar el proceso de eliminación de un gasto, incluyendo el paso de confirmación por parte del usuario.

```mermaid
sequenceDiagram
    actor User
    participant VistaPrincipal
    participant GastoRow
    participant Presenter
    participant Model

    User->>GastoRow: Clica botón "Eliminar"
    GastoRow->>Presenter: on_delete_gasto_clicked(gasto_id)

    Presenter->>VistaPrincipal: show_confirm_delete_dialog(...)
    VistaPrincipal-->>User: Muestra diálogo de confirmación

    alt Usuario confirma
        User->>VistaPrincipal: Clica "Sí"
        VistaPrincipal->>Presenter: on_confirm_delete(gasto_id)

        Presenter->>Presenter: _execute_in_thread(worker)
        
        par Worker Thread
            Presenter->>Model: delete_gasto(gasto_id)
            activate Model
            Model-->>Presenter: devuelve True/False
            deactivate Model
            
            Presenter->>VistaPrincipal: GLib.idle_add(ui_update, success)
        and Main Thread (UI)
            Presenter->>VistaPrincipal: show_loading(True)
            Note over Presenter, VistaPrincipal: Si success es True, se recargan los datos.
            Presenter->>Presenter: cargar_datos_principales()
        end

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
    participant AmigoRow
    participant Presenter
    participant Model

    User->>AmigoRow: Activa una fila de la lista de amigos
    AmigoRow->>Presenter: on_amigo_row_activated(listbox, self)
    Note over Presenter: El presentador llama a on_details_amigo_clicked(amigo_id, row)

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Presenter->>Model: get_amigo_details(amigo_id)
        activate Model
        Model-->>Presenter: devuelve objeto Amigo
        deactivate Model

        Presenter->>Model: get_gastos_por_amigo(amigo_id)
        activate Model
        Model-->>Presenter: devuelve lista de Gastos
        deactivate Model
        
        Presenter->>AmigoRow: GLib.idle_add(ui_update, amigo, gastos)
    and Main Thread (UI)
        Presenter->>AmigoRow: show_loading(True)
        AmigoRow->>AmigoRow: show_details_view(amigo, gastos)
        AmigoRow->>AmigoRow: show_loading(False)
    end
```

### **3.6. Amigo Realiza un Aporte (Pago)**

Objetivo: Mostrar cómo el usuario registra un pago o aporte de un amigo para un gasto específico, lo que reduce su deuda

```mermaid
sequenceDiagram
    actor User
    participant VistaPrincipal
    participant GastoRow
    participant Presenter
    participant DialogoAporte
    participant Model

    User->>GastoRow: Clica botón "Añadir Aporte"
    GastoRow->>Presenter: on_open_aporte_dialog_clicked(gasto)

    Presenter->>VistaPrincipal: mostrar_dialogo_aporte(gasto.friends, on_make_payment_clicked)
    activate VistaPrincipal
    VistaPrincipal->>DialogoAporte: __init__(...)
    DialogoAporte-->>User: Muestra diálogo para seleccionar amigo e importe
    deactivate VistaPrincipal

    User->>DialogoAporte: Selecciona amigo, introduce importe y clica "Aceptar"
    DialogoAporte->>Presenter: on_make_payment_clicked(gasto_id, amigo_id, amount)

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Presenter->>Model: make_payment_for_friend(gasto_id, amigo_id, amount)
        activate Model
        Model-->>Presenter: devuelve True/False (success)
        deactivate Model
        
        alt Si el pago fue exitoso y la deuda es cero
            Presenter->>Model: get_amigos_por_gasto(gasto_id)
            Note over Presenter, Model: Verifica si el débito del amigo es < 0.01
            Presenter->>Model: remove_amigo_de_gasto(gasto_id, amigo_id)
        end

        Presenter->>VistaPrincipal: GLib.idle_add(ui_update, success)
    and Main Thread (UI)
        Presenter->>VistaPrincipal: show_loading(True)
        Note over Presenter, VistaPrincipal: Si success es True, se recargan todos los datos.
        Presenter->>Presenter: cargar_datos_principales()
    end
```

### **3.7. Añadir Amigo a un Gasto Existente**

Objetivo: Mostrar cómo el flujo específico para asociar un nuevo amigo a un gasto ya creado.

```mermaid
sequenceDiagram
    actor User
    participant GastoRow
    participant Presenter
    participant Model

    User->>GastoRow: Clica botón "Modificar" en un gasto
    GastoRow->>Presenter: on_modify_gasto_clicked(gasto_id, self)

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Presenter->>Model: get_gasto_details(gasto_id)
        Presenter->>Model: get_amigos()
        Presenter->>GastoRow: GLib.idle_add(ui_update, ...)
    and Main Thread (UI)
        Presenter->>GastoRow: show_loading(True)
        GastoRow->>GastoRow: update_edit_view(gasto, amigos)
        GastoRow-->>User: Muestra formulario de edición con todos los amigos
        GastoRow->>GastoRow: show_loading(False)
    end
    
    User->>GastoRow: Marca el checkbox de un amigo que no estaba seleccionado y clica "Guardar"
    GastoRow->>Presenter: on_save_changes_clicked(...)

    Presenter->>Presenter: _execute_in_thread(worker)
    
    par Worker Thread
        Note over Presenter: Calcula la diferencia de amigos. Identifica el nuevo amigo a añadir.
        Presenter->>Model: add_amigo_a_gasto(gasto_id, nuevo_amigo_id)
        activate Model
        Model-->>Presenter: devuelve True/False
        deactivate Model
        
        Note over Presenter, Model: También podría llamar a update_gasto() si otros datos cambiaron.

        Presenter->>GastoRow: GLib.idle_add(ui_update, success)
    and Main Thread (UI)
        Presenter->>GastoRow: show_loading(True)
        Note over Presenter, GastoRow: Si success es True, se recargan los datos para mostrar al nuevo amigo.
        Presenter->>Presenter: cargar_datos_principales()
    end
```