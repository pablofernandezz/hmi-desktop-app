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

*   **Resumen de Funcionalidades Implementadas:**
    *   Arquitectura MVP con separación de responsabilidades.
    *   Comunicación con el servidor para todas las operaciones.
    *   CRUD completo para la clase "Gastos".
    *   Gestión de la asociación de amigos a gastos.
    *   Visualización de detalles de gastos y amigos.
    *   Manejo de errores de conexión con interfaz dedicada.
    *   Interfaz de usuario pulida con logo y elementos de UX mejorados.


---

## Registro de tareas llevadas a cabo durante la semana 2

---

#### **Tarea 5: Correcciones de la Tarea 1 (Feedback)**

*   **Descripción de la tarea:** Solucionamos todos los errores de la entrega de la primera tarea. Los cambios principales incluyen:
    1.  **Refactorización de la UI:** Eliminamos el exceso de diálogos para mostrar detalles y hacer una modificación. En su lugar, implementamos un sistema de `Gtk.Revealer` que permite desplegar la información "in-place" tanto para gastos como para amigos, mejorando la experiencia de usuario.
    2.  **Mejora del Flujo de Creación de Gastos:** Modificamos el proceso para que el usuario pueda asignar amigos **durante** la creación del gasto. Aunque la API requiere dos pasos, la lógica se encapsuló en una sola función, en la que se crea el gasto y se asignan los amigos que participan en él, todo ello sin que el usuario lo tenga que hacer por separado,esto hace el proceso sencillo e intuitivo.
    3.  **Revisión Arquitectónica:** Se corrigió el punto de entrada de la aplicación (`main.py`) para seguir el patrón de inyección de dependencias, para hacer que la Vista y el Presentador se creen y conecten en el `main`.
    4.  **Ajustes de Diseño:** Reubicamos el botón de añadir gasto, se eliminó el logo del cuerpo principal de la aplicación, que movimos al diálogo "Acerca de", y también ocultamos los IDs internos al usuario final.
*   **Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** El principal desafío fue refactorizar la Vista para usar `Gtk.Revealer`, que implicó crear clases de fila personalizadas (`GastoRow`, `AmigoRow`) y adaptar toda la lógica del Presentador para interactuar con estas nuevas clases en lugar de con diálogos globales.

---

#### **Tarea 6: Implementación de la Funcionalidad de Aportes**

*   **Descripción de la tarea:** Implementamos desde cero la funcionalidad completa para que un amigo pueda realizar un aporte a un gasto (que faltaba de la primera tarea). Esto incluye:
    1.  **Interfaz de Aportes:** Creamos de un diálogo (`DialogoAporte`) que permite seleccionar un amigo participante y una cantidad a pagar, con validación para no superar la deuda de ese amigo en ese gasto.
    2.  **Lógica de Negocio:** Añadimos los métodos necesarios al Modelo para comunicarse con los endpoints de la API correspondientes (`PUT /expenses/{id}/friends/{id}`).
    3.  **Gestión de Deuda Saldada:** Implementamos la lógica en el Presentador para que, depués de un aporte exitoso, se compruebe si la deuda del amigo ha llegado a cero y, en ese caso, no le deje hacer más aportaciones.
*   **Asignación de responsables:** Pablo Fernández Martí.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** Tuvimos varios problemas con un bug en el que la vista de detalles no se actualizaba correctamente después de un aporte. Lo solucionamos implementando un patrón de refresco en el Presentador, que recarga los datos y fuerza el redibujado de la vista de detalles con la información actualizada del servidor.

---

#### **Tarea 7: Gestión de la Concurrencia (Tarea 2)**

*   **Descripción de la tarea:** Identificamos todas las operaciones de red como bloqueantes y se refactorizó el **Presentador** para ejecutar todas las llamadas al Modelo en hilos de ejecución secundarios (`threading`). Garantiando que la interfaz gráfica nunca se congele, incluso durante peticiones lentas al servidor y dando feedback al usuario y que sepa así que se está ejecutando algo.
*   **Asignación de responsables:** Nicolás Domínguez Souto.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** El reto fue asegurarnos de que todas las actualizaciones de la UI se realizaran de forma segura en el hilo principal de GTK. Lo conseguimos con `GLib.idle_add()` para programar las funciones de actualización de la vista después de que el hilo de trabajo completara la operación de red. Se actualizó el `diseño_sw.md` con un diagrama de secuencia que refleja este comportamiento concurrente.

---

#### **Tarea 8: Gestión de Errores de E/S (Tarea 2)**

*   **Descripción de la tarea:** Extendimos el manejo de errores de conexión a **todas** las operaciones que interactúan con el servidor. Ahora, si cualquier petición (añadir, modificar, eliminar, aportar, ver detalles) falla, la aplicación muestra la pantalla de error con la opción de "Reintentar", proporcionando una  mejor experiencia de usuario.
*   **Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** No se presentaron conflictos significativos, ya que la base (la pantalla de error y la lógica de detección en el Modelo) la habíamos implementado ya en la Tarea 1. Solo tuvimos que aplicar el  patrón de forma sistemática en todos los métodos del Presentador.

---

## Estado del repositorio en la semana 2

Al cierre de la semana 2, el repositorio ha sido actualizado para cumplir con todos los requisitos de la Tarea 2 y las correcciones de la Tarea 1. La aplicación es ahora concurrente, robusta ante errores de red y ofrece una experiencia de usuario mejorada.

*   **Principales Cambios en el Código:**
    *   **`view.py`:** Refactorización masiva, ahora usamos `Gtk.HeaderBar`, `Gtk.Revealer` y clases de fila personalizadas (`GastoRow`, `AmigoRow`). Mejoramos el diseño y la usabilidad general.
    *   **`presenter.py`:** Refactorización completa para implementar la concurrencia en todas las operaciones de red mediante `threading` y `GLib.idle_add`. Mejoramos el manejo de errores y la lógica de refresco de la UI.
    *   **`model.py`:** Añadimos el método `make_payment_for_friend` creamos la clase `AmigoEnGasto` para manejar los datos de deuda en cada gasto de forma más precisa.
    *   **`main.py`:** Corregido para seguir un patrón de inyección de dependencias.

*   **Artefactos Actualizados:**
    *   **`diseño_sw.md`**: Actualizamos los diagramas de secuencia para reflejar el uso de hilos en las operaciones concurrentes.

*   **Resumen de Funcionalidades Implementadas:**
    *   Todas las operaciones de red se ejecutan en hilos separados, evitando el bloqueo de la UI.
    *   El spinner de carga se muestra durante todas las operaciones de E/S.
    *   La gestión de errores de conexión es global para toda la aplicación.
    *   La UI utiliza `Gtk.Revealer` para una experiencia más fluida y sin diálogos emergentes para detalles/edición.
    *   La creación de gastos permite asignar amigos en un solo paso para el usuario.
    *   La funcionalidad de realizar aportes está completamente implementada.
    *   La arquitectura de la aplicación ha sido corregida y mejorada.


---

## Registro de tareas llevadas a cabo durante la semana 3

---

#### **Tarea 9: Internacionalización de Cadenas de Texto (i18n)**

*   **Descripción de la tarea:** Preparamos la aplicación para soportar diferentes idiomas. Utilizamos la librería `gettext` de Python para marcar todos los textos visibles para el usuario en el fichero `view.py`. Creamos una función de ayuda `_()` para simplificar el marcado de textos. Además, configuramos el fichero `main.py` para inicializar `gettext`, definiendo el dominio de la aplicación (`splitwithme`) y la ubicación del directorio `locale`.
*   **Asignación de responsables:** Pablo Fernández Martí.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** Tuvimos un problema al generar los archivos `.po`, no se registraban todos los textos correctamente, con la ayuda de la IA Deepseek anlizó todo el código de view.py y nos dió las cadena de texto que no habían sido generadas automáticamnete, ahorrándonos mucho trabajo manual.

---

#### **Tarea 10: Localización a Gallego e Inglés (l10n)**

*   **Descripción de la tarea:** Para validar la internacionalización, localizamos la aplicación a dos nuevos idiomas: Gallego (gl_ES) e Inglés (en_GB). Utilizamos las herramientas (`xgettext`, `msginit`, `msgfmt`) para crear la estructura de directorios `locale`, generar los ficheros de plantilla (`.pot`), inicializar los catálogos de mensajes (`.po`) y compilarlos a su formato binario (`.mo`). Finalmente realizamos las traducciones correspondientes en cada fichero `.po`.
*   **Asignación de responsables:** Traducción al Gallego: Nicolás Domínguez Souto, Traducción al Inglés: Joel Ramos Carro.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** No se presentaron conflictos.

---

#### **Tarea 11: Internacionalización de Formatos (Moneda y Fechas)**

*   **Descripción de la tarea:** Utilizamos la librería `locale` de Python para que la aplicación mostrara las divisas y las fechas en el formato correspondiente a la configuración regional del usuario. Configuramos `locale.setlocale(locale.LC_ALL, '')` en `main.py` para que la aplicación adopte la configuración del sistema. Creamos las funciones de ayuda en `view.py` (`format_currency`, `format_date`) para encapsular esta lógica y aplicarla de forma consistente en toda la interfaz.
*   **Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** No se presentaron conflictos.

---

#### **Tarea 12: Actualización de Documentación**

*   **Descripción de la tarea:** También tuvimos que actualizar la documentación del proyecto para reflejar todos los cambios implementados durante la tarea. Esto incluyó la actualización de los wireframes en el `diseño-iu.pdf` para mostrar la nueva interfaz con `Gtk.Revealer` y la actualización de los diagramas de secuencia en `diseño_sw.md` para reducir el número de diagramas.
*   **Asignación de responsables:** Tarea conjunta del equipo de desarrollo.
*   **Estado de completud:** **100% Completado**.
*   **Conflictos, desviaciones, etc.:** Tarea realizada en paralelo sin conflictos.

---

## Estado del repositorio en la semana 3

Al cierre de la semana 3, el repositorio contiene la versión final de la aplicación, cumpliendo con todos los requisitos de las tres tareas de la práctica.

*   **Principales Cambios en el Código:**
    *   **`main.py`:** Añadimos la configuración inicial de `gettext` y `locale`.
    *   **`view.py`:** Todas las cadenas de texto fueron marcadas para traducción con `_()`. Todas las fechas y cantidades monetarias se formatean usando las funciones `format_date` y `format_currency`.
    *   **Nueva Estructura de Directorios:** Creamos el directorio `locale` con los ficheros `.pot`, `.po` y `.mo` para los idiomas `es`, `gl` y `en`.

*   **Artefactos Finales:**
    *   **Código Fuente (`/src`)**: Versión final, concurrente y completamente internacionalizada.
    *   **Traducciones (`/locale`)**: Catálogos de mensajes para castellano, gallego e inglés.
    *   **Documentación (`diseño-iu.pdf`, `diseño_sw.md`)**: Actualizada para reflejar el estado final de la aplicación.

*   **Resumen de Funcionalidades Finales:**
    *   La aplicación se muestra en el idioma del sistema (castellano, gallego o inglés).
    *   Las fechas y monedas se formatean según la configuración regional del sistema.
    *   Se mantienen todas las funcionalidades de las tareas anteriores, como la concurrencia y el manejo de errores.
    *   La experiencia de usuario ha sido mejorada gracias a la refactorización de la interfaz.