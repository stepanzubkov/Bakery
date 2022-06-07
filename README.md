# Bakery - website on flask

This is a site for an American bakery. You can familiarize yourself with the functionality.

## Run app

For this website i use docker and you can simply run this app in one line

```bash
docker-compose up -d --build
```

The container will run in background (option -d) and you can easy run different commands, like 'bash' or 'ls', with 'docker-compose exec'

If you want insert into db test data, you must run this command:

```bash
docker-compose exec -w /app app sh
```

Then, type:

```bash
flask db upgrade
python test_data.py
```

Blog page will show youtube videos from channel only when you spicify the access token.
You should create file 'youtube_token.txt' and place youtube access key into this file.
See https://console.cloud.google.com/ to do this.

## Migrations

For editing DB tables on python, i use migrations with flask-migrate. You can easy create your own DB's versions.

Use this command to get the cli in the container:

```bash
docker-compose exec -w /app app sh
```

And, you can upgrade db:

```bash
flask db upgrade
```

If you want to create your own migration, you must edit db models and run this command in the container:

```bash
flask db migrate -m "My migration message"
```

## Tests

For tests, you should run the app.
Then, go to the tests folder and run tests with following commands:

```bash
cd tests
pytest
```

Run single test, for example:

```bash
pytest api/test_products.py

```

## Contribution

If you want to contribute, please write me (contacts in bio)

### Good luck :)
