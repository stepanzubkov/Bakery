# Bakery - website on flask

This is a site for an American bakery. To simplify my work as a developer, I took a ready-made frontend. You can familiarize yourself with the functionality. The site is under construction

## Run app

For this website i use docker and you can simply run this app in one line

```bash
docker-compose up -d --build
```

The container will run in background (option -d) and you can easy run different commands, like 'bash' or 'ls', with 'docker-compose exec'

## Migrations

For editing DB tables on python, i use migrations with flask-migrate. You can easy create your own DB's versions.

Use this command to get the cli in the container:

```bash
docker-compose exec -w /app app bash
```

Then, type into the terminal this command:

```bash
flask db migrate -m "My migration message"
```

And, you can upgrade db:

```bash
flask db upgrate
```

### Good luck :)
