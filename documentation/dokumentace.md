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
      - [NLU - `dialmonkey/nlu/planner.py`](#nlu---dialmonkeynluplannerpy)
      - [DST - `dialmonkey/dst/rule.py`](#dst---dialmonkeydstrulepy)
      - [DP - `dialmonkey/policy/planner.py`respektive `dialmonkey/policy/planner_server.py`](#dp---dialmonkeypolicyplannerpyrespektive-dialmonkeypolicyplanner_serverpy)
      - [NLG - `dialmonkey/nlg/planner.py`](#nlg---dialmonkeynlgplannerpy)

## Instalace

Celou instalaci je doporučeno dělat ve _venv_ nebo něčem podobném. U následujících příkazů je předpokládané spuštění v "root" directory `dialogue-planner`.

Nejprve je potřeba nainstalovat všechny využívané moduly, jejichž seznam lze najít v `requirements.txt`. Instalaci jde provést jednoduše pomocí:

```pip install -r requirements.txt```

Poté je potřeba nainstalovat _Dialmonkey_, což je možné pomocí:

```pip install -e .```

## Používání

### Dialog
Pro komunikaci se systémem je třeba využívat češtiny včetně diakritiky. Na velikosti písmen nezáleží. Příklady zadání: _„co mám v plánu zítra?“, „kdy mám v plánu státnice?“, „změnit na 25.6.2022“, „smazat“, „přidat kadeřnictví, 5.6.2021 od 13 do 17 hodin“_

### Webserver
Nejjednodušším způsobem je spustit Plánovač jako lokální webserver pomocí:

```python webserver/server.py```

_Flask_ vygeneruje `localhost` adresu, ke které je možné přistoupit přes prohlížeč. Na jednoduché stránce pak naleznete instrukce ke komunikaci a tlačítko `Authenticate` k zahájení komunikace. Po stisku tlačítka je nejprve provedena autentizace ke Google účtu (o té více ve [speciální sekci](#autentizace)). Po úspěšné autentizaci je na stránce zpřístupněno pole pro zadávání vstupu, který je odeslán stiskem klávesy `Enter`. Následně je vygenerována odpověď systému a spolu se vstupem jsou zobrazeny nad zadávacím polem. Poté je možné v dialogu pokračovat zadáním dalšího vstupu, nebo dialog ukončit stiskem tlačítka `End dialogue`. Pokud uživatel dialog sám neukončí, je dialog ukončen po přibližně 3 minutách neaktivity.
#### Více uživatelů naráz
Webserver umožňuje přístup více uživatelů v jednu chvíli, ovšem požadavky jsou vykonávány sekvenčně. Rozlišení uživatelů je prováděno pomocí `session id`, které prohlížeč posílá spolu s požadavkem. Proto v případě použití z jednoho počítače je potřeba využít _Anonymní režim_ nebo něco podobného, který zajistí jiné `id` než jen nová karta v prohlížeči.

Každý uživatel může být spojen s jiným Google účtem.

### Konzole
Druhým možným způsobem použití je přes konzoli, kde je možné spustit:

```python run_dialmonkey.py --conf conf/planner.yaml```

Po provedení autentizace pak bude dialog probíhat v konzoli, ukončen může být zadáním prázdného vstupu, či klíčového slova `konec`. V obou těchto případech je v adresáři uložena historie dialogu v souboru `history-*.json`. Pokud je běh dialogu ukončen stiskem `Ctrl+C`, historie uložena není.

### Autentizace
Aplikace je v testovacím módu, tedy autentizace je zatím možná jen pro účty specificky uvedené jako testovací. V opačném případě je autentizace hned na začátku zamítnuta.

Pro funkčnost Plánovače je třeba udělit mu oprávnění k manipulaci s Google kalendářem u účtu, který chcete použít. Jakmile toto uděláte při použití přes konzoli, Plánovač si uloží identifikátor do souboru `examples-testing/token.json` a příště již autentizace není nutná. 

Při použití přes webserver je potřeba provést autentizaci vždy na začátku dialogu, uložení identifikátoru není podporováno. V tomto případě probíhá tak, 
že je uživateli vygenerován link, který musí otevřít v nové kartě. Po udělení 
všech potřebných oprávnění získá uživatel kód, který musí vložit do vstupního 
pole a potvrdit, čímž je autentizace dokončena.

## Vývoj

Jak již bylo zmíněno, celý systém je postaven na frameworku _[Dialmonkey](https://gitlab.com/ufal/dsg/dialmonkey)_. Základní dokumentaci Dialmonkey lze nalézt v repozitáři frameworku.

### Konfigurace

Konfigurace je uložena v sobouru ve složce `conf`. Vždy musí obsahovat seznam komponent, které budou použity, a slova rozpoznávaná jako konec dialogu. Volitelně může obsahovat také úroveň loggingu či input/output kanály, tyto ale mohou být přepsány při spuštění.

Plánovač používá při běhu v konzoli konfiguraci `conf/planner.yaml`, při běhu jako webserver pak `conf/planner_server.yaml`.

### Řízení dialogu

O řízení dialogu se stará instance třídy `ConversationHandler`, která bere jako parametr konfigurační soubor. Tato instance při inicializaci zajistí vytvoření všech komponent dle konfigurace.

Vlastní dialog je pak uložen v instanci třídy `Dialogue`. Na začátku je do ní uložen uživatelův vstup. Následně je tato instance posupně předávána všem nakonfigurovaným komponentám, každá komponenta si obvykle něco vyplněného předchozími a vrátí instanci upravenou o svůj výstup.

### Komponenty

Plánovač používá kompenty NLU (_natural language understanding_ - extrakce významu z přirozeného jazyka), DST (_dialogue state tracking_ - sledování toho, co uživatel zmínil již dřív, případně úprava), DP (_dialogue policy_ - provedení úkonů a vygenerování významu toho, co má být sděleno uživateli) a NLG (_natural language generation_ - vytvoření vět v přirozeném jazyce z významu vygenerovaného DP). Každá komponenta musí dědit od abstraktní třídy `Component`.

#### NLU - `dialmonkey/nlu/planner.py`

NLU vezme vstup uživatele (který vyplnil `ConversationHandler`) a pomocí série funkcí se z něj pokusí dostat význam související s tématem, kde každá funkce se specializuje na extrakci konkrétní části - jedna se snaží zjistit, jestli uživatel zmínil něco o datu, jiná jestli zmínil něco o času, jiná o co se uživatel celkově snaží.

Každá funkce používá sérii `if-else` větví, které se obvykle snaží pomocí _regulárních výrazů_ najít něco v uživatelově vstupu - například pokud ve vstupu je "v [číslo]", pravděpodobně se jedná o časový údaj.

V případě názvů událostí a míst je vstup pomocí MorphoDiTy převeden na lemma, tedy místo například `doktora` NLU uloží jen `doktor` (tedy potom když máte v kalendáři událost _doktor_, můžete se zeptat _„kdy mám v plánu doktora?“_ a událost bude správně nalezena).

#### DST - `dialmonkey/dst/rule.py`

DST je připraven jak pro aktuální použití bez uvažování pravděpodobnostního rozložení hodnot slotů, tak pro případné rozšíření o pravděpodobnosti. Vlastní stav je slovník, který má jako klíče názvy slotů. Při použití bez pravděpodobností je jednoduše přidán záznam do slovníku, pokud tento klíč ve slovníku již existoval, je hodnota přepsána (chápáno tak, že si to uživatel rozmyslel). Speciálním je intent `task` se slotem `goal`, jehož hodnota je uložena pod klíč `goal_`, tato hodnota je dále chápána jako uživatelův primární cíl v konverzaci.

#### DP - `dialmonkey/policy/planner.py`respektive `dialmonkey/policy/planner_server.py`

Při inicializaci DP je vytvořena zároveň i služba pro komunikaci s Google Calendar API, tedy provedena autentizace. Tato autentizace je pak provázána s danou instancí DP (a přeneseně pak s instancí `ConversatioHandleru`, ke kterému DP patří). V případě konzolové verze je autentizační token uložen do `examples-testing/token.json`, takže při dalším behu již není autentizace ze strany uživatele nutná. V případě webové verze se token neukládá je nutno provést autentizaci při zahájení dialogu.

DP se dívá na `goal_` dané konverzace a na základě toho koná. U manipulací s událostmi se ještě uživatele ptá na potvrzení, že vše bylo pochopeno správně. Pokud se uživatelův cíl změní, přechozí potvrzení je samozřejmě zneplatněno.

Pro každý druh úkonu má DP seznam slotů, jejichž zaplnění kontroluje (například pro dotaz na události v nějakém dni je třeba znát, jaký den uživatele zajímá). Pokud tyto sloty nejsou zaplněny, DP vyplní záměr na tyto sloty se zeptat. Pokud jsou všechny sloty pro danou akci vyplněny, vyplní jako záměr podat všechny informace (pokud šlo jen o dotazovací cíl), nebo zeptat se na potvrzení (pokud byla cílem nějaká manipulace). Pokud uživatel potvrzení udělí, je manipulace provedena a vyplněn záměr informovat o tom.

V případě informací o událostech, kdy je vyplněno více informačních slotů, přidává na jejich začátek speciální slot `event_by_name` nebo `event_by_date`, které NLG napovídají, kolik následujících slotů má pro informování použít.

#### NLG - `dialmonkey/nlg/planner.py`

NLG vezme záměry vyplněné DP a pomocí šablon uložených v `dialmonkey/nlg/templates/planner.json` je převede na přirozený jazyk. Většina šablon má více variant, v takovém případě je mezi nimi vybráno náhodně.

Pokud detekuje jeden ze speciálních slotů `event_by_(name|date)`, použije následujících 5 (nebo 4) sloty pro informování o událostech pomocí šablony. Pokud takových událostí je víc, spojí je náhodně vybranou spojkou.

Všechny zbylé sloty se snaží zpracovat tak, že nejprve zkusí najít šablonu odpovídající všem slotům. Pokud takovou nenajde, zkusí najít šablonu odpovídající dvěma po sobě jdoucím slotům. Pokud ani takovou nenajde, použije šablonu pro samostatný slot (které pro každý slot existují) a pokračuje dál. Ideální by bylo zkusit najít šablonu pokrývající co nejvíce slotů, ale to bychom museli procházet všechny podmnožiny slotů, tedy v nejhorším případě množství kombinací exponenciální k množství slotů, což by bylo neudržitelné.

Věty v přirozeném jazyce pak vrátí jako `system_response` a `ConversationHandler` tuto odpověď vrátí uživateli.
