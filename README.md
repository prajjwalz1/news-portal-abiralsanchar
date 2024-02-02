# AbiralSanchar | BACKEND

AbiralSanchar is a NewsPortal Web Application .

## Authentication Documentation 
1. We use CustomMiddleware 'JWTMiddleware' to Refresh the Access Token and Set the new Access Token in Cookie, We dont do anything on middleware if the user is Guest i.e. no access/refresh token is in request body
2. We have 2 Decorators :
'access_token_required' validates if the user is logged in or not with valid JWT
'staff_admin_required' validates if the requesting user is Staff/SuperUser or not , if its normal user then, ACCESS DENIED!
3. Only Staff/SuperUser can use SignUp view to create new Users ()
4. Only logged-in user who has valid token can do CRUD operations on model.

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


