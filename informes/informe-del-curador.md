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


  - **Utilidad y aplicación a la práctica:** Nos ayuda a comprender la base teórica del patrón que estamos implementando en nuestro código (`model.py`, `view.py`, `presenter.py`), asegurando que la separación de responsabilidades sea la correcta y que la vista permanezca totalmente independiente del modelo.





- **2. Documentación oficial PyGObject:**


  - **Descripción:** Es la referencia principal y la guía oficial para desarrollar aplicaciones con GTK 4 y Python. Contiene tutoriales, ejemplos de código y una API de referencia completa para todos los widgets y clases.


  - **Utilidad y aplicación a la práctica:** Es la guía de consulta fundamental para resolver cualquier duda sobre cómo crear un widget (`Gtk.ListBox`), organizarlo en la ventana o, crucialmente, cómo conectar una acción del usuario (una "señal") a una función en el presentador para implementar la programación dirigida por eventos.





- **3. Aplicación de demostración GTK 4 Python Demo:**


  - **Descripción:** Es una aplicación incluida con la librería que muestra de forma interactiva casi todos los widgets de GTK 4, presentando su código fuente correspondiente en Python.


  - **Utilidad y aplicación a la práctica:** Permite explorar visualmente los componentes disponibles, lo que nos ayuda a elegir los widgets más adecuados para nuestro diseño de interfaz y a ver ejemplos de implementación que podemos adaptar a nuestro proyecto.





- **4. Tutorial de la librería `requests` para Python (de "Real Python"):**


  - **Descripción:** Un tutorial detallado que explica cómo realizar peticiones HTTP (GET, POST, PUT, DELETE) con esta librería, incluyendo el manejo de errores y datos en formato JSON.


  - **Utilidad y aplicación a la práctica:** Es clave para implementar correctamente toda la comunicación entre nuestro `model.py` y el servidor. Nos enseña a obtener, crear, modificar y eliminar datos de forma remota, que es una de las funcionalidades centrales de nuestra aplicación.





- **5. Documentación y editor online Mermaid:**


  - **Descripción:** La página oficial de Mermaid, que contiene toda la sintaxis necesaria para crear diagramas UML (clases, secuencia, etc.) a partir de texto simple, e incluye un editor para visualizarlos en tiempo real.


  - **Utilidad y aplicación a la práctica:** Es la herramienta que usamos para crear los diagramas de clases y de secuencia requeridos en el fichero `diseño_sw.md`. Permite documentar la arquitectura de software de forma clara y profesional directamente en el formato Markdown que se nos exige.





- **6. Asistentes de IA:**


  - **Descripción:** Modelos de lenguaje a los que se puede acceder mediante una interfaz de chat. Capaces de comprender y generar lenguaje natural, código y dar explicaciones sobre una amplia variedad de conceptos técnicos.


  - **Utilidad y aplicación a la práctica:** Actúa como herramienta de apoyo a la hora de resolver dudas puntuales, que no se pueden solucionar rápidamente con la documentación oficial.
