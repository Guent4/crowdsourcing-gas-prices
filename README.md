# crowdsourcing gas prices

### Backend
install PostgresSQL, create db called `backend`

add `localsettings.py` with db info to `/backend/backend`

`python manage.py runserver`

visit `localhost:8000`

### Edge

1.  Make sure you have Python 2.7.*.
1.  Install postgres
    1.  `sudo apt-get update` then `sudo apt-get install postgresql postgresql-contrib`
    1.  To start postgres: `sudo service postgresql start`
    1.  To log into postgres: `sudo -i -u postgres` followed by `psql`
    1.  Set the password: `\password postgres`
    1.  Create a database named `edge` via: `CREATE DATABASE edge;`.  Verify that it was created by `\l`
    1.  Use `\c edge` to connect to the database and use `\dt` to display the tables      
1.  Install Django
    1.  `pip install django`
    1.  `pip install psycopg2-binary`
1.  Create the Django project (this only needed to be done the first time)
    1.  Start the project by running: `django-admin startproject edge edge/`
    1.  To verify that everything was created correctly run: `python manage.py runserver`
    1.  Create the app via: `python manage.py startapp app`
    1.  Create `local_settings.py` file from the template, `local_settings.txt` 
1.  Migrate the database
    1.  `python manage.py makemigrations`
    2.  `python manage.py migrate`

### Client