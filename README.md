cat > README.md <<'EOF'
# ✈️ Sistema de Gestión de Aerolínea

Sistema web desarrollado con **Django** para la gestión integral de una aerolínea, como parte del proyecto final integrador de la Tecnicatura Superior en Desarrollo de Software.  
Permite administrar vuelos, pasajeros, reservas y usuarios, con funcionalidades diferenciadas para **administradores** y **clientes**.

---

## 📋 Características

### Para Usuarios (Clientes)
- Registro e inicio de sesión
- Búsqueda de vuelos por origen, destino y fecha
- Reserva de vuelos disponibles
- Consulta del estado de vuelos
- Visualización de historial de reservas
- Edición de datos personales

### Para Administradores
- Panel de control con acceso privado
- Gestión completa de vuelos: crear, editar, eliminar
- Asignación de aviones a vuelos
- Gestión de reservas: listar, cancelar, modificar
- Gestión de usuarios: ver, editar, bloquear
- Reportes y estadísticas
- Configuración de tarifas y promociones

---

## 🛠 Tecnologías utilizadas

- **Backend:** Django (Python)
- **Frontend:** HTML5, CSS3, Bootstrap
- **Base de datos:** SQLite (modo desarrollo) / PostgreSQL (modo producción)
- **Control de versiones:** Git y GitHub

---

## 📦 Requisitos previos

Asegúrate de tener instalado:

- [Python 3.10+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Git](https://git-scm.com/)
- [PostgreSQL](https://www.postgresql.org/) *(opcional si se usa en producción)*

---

##  Instalación y ejecución

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/bianprincipi/aerolinea_antobianca.git
   cd aerolinea_antobianca
   python -m venv .venv
 2) source .venv/bin/activate  # En Linux/Mac
    .venv\Scripts\activate     # En Windows
3) pip install -r requirements.txt
4) python3 manage.py makemigrations
5) python3 manage.py migrate
6) python3 manage.py createsuperuser
7)python3 manage.py runserver


