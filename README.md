<!-- Write documentation on how to Create .venv environment in python -->
<!-- Write documentation on how to install dependencies -->
<!-- Write documentation on how to run the project -->

# 

# Wilma kalenteriin

## Kuvaus

Wilma kalenteriin on python sovellus, joka hakee Wilman kalenterista kotitehtävät ja lisää ne käyttäjän valitsemaan kalenteriin.


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

Asenna lisäksi Playwright selain ajuri komennolla

```bash
playwright install
```

Lisäksi tarvitset tätä sovellusta varten Google Calendar API:n. Tarkat ohjeet löytyvät Googlen omilta sivuilta [Python quickstart](https://developers.google.com/calendar/api/quickstart/python)

## Käyttö

Muuta tiedostossa configfile.py olevat muuttujat haluamiksesi ja nimeä tiedosto config.py tiedostoksi.

