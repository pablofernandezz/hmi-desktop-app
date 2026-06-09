# 💸 SplitWithMe - Cliente de Escritorio (HMI)

![Estado del proyecto](https://img.shields.io/badge/Estado-Completado-success)
![Contexto Académico](https://img.shields.io/badge/Contexto-UDC_FIC-blue)
![Asignatura](https://img.shields.io/badge/Asignatura-IPM-orange)

Aplicación de escritorio desarrollada para la gestión y división de gastos compartidos, permitiendo a los usuarios registrar deudas y liquidar balances de forma intuitiva.

Este repositorio contiene exclusivamente el **Cliente de Escritorio**. Puedes consultar la versión web de este mismo sistema en el siguiente enlace:
👉 **[SplitWithMe - Cliente Web](https://github.com/pablofernandezz/hmi-web-app)**

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python
* **Interfaz Gráfica:** GTK 4
* **Comunicación:** Peticiones HTTP a API RESTful

## 🏗️ Arquitectura del Sistema

Este proyecto sigue una arquitectura cliente-servidor. Este repositorio actúa como cliente de escritorio y consume los servicios de una API externa. La API maneja toda la lógica de negocio (usuarios, grupos, balances), mientras que este cliente se enfoca en proporcionar una experiencia de usuario fluida y nativa en el sistema operativo.

## ⚙️ Instalación y Despliegue Local

Para ejecutar este proyecto en tu máquina local, es **necesario** tener la API backend en funcionamiento primero.

### 1. Levantar la API Backend (Dependencia Externa)
La API requerida es `splitwithme` y debe ejecutarse localmente:
1. Clona el repositorio de la API: 
   `git clone https://github.com/nbarreira/splitwithme`
2. Sigue las instrucciones del `README.md` de ese repositorio para arrancar el servidor local.

### 2. Ejecutar el Cliente de Escritorio
Con la API respondiendo en local, puedes levantar la interfaz gráfica:

1. Clona este repositorio:
```bash
   git clone [https://github.com/pablofernandezz/hmi-desktop-app.git](https://github.com/pablofernandezz/hmi-desktop-app.git)
   cd hmi-desktop-app
```
2. Instala las dependencias necesarias:
```bash
   pip install -r requirements.txt
```
3. Ejecuta la aplicación principal:
```bash
   python main.py
```
🎓 Contexto Académico y Equipo

Este proyecto fue desarrollado de forma colaborativa como parte de la asignatura de Interacción Persona-Máquina (IPM) en la Facultade de Informática da Coruña (FIC - UDC). El objetivo principal fue aplicar los principios de usabilidad, diseño de interfaces y experiencia de usuario.

Desarrollado por:

    Pablo Fernández Martí LinkedIn: www.linkedin.com/in/pablo-fernandez-marti-526320415

    Joel Ramos Carro

    Nicolás Domínguez Souto
