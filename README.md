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

Remember to configure the same database name and database user on the `settings.yaml` file.

## Running the project
First, you will need to activate Poetry's virtual environment, and then install all the dependencies with Poetry:
> \> poetry shell  
> \> poetry install

After that, create a new superuser using Django's management system:
> \> python manage.py createsuperuser

You'll need at least this first admin user to start all other API resources.

The `pypoetry.toml` file sets up some aliases using [Taskipy](pypi.org/project/taskipy).

to run all tests, use the command:
> \> task test

After ensuring everything works, you can run the API using:
> \> task run