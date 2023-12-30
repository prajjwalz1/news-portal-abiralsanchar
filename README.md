# AbiralSanchar | BACKEND

AbiralSanchar is a NewsPortal Web Application .

## Prerequisites

Make sure you have the following installed:

- python v3.12.1
- pip (Python package installer)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/MrAalu/AbiralSanchar-Backend
    ```

2. Navigate to the project directory:

    ```bash
    cd AbiralSanchar-Backend
    ```

3. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

5. Install project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

7. Populate database with Starter Data for API Testing:

    ```bash
    python manage.py loaddata populateDatabase.json
    ```


