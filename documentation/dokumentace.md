# 📅 Plánovač

Dialogový systém v českém jazyce pro manipulaci s Google kalendářem postavený na frameworku [Dialmonkey](https://gitlab.com/ufal/dsg/dialmonkey), pro lemmatizaci je použita [MorphoDiTa](https://ufal.mff.cuni.cz/morphodita).

## Instalace

Celou instalaci je doporučeno dělat ve _venv_ nebo něčem podobném. U následujících příkazů je předpokládané spuštění v "root" directory `dialogue-planner`.

První je potřeba nainstalovat všechny využívané moduly, jejichž seznam lze najít v `requirements.txt`. Instalaci jde provést jednoduše pomocí:
```pip install -r requirements.txt```
Poté je potřeba nainstalovat _Dialmonkey_, což je možné pomocí:
```pip install -e .```

## Používání

### Webserver
Nejjednodušším způsobem je spustit Plánovač jako lokální webserver pomocí:
```python webserver/server.py```
Flask vygeneruje `localhost` adresu, ke které je možné přistoupit přes prohlížeč. Na jednoduché stránce pak naleznete instrukce ke komunikaci (je třeba zadávat věty v přirozném jazyce včetně diakritiky) a tlačítko `Start dialogue` k zahájení dialogu. Po stisku tlačítka je nejprve provedena autentizace ke Google účtu (o té více ve [speciální sekci](#autentizace)). Po úspěšné autentizaci je na stránce zpřístupněno pole pro zadání vstupu, který je odeslán stiskem klávesy `Enter`. Následně je vygenerována odpověď systému a spolu se vstupem jsou zobrazeny nad zadávacím polem. Poté je možné v dialogu pokračovat zadáním dalšího vstupu, nebo dialog ukončit stiskem tlačítka `End dialogue`. Pokud uživatel dialog sám neukončí, je dialog ukončen po přibližně 3 minutách neaktivity.
#### Více uživatelů naráz
Webserver umožňuje přístup více uživatelů v jednu chvíli, ovšem požadavky jsou vykonávány sekvenčně. Rozlišení uživatelů je prováděno pomocí `session id`, které prohlížeč posílá spolu s požadavkem. Proto v případě použití z jednoho počítače je potřeba využít _Anonymní režim_ nebo něco podobného, který zajistí jiné `id` než jen nová karta v prohlížeči.
Každý uživatel může být spojen s jiným Google účtem.

### Konzole
Druhým možným způsobem použití je přes konzoli, kde je možné spustit:
```python run_dialmonkey.py --conf conf/planner.yaml```
Po provedení autentizace pak bude dialog probíhat v konzoli, ukončen může být zadáním prázdného vstupu, či klíčového slova `konec`. V obou těchto případech je v adresáři uložena historie dialogu v souboru `history-*.json`. Pokud je běh dialogu ukončen stiskem `Ctrl+C`, historie uložena není.

### Autentizace
Aplikace je v testovacím módu, tedy autentizace je zatím možná jen pro účty specificky uvedené jako testovací. V opačném případě je autentizace hned na začátku zamítnuta.

Pro funkčnost Plánovače je třeba udělit mu oprávnění k manipulaci s Google kalendářem u účtu, který chcete použít. Jakmile toto uděláte při použití přes konzoli, Plánovač si uloží identifikátor do souboru `examples-testing/token.json` a příště již autentizace není nutná. Při použití přes webserver je potřeba provést autentizaci vždy na začátku dialogu, uložení identifikátoru není podporováno.