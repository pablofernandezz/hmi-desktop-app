Informe del Curador-Traductor


> A continuación se ofrece una plantilla del informe que debe


> generar la persona encargada de este role cada semana.



## Objetivos de aprendizaje de la semana 1




  - Concepto, herramienta, ...


- **Concepto:** Patrón Arquitectónico Model-View-Presenter (MVP)


  - **Recursos identificados:**


    - Artículo de Wikipedia sobre el patrón Model-View-Presenter.





- **Concepto:** Programación Dirigida por Eventos


  - **Recursos identificados:**


    - Documentación oficial de PyGObject (específicamente la sección sobre Señales y Callbacks).





- **Herramienta:** Librería Gráfica GTK 4 con Python (PyGObject)


  - **Recursos identificados:**


    - Documentación oficial de PyGObject.


    - Aplicación de demostración GTK 4 Python Demo.





- **Herramienta:** Diseño Software con UML y Mermaid


  - **Recursos identificados:**


    - Documentación y editor online de Mermaid.





- **Herramienta:** Comunicación con Servidor Externo (API REST)


  - **Recursos identificados:**


    - Tutorial de la librería `requests` para Python.





- **Herramienta:** IA Generativa


  - **Recursos identificados:**


    - Asistentes de IA conversacionales (Gemini).




    Recursos indentificados para su estudio.


	


	

## Recursos empleados en la semana 1




  - Descripción del recurso.


  


    Utilidad y aplicación a la práctica.


- **1. Artículo de Wikipedia sobre el patrón Model-View-Presenter:**


  - **Descripción:** Artículo que ofrece una definición clara y concisa del patrón arquitectónico MVP, explicando las responsabilidades de cada componente (Modelo, Vista, Presentador) y cómo se comunican entre ellos.


  - **Aplicación práctica:** Nos ayuda a comprender la base teórica del patrón que estamos implementando en nuestro código (`model.py`, `view.py`, `presenter.py`), asegurando que la separación de responsabilidades sea la correcta y que la vista permanezca totalmente independiente del modelo.





- **2. Documentación oficial PyGObject:**


  - **Descripción:** Es la referencia principal y la guía oficial para desarrollar aplicaciones con GTK 4 y Python. Contiene tutoriales, ejemplos de código y una API de referencia completa para todos los widgets y clases.


  - **Aplicación práctica:** Es la guía de consulta fundamental para resolver cualquier duda sobre cómo crear un widget (`Gtk.ListBox`), organizarlo en la ventana o, crucialmente, cómo conectar una acción del usuario (una "señal") a una función en el presentador para implementar la programación dirigida por eventos.





- **3. Aplicación de demostración GTK 4 Python Demo:**


  - **Descripción:** Es una aplicación incluida con la librería que muestra de forma interactiva casi todos los widgets de GTK 4, presentando su código fuente correspondiente en Python.


  - **Aplicación práctica:** Permite explorar visualmente los componentes disponibles, lo que nos ayuda a elegir los widgets más adecuados para nuestro diseño de interfaz y a ver ejemplos de implementación que podemos adaptar a nuestro proyecto.





- **4. Tutorial de la librería `requests` para Python (de "Real Python"):**


  - **Descripción:** Un tutorial detallado que explica cómo realizar peticiones HTTP (GET, POST, PUT, DELETE) con esta librería, incluyendo el manejo de errores y datos en formato JSON.


  - **Aplicación práctica:** Es clave para implementar correctamente toda la comunicación entre nuestro `model.py` y el servidor. Nos enseña a obtener, crear, modificar y eliminar datos de forma remota, que es una de las funcionalidades centrales de nuestra aplicación.





- **5. Documentación y editor online Mermaid:**


  - **Descripción:** La página oficial de Mermaid, que contiene toda la sintaxis necesaria para crear diagramas UML (clases, secuencia, etc.) a partir de texto simple, e incluye un editor para visualizarlos en tiempo real.


  - **Aplicación práctica:** Es la herramienta que usamos para crear los diagramas de clases y de secuencia requeridos en el fichero `diseño_sw.md`. Permite documentar la arquitectura de software de forma clara y profesional directamente en el formato Markdown que se nos exige.





- **6. Asistentes de IA:**


  - **Descripción:** Modelos de lenguaje a los que se puede acceder mediante una interfaz de chat. Capaces de comprender y generar lenguaje natural, código y dar explicaciones sobre una amplia variedad de conceptos técnicos.


  - **Aplicación práctica:** Actúa como herramienta de apoyo a la hora de resolver dudas puntuales, que no se pueden solucionar rápidamente con la documentación oficial.


## Objetivos de aprendizaje de la semana 2

*   **Concepto:** Asincronía en Interfaces Gráficas (Threading)
    *   **Recursos identificados:**
        *   Tutoriales sobre el módulo `threading` de Python.
        *   Documentación de PyGObject sobre `GLib.idle_add` para la comunicación segura entre hilos.

*   **Concepto:** Diseño de Experiencia de Usuario (UX) Avanzada
    *   **Recursos identificados:**
        *   Guías de Interfaz Humana (HIG) de GNOME.
        *   Artículos sobre patrones de diseño UX para aplicaciones de escritorio.

*   **Herramienta:** Widgets Avanzados de GTK 4 (Gtk.Revealer, Gtk.Stack, Gtk.Overlay)
    *   **Recursos identificados:**
        *   Documentación oficial de PyGObject para los widgets `Gtk.Stack`, `Gtk.Revealer` y `Gtk.Overlay`.
        *   Ejemplos de implementación de vistas dinámicas y superposiciones.

*   **Herramienta:** Diálogos Modales Complejos y Gestión de Formularios
    *   **Recursos identificados:**
        *   Documentación de `Gtk.Dialog` para la creación de diálogos personalizados.
        *   Tutoriales sobre la gestión de eventos y validación de datos en diálogos de GTK 4.

## Recursos empleados en la semana 2

*   **1. Documentación de PyGObject sobre Threading y GLib.idle_add:**
    *   **Descripción:** Sección específica de la documentación que explica cómo ejecutar operaciones de larga duración (como peticiones de red) en un hilo separado para no bloquear la interfaz gráfica. Detalla el uso de `GLib.idle_add` como el mecanismo fundamental para enviar los resultados de vuelta al hilo principal de forma segura y actualizar la UI.
    *   **Aplicación práctica:** Ha sido el recurso más crítico de la semana. Nos ha permitido implementar la carga de datos de forma asíncrona. Cada vez que se necesita obtener información del servidor, se lanza un hilo (`threading.Thread`) que realiza la llamada a la API y, una vez obtenidos los datos, usa `GLib.idle_add` para pasarle la información a una función que se encarga de actualizar los `Gtk.ListBox` en la vista. Esto ha solucionado completamente el problema de que la aplicación se "congelara" mientras esperaba una respuesta del servidor.

*   **2. Guía de Interfaz Humana (HIG) de GNOME:**
    *   **Descripción:** Documento que establece los principios de diseño y las convenciones para crear aplicaciones que se sientan nativas y coherentes en el ecosistema GNOME/GTK. Ofrece pautas sobre el uso de widgets, la disposición, la retroalimentación al usuario y la gestión de errores.
    *   **Aplicación práctica:** La hemos consultado para tomar decisiones de diseño de UX. Basándonos en sus recomendaciones, hemos implementado el `Gtk.Overlay` con un `Gtk.Spinner` para dar feedback visual durante las cargas asíncronas, y un `Gtk.Stack` para cambiar a una vista de error de conexión con un botón de "Reintentar", mejorando drásticamente la experiencia de usuario. También se ha aplicado para estilizar botones de acciones destructivas (`.destructive-action`).

*   **3. Documentación de Widgets Avanzados de GTK 4 (Gtk.Revealer, Gtk.Stack):**
    *   **Descripción:** Páginas de la documentación oficial que describen el funcionamiento de contenedores dinámicos como `Gtk.Stack` (para gestionar múltiples vistas en un mismo espacio) y `Gtk.Revealer` (para mostrar u ocultar widgets con una animación).
    *   **Aplicación práctica:** `Gtk.Revealer` ha sido clave para crear las filas de gastos y amigos expandibles. Al hacer clic en "detalles", el `Gtk.Revealer` muestra de forma animada un nuevo panel con información adicional, sin tener que abrir una ventana nueva. `Gtk.Stack` se ha usado como el contenedor principal de la ventana para poder cambiar entre la vista de contenido y la pantalla de error de conexión.

*   **4. Tutoriales sobre la creación de Diálogos Personalizados (Gtk.Dialog):**
    *   **Descripción:** Ejemplos y guías que explican cómo heredar de la clase `Gtk.Dialog` para construir ventanas modales a medida, con formularios, validación de entradas y lógica de respuesta personalizada.
    *   **Aplicación práctica:** Nos ha permitido crear `DialogoGasto` y `DialogoAporte`. Estos diálogos contienen múltiples widgets (`Gtk.Entry`, `Gtk.SpinButton`, `Gtk.CheckButton`), realizan validaciones básicas (ej. que la descripción no esté vacía) y comunican los datos introducidos de vuelta al presentador mediante callbacks para su procesamiento.


*   **5. Asistentes de IA:**
    *   **Descripción:** Herramientas de IA conversacional utilizadas para consultas específicas y depuración.
    *   **Aplicación práctica:** Ha sido un apoyo fundamental para entender la interacción entre `threading` y `GLib.idle_add`, proporcionando ejemplos de esqueleto que luego adaptamos. También se usó para resolver dudas concretas sobre cómo deshabilitar un `Gtk.CheckButton` (`.set_sensitive(False)`) o añadirle un `tooltip` para mejorar la UX en la ventana de edición de gastos.
