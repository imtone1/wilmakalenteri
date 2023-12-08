<!-- Write documentation on how to Create .venv environment in python -->
<!-- Write documentation on how to install dependencies -->
<!-- Write documentation on how to run the project -->

# 

# Wilma kalenteriin

## Kuvaus

Wilma kalenteriin on python sovellus, joka hakee Wilmasta kotitehtävät ja lisää ne käyttäjän valitsemaan Google kalenteriin.

### Tausta 

Halusin luoda sovelluksen, jolla voisin helposti lisätä Wilman kotitehtävät Google kalenteriin. Tämä helpottaa lasten kotitehtävien seuraamista. 

## Asennus

Suosittelen luoda virtuaaliympäristön tätä sovellusta varten. Virtuaaliympäristön luominen onnistuu seuraavalla komennolla:

Asenna virtuaaliympäristö moduuli
```bash
pip install virtualenv
```

Navigoi projektin juureen ja luo virtuaaliympäristö komennolla

```bash
python3 -m venv .venv
```
tai 

```bash
python -m venv .venv
```

Aktivoi virtuaaliympäristö komennolla

Windows
```bash
.venv\Scripts\activate
```
Linux tai Mac tietokoneissa
```bash
source .venv/bin/activate
```
## Riippuvuudet

Asenna tarvittavat kirjastot komennolla
    
```bash
pip install -r requirements.txt
```

Asenna lisäksi Playwright selain ajuri komennolla. Lisätietoa Playwrightista löytyy [täältä](https://playwright.dev/python/docs/intro)

```bash
playwright install
```

Lisäksi tarvitset tätä sovellusta varten Google Calendar API:n. Tarkat ohjeet löytyvät Googlen omilta sivuilta [Python quickstart](https://developers.google.com/calendar/api/quickstart/python)

Tietokantana on SQLite3. Lisätietoa SQLite3:sta löytyy [täältä](https://docs.python.org/3/library/sqlite3.html)

## Käyttö

Muuta tiedostossa configfile.py olevat muuttujat haluamiksesi ja nimeä tiedosto config.py tiedostoksi.

