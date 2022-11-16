# SmoothPoll

## Prepare your enviroment to start coding

### Inizialize virtual enviroment w. Pipenv

Before running any command remember to install eventual new dependencies:
```bash
pipenv install  
```

and activate the virtual environment:

```bash
pipenv shell  
```

### Database migration

Run the following command before start the server, in order to create all the tables in your database:

```bash
python manage.py migrate  
```

### Run the server
To run the server:
```bash
python manage.py runserver  
```

## Quick notes on how to code

This project is based on Django, so all usual Django rules and commands are valid here. Here it follows a quick brief.

-   project is divided into applications. To create a new application you may use command: 
    ```bash
    python manage.py startapp APP_NAME
    ```

    (more info: https://docs.djangoproject.com/en/4.1/intro/tutorial01/)

-   to iterate with database you will use models and migrations. After creating a model, you wanna run this command to create a migration file:

    ```bash
    python manage.py makemigration APP_NAME
    ```

    (more info: https://docs.djangoproject.com/en/4.1/intro/tutorial02/#database-setup)