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


## Objetivos de aprendizaje de la semana 3

*   **Concepto:** Internacionalización (i18n) y Localización (l10n)
    *   **Recursos identificados:**
        *   Documentación oficial de Python sobre el módulo `gettext`.
        *   Documentación oficial de Python sobre el módulo `locale`.

*   **Herramienta:** GNU gettext (herramientas de línea de comandos)
    *   **Recursos identificados:**
        *   Tutoriales sobre los comandos `msgfmt` (para compilar traducciones).
        *   Archivos de traducción (`.po`, `.mo`).

*   **Concepto:** Formateo de datos dependiente de la localización
    *   **Recursos identificados:**
        *   Documentación sobre las directivas de formateo de fechas de Python (`strftime`).
        *   Guías sobre el uso de `locale.currency` para la representación de valores monetarios.

## Recursos empleados en la semana 3

*   **1. Documentación del módulo `gettext` de Python:**
    *   **Descripción:** Es la documentación oficial que explica el framework estándar de Python para la internacionalización. Detalla cómo marcar cadenas de texto para su traducción, cómo configurar el "dominio" de la aplicación y cómo cargar los catálogos de mensajes compilados.
    *   **Aplicación práctica:** Ha sido el pilar de la tarea. Siguiendo esta guía, hemos modificado el `main.py` para inicializar el sistema `gettext`, definiendo el dominio (`APP_NAME = "splitwithme"`) y el directorio de traducciones (`LOCALE_DIR`). Crucialmente, hemos importado el alias `_ = gettext.gettext` en `view.py` y hemos envuelto todas las cadenas de texto visibles para el usuario (etiquetas, títulos de botones, mensajes de error) con la función `_()`, como en `_("Realizar Aporte")`, para que puedan ser traducidas.

*   **2. Documentación del módulo `locale` de Python:**
    *   **Descripción:** Recurso que explica cómo interactuar con la base de datos de localización del sistema operativo. Permite adaptar el formato de números, fechas, monedas y otros valores a las convenciones del país o región del usuario.
    *   **Aplicación práctica:** Lo hemos utilizado para dos fines principales. Primero, en `main.py`, la llamada a `locale.setlocale(locale.LC_ALL, '')` configura la aplicación para que utilice la configuración regional del sistema. Segundo, en `view.py`, hemos creado dos funciones de ayuda: `format_currency`, que usa `locale.currency()` para mostrar los importes con el símbolo y separadores correctos, y `format_date`, que usa `strftime("%x")` para mostrar las fechas en el formato local estándar (ej. DD/MM/AAAA).

*   **3. Archivos de traducción (`.po`, `.mo`) y la herramienta `msgfmt`:**
    *   **Descripción:** Los archivos `.po` son ficheros de texto plano legibles por humanos donde se escriben las traducciones. La herramienta `msgfmt` es un programa de línea de comandos que compila estos archivos `.po` en archivos binarios optimizados `.mo`, que son los que la aplicación utiliza en tiempo de ejecución.
    *   **Aplicación práctica:** Hemos creado la estructura de directorios `locale/gl_ES/LC_MESSAGES/`. Dentro, hemos editado el archivo `splitwithme.po` para añadir las traducciones al gallego. El paso final y fundamental ha sido usar el comando `msgfmt` en la terminal para compilar el `.po` y generar el archivo `splitwithme.mo`, permitiendo que la aplicación cargara nuestras traducciones al ejecutarse con el `locale` gallego.

*   **4. Asistentes de IA:**
    *   **Descripción:** Herramientas de IA conversacional utilizadas para consultas sobre la configuración del sistema y la depuración de errores específicos.
    *   **Aplicación práctica:** Han sido un recurso clave para solucionar el error `locale.Error: unsupported locale setting`. El asistente nos guio para entender que el problema no estaba en el código, sino en que el `locale` `gl_ES.UTF-8` no estaba generado en el sistema operativo de la máquina virtual. Nos proporcionó los comandos exactos (`sudo nano /etc/locale.gen` y `sudo locale-gen`) para solucionar el problema, lo que fue indispensable para poder probar la funcionalidad de internacionalización.
