# Informe del Facilitador-Administrador

  > A continuación se ofrece un informe con todos los avances del desarrollo del proyecto esta primera semana.


##  Registro de tareas llevadas a cabo durante la semana 1

  #### **Tarea 1: Diseño de la Interfaz y Casos de Uso**

  ***Descripción de la tarea:** Pusimos en común los trabajos individuals de los miembros del equipo para crear un diseño de interfaz de usuario (UI) coherente y aceptado por los tres miembros.
  Definimos los casos de uso principales de la aplicación, centrandonos exclusivamente en la gestión de gastos, tal y como indicaba el enunciado.
  El resultado de esta fase se plasmó en el documento `diseño-iu`, que incluye wireframes, flujos de navegación y la descripción formal de los casos de uso.
  ***Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
  ***Estado de completud:** **100% Completado**.
  ***Conflictos, desviaciones, etc.:** La principal desviación fue la necesidad de eliminar todas las funcionalidades de gestión de amigos (Añadir, Modificar, Eliminar), ajustando el diseño para que esta sección fuera de solo lectura, de acuerdo a los requisitos de la práctica.

---

#### **Tarea 2: Selección y Diseño de la Arquitectura Software**

*   **Descripción de la tarea:** Seleccionamos el patrón arquitectónico **Model-View-Presenter (MVP)** por su separación de responsabilidades y su adecuación al entorno de desarrollo (Python + GTK). SRealizamos el diseño software, creando un diagrama de clases para la parte estática y diagramas de secuencia para la dinámica. Todo el diseño está documentado en el fichero `diseño_sw.md` utilizando el lenguaje Mermaid para los diagramas UML.
*   **Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** No se presentaron conflictos. La elección del patrón fue directa, siguiendo las recomendaciones y el material de ejemplo proporcionado en la asignatura.

---

#### **Tarea 3: Implementación, Conexión y Depuración**

*   **Descripción de la tarea:** Implementamos la estructura base de la aplicación siguiendo el patrón MVP, se estableció la conexión con el servidor proporcionado y se desarrollaron las funcionalidades completas de **CRUD** (Crear, Leer, Actualizar, Eliminar) para los gastos. En esto también se incluye la  lógica para asociar y desasociar amigos a un gasto existente.
*   **Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** Durante esta fase surgieron varios desafíos que resolvimos con éxito:
    *   **Desajustes con la API:** Detectamos y corrregimos diferencias entre las clases del modelo de datos y el JSON devuelto por la API (en los nombres de los atributos: `description` vs `descripcion`, `amount` vs `importe`).
    *   **Depuración de Endpoints:** Descubrimos que la API esperaba los parámetros para añadir amigos a un gasto (`friend_id`) como parámetros de consulta (`params`) en la URL, en lugar de en el cuerpo (`json`) de la petición `POST`. Ajustamos el modelo para solucionar errores.
    *   **Lógica de Sincronización:** La implementación de la lógica para actualizar la lista de amigos en un gasto (calculando las diferencias entre la lista original y la nueva) requirió una atención especial en el Presentador.

---

#### **Tarea 4: Mejoras de UI/UX y Manejo de Errores**

*   **Descripción de la tarea:** Pulimos la experiencia de usuario reemplazando los botones de "Detalles" por la activación directa de filas en las listas.
Añadimos la identidad visual de la aplicación (logo) y, fundamentalmente, se implementó un sistema de manejo de errores de conexión que muestra una pantalla específica si el servidor no está disponible, con opción de reintentar establecer conexión.
*   **Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** Encontramos un bug de layout con `Gtk.Overlay` que provocaba que los botones no fueran clickables. Este bug se resolvió corrigiendo la jerarquía de los widgets en la vista para que el contenido principal no se solapara con otros elementos.

---

## Estado del repositorio en la semama 1
Al cierre de la semana 1, el repositorio se encuentra en un estado estable y contiene todos los artefactos requeridos en la Tarea 1.

*   **Estructura de Ficheros Relevante:**
    ```
    .
    ├── assets/
    │   └── images/
    │       ├── logo.png
    │       └── wifi-off.png
    ├── src/
    │   ├── main.py
    │   ├── model.py
    │   ├── presenter.py
    │   └── view.py
    ├── diseño-iu.pdf
    └── diseño_sw.md
    ```

*   **Artefactos Entregados:**
    1.  **`diseño-iu.pdf`**: Contiene el diseño completo de la interfaz y los casos de uso.
    2.  **`diseño_sw.md`**: Contiene el diseño software basado en MVP con diagramas UML en Mermaid.
    3.  **Código Fuente (`/src`)**: Implementación completa y funcional de la Tarea 1.

*   **Funcionalidad Implementada y Verificada:**
    *   Arquitectura MVP con separación de responsabilidades.
    *   Comunicación con el servidor para todas las operaciones.
    *   CRUD completo para la clase "Gastos".
    *   Gestión de la asociación de amigos a gastos.
    *   Visualización de detalles de gastos y amigos.
    *   Manejo de errores de conexión con interfaz dedicada.
    *   Interfaz de usuario pulida con logo y elementos de UX mejorados.
