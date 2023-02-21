# SmoothPoll

## Prepare your enviroment to start coding

### Inizialize virtual enviroment w/ Pipenv

Before running any command remember to install eventual new dependencies:
```bash
pipenv install  
```

and activate the virtual environment:

```bash
pipenv shell  
```

### Initialize .env file

Copy ```.env.example``` file and rename it into ```.env```. Here you will add eventual enviroment configurations.

### Database migration

To run this application you need a database. It can be a PostgreSQL or an SQLite:

- if you want an SQLite, set $USE_POSTGRESQL=False$ in your ENV file
- if you want PostgreSQL instead, 
  - install it somewhere or connect to an existent (through settings in ENV file, see ```.env.example```)
  - ensure user has permission to CREATEDB
  - if it is a local one, ensure it is running (<code>sudo service postgresql start</code>)
- if you just switched between the two, ensure you have runned (in ```python manage.py shell```) commands:

      from django.contrib.contenttypes.models import ContentType

      ContentType.objects.all().delete()


Run the following command before start the server, in order to create all the tables in your database:

```bash
python manage.py migrate  
```

### Site ID and Google initialization

TODO: add a brief procedure

### Run the server
To run the server:
```bash
python manage.py runserver  
```
## Command Line Interface(CLI)
To see all available CLIs run:
```bash
python manage.py --help 
```
### General CLI usage
```bash
python manage.py [cli_command]
```
#### Custom CLI commands
- poll_seeder
## Quick notes on how to code

This project is based on Django, so all usual Django rules and commands are valid here. Here it follows a quick brief.

-   project is divided into applications. To create a new application you may use command: 
    ```bash
    python manage.py startapp APP_NAME
    ```

    (more info: https://docs.djangoproject.com/en/4.1/intro/tutorial01/)

-   to iterate with database you will use models and migrations. After creating a model, you wanna run this command to create a migration file:

    ```bash
    python manage.py makemigrations APP_NAME
    ```

    (more info: https://docs.djangoproject.com/en/4.1/intro/tutorial02/#database-setup)

-   if you quickly need to run some code on a running application:

    ```bash
    python manage.py shell
    ```

    then you can call services, models code, etc.
    (https://docs.djangoproject.com/en/4.1/intro/tutorial02/#playing-with-the-api)

    For example, this sequence of commands will make you create a dummy survey:
    -   import service:
        ```
        from apps.polls_management.services.poll_service import PollService
        ```
    -   use service to create dummy survey
        ```
        PollService.create("sondaggio di prova", "che sondaggio facciamo?", [{"key": "risposta-1", "value": "Risposta 1"}, {"key": "risposta-2", "value": "Risposta 2"}])
        ```
## Semantic versioning
To create a new version use the `bump2version` command. The version system follow the [Semantic Versioning 2.0.0](https://semver.org/#semantic-versioning-200) guidelines.

According to Semantic Versioning 2.0.0 the type of version increment can be:
1. `major` : version when you make incompatible API changes
1. `minor` : version when you add functionality in a backwards compatible manner
1. `patch` : version when you make backwards compatible bug fixes

### Example
```bash
bump2version minor
```

## Code documentation
If you have updated or if you only want to see the documentation in locale, run:
```bash
mkdocs serve
```


## Admin panel

To use admin panel you have to create a super-user. You can do it through command:

```bash
python manage.py createsuperuser --username NAME --email EMAIL
```

System will make you set your password.

