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

## BeautifulSoup

Tiedosto beautifulsoup.py käyttää BeautifulSoup kirjastoa Wilman sivujen parsimiseen. Lisätietoa BeautifulSoupista löytyy [täältä](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

Sen käyttö saattaa vaatia Wilma sivuston tarkempaa tutkimista.

## Kehittäjätyökalut (Developer Tools)

Navigoi Wilma sivustolle ja avaa kehittäjätyökalut joko painamalla F12 tai oikealla hiiren näppäimellä ja valitse "Inspect". 

Navigoi kehittäjätyökaluissa "Network" välilehdelle. Täppää "Preserve log" ja yritä kirjautua (pelkkä "Kirjaudu sisään" ilman tunnuksia riittää).

Nyt kehittäjätyökaluissa pitäisi näkyä login POST pyyntö. Etsi login pyyntö. Headers välilehdeltä löytyy tarvitsemanne payload tiedot. Nämä ovat otsikomme.

![Headers](./data/kuvat/network_tab.JPG)

Lisäksi tarvitsemme session cookien. Nämä löytyvät "Cookies" välilehdeltä tai samalta paikasta, josta löysimme payload tiedot "Headers" välilehdeltä. Tarkista Set-Cookie cookien nimi.

![Cookies](./data/kuvat/setcookie.JPG)




