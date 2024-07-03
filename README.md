# TREE EVERYWHERE
### A database of trees planted by volunteers around the world.

This is a Django API project that registers trees planted by the users.

## Requirements

In order to run this API you will need:

1. [Python 3.12](www.python.org/downloads)
2. [PostgreSQL 16](www.postgresql.org/download)
3. [Poetry](python-poetry.org/docs/#installation)
4. Configure environment files:
   1. `.env`
   2. `settings.yaml`
   3. `.secrets.yaml`

### Environment configuration
The environment variables are handled by [Dynaconf](www.dynaconf.com).  
The settings that need configuring are given by comments in the file.  

### Database
A PostgreSQL database is needed as well. You can create one by going into your PostgreSQL instance and running the command:
> postgres# CREATE DATABASE *database_name* WITH OWNER *database_user*;

Set your user to being able to create databases in order for the Django testing suite be able to create the testing environment database: 
> postgres# ALTER USER *database_user* CREATEDB;

Remember to configure the same database name and database user on the `settings.yaml` file, and the same password on the `.secrets.yaml` file.

## Running the project
First, you will need to activate Poetry's virtual environment, and then install all the dependencies with Poetry:
> \> poetry shell  
> \> poetry install

After that, run the database migrations and create a new superuser using Django's management system:
> \> python manage.py migrate  
> \> python manage.py createsuperuser

You'll need at least this first admin user to start all other API resources.

Collect the standard static files from Django/Django Rest Framework by running the command:
> \> python manage.py collectstatic

The `pypoetry.toml` file sets up some aliases using [Taskipy](pypi.org/project/taskipy).

To run all tests, use the command:
> \> task test

After ensuring everything works, you can run the API using:
> \> task run