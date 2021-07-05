# 📅 Plánovač

Dialogový systém v českém jazyce pro manipulaci s Google kalendářem postavený na frameworku [Dialmonkey](https://gitlab.com/ufal/dsg/dialmonkey), pro lemmatizaci je použita [MorphoDiTa](https://ufal.mff.cuni.cz/morphodita).

## Obsah
- [📅 Plánovač](#-plánovač)
  - [Obsah](#obsah)
  - [Instalace](#instalace)
  - [Používání](#používání)
    - [Dialog](#dialog)
    - [Webserver](#webserver)
      - [Více uživatelů naráz](#více-uživatelů-naráz)
    - [Konzole](#konzole)
    - [Autentizace](#autentizace)
  - [Vývoj](#vývoj)
    - [Konfigurace](#konfigurace)
    - [Řízení dialogu](#řízení-dialogu)
    - [Komponenty](#komponenty)
      - [NLU](#nlu)

## Instalace

Celou instalaci je doporučeno dělat ve _venv_ nebo něčem podobném. U následujících příkazů je předpokládané spuštění v "root" directory `dialogue-planner`.

První je potřeba nainstalovat všechny využívané moduly, jejichž seznam lze najít v `requirements.txt`. Instalaci jde provést jednoduše pomocí:

```pip install -r requirements.txt```

Poté je potřeba nainstalovat _Dialmonkey_, což je možné pomocí:

```pip install -e .```

## Používání

### Dialog
Pro komunikaci se systémem je třeba využívat češtiny včetně diakritiky. Na velikosti písmen nezáleží. Příklady zadání: _„co mám v plánu zítra?“, „kdy mám v plánu státnice?“, „změnit na 25.6.2022“, „smazat“, „přidat kadeřnictví, 5.6.2021 od 13 do 17 hodin“_

### Webserver
Nejjednodušším způsobem je spustit Plánovač jako lokální webserver pomocí:

```python webserver/server.py```

_Flask_ vygeneruje `localhost` adresu, ke které je možné přistoupit přes prohlížeč. Na jednoduché stránce pak naleznete instrukce ke komunikaci a tlačítko `Start dialogue` k zahájení dialogu. Po stisku tlačítka je nejprve provedena autentizace ke Google účtu (o té více ve [speciální sekci](#autentizace)). Po úspěšné autentizaci je na stránce zpřístupněno pole pro zadávání vstupu, který je odeslán stiskem klávesy `Enter`. Následně je vygenerována odpověď systému a spolu se vstupem jsou zobrazeny nad zadávacím polem. Poté je možné v dialogu pokračovat zadáním dalšího vstupu, nebo dialog ukončit stiskem tlačítka `End dialogue`. Pokud uživatel dialog sám neukončí, je dialog ukončen po přibližně 3 minutách neaktivity.
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

## Vývoj

Jak již bylo zmíněno, celý systém je postaven na frameworku _Dialmonkey_.

### Konfigurace

Konfigurace je uložena v sobouru ve složce `conf`. Vždy musí obsahovat seznam komponent, které budou použity, a slova rozpoznávaná jako konec dialogu. Volitelně může obsahovat také úroveň loggingu či input/output kanály, tyto ale mohou být přepsány při spuštění.

Plánovač používá při běhu v konzoli konfiguraci `conf/planner.yaml`, při běhu jako webserver pak `conf/planner_server.yaml`.

### Řízení dialogu

O řízení dialogu se stará instance třídy `ConversationHandler`, která bere jako parametr konfigurační soubor. Tato instance při inicializaci zajistí vytvoření všech komponent dle konfigurace.

Vlastní dialog je pak uložen v instanci třídy `Dialogue`. Na začátku je do ní uložen uživatelův vstup. Následně je tato instance posupně předávána všem nakonfigurovaným komponentám, každá komponenta si obvykle něco vyplněného předchozími a vrátí instanci upravenou o svůj výstup.

### Komponenty

Plánovač používá kompenty NLU (_natural language understanding_ - extrakce významu z přirozeného jazyka), DST (_dialogue state tracking_ - sledování toho, co uživatel zmínil již dřív, případně úprava), DP (_dialogue policy_ - provedení úkonů a vygenerování významu toho, co má být sděleno uživateli) a NLG (_natural language generation_ - vytvoření vět v přirozeném jazyce z významu vygenerovaného DP).

#### NLU

NLU vezme vstup uživatele a pomocí série funkcí se z něj pokusí dostat význam související s tématem, kde každá funkce se specializuje na extrakci konkrétní části - jedna se snaží zjistit, jestli uživatel zmínil něco o datu, jiná jestli zmínil něco o času, jiná o co se uživatel celkově snaží.

Každá funkce používá sérii `if-else` větví, které se obvykle snaží pomocí _regulárních výrazů_ najít něco v uživatelově vstupu - například pokud ve vstupu je "v [číslo]", pravděpodobně se jedná o časový údaj.