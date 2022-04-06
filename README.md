# Bakery - website on flask

This is a site for an American bakery. You can familiarize yourself with the functionality. The site is under construction

## Run app

For this website i use docker and you can simply run this app in one line

```bash
docker-compose up -d --build
```

The container will run in background (option -d) and you can easy run different commands, like 'bash' or 'ls', with 'docker-compose exec'

If you want insert into db test data, you must run this command:

```bash
docker-compose exec -w /app app 'python test_data.py'
```

## Migrations

For editing DB tables on python, i use migrations with flask-migrate. You can easy create your own DB's versions.

Use this command to get the cli in the container:

```bash
docker-compose exec -w /app app sh
```

And, you can upgrade db:

```bash
flask db upgrate
```

If you want to create your own migration, you must edit db models and run this command in the container:

```bash
flask db migrate -m "My migration message"
```

### Good luck :)
