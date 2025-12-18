# Inventory Management System

A modern, web-based Inventory Management System built with Python (Flask) and SQLite.

## Features

*   **Multi-Tenancy**: Supports multiple independent organizations (tenants), each with its own isolated database and users.
*   **Authentication**: Secure login/logout with role-based access (Admin/Employee).
*   **Dashboard**: Real-time overview of total products, low stock alerts, and recent movements.
*   **Product Management**: Add, edit, delete, and search products.
*   **Stock Control**: Record stock entries and exits with reasons.
*   **Provider Management**: Manage supplier information.
*   **User Management**: Admin interface to manage system users.
*   **Audit Logs**: Complete history of user actions.
*   **Reports**: Export inventory data to CSV and PDF.

## Installation

1.  **Clone the repository** or extract the source code.
2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    # source venv/bin/activate  # Linux/Mac
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Setup & Usage

### 1. Generate Access Codes (Tenants)
Before running the application, you must generate the initial tenants (databases). Each tenant has a unique **Access Code**.

Run the setup script:
```bash
python inventory_system/create_initial_tenants.py
```
This will:
*   Create a `tenants/` directory.
*   Generate 10 independent SQLite databases.
*   Create a `tenants.json` mapping codes to databases.
*   **Display a list of Access Codes** in the terminal. **SAVE THESE CODES!**

### 2. Run the Application
```bash
python run.py
```
Open your browser and go to `http://127.0.0.1:5000`.

### 3. Login
To log in, you need:
*   **Username**: `admin`
*   **Password**: `password`
*   **Access Code**: One of the codes generated in Step 1 (e.g., `A1B2C3D4`).

*Note: You can manage tenants (delete them) using `python inventory_system/manage_tenants.py`.*

## Project Structure

*   `/app`: Application logic and blueprints.
*   `/auth`: Authentication routes.
*   `/db`: Database models.
*   `/ui`: HTML templates and static files.
*   `/tests`: Automated tests.
*   `config.py`: Configuration.
*   `run.py`: Entry point.

## Testing
To run the automated tests:
```bash
pytest
```
