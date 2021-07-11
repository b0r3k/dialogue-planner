## Specifikace - Dialogový asistent pro komunikaci s kalendářem
 
- [Specifikace - Dialogový asistent pro komunikaci s kalendářem](#specifikace---dialogový-asistent-pro-komunikaci-s-kalendářem)
  - [1. Manipulace s kalendářem](#1-manipulace-s-kalendářem)
    - [1.1 Výpis událostí pro zadaný den](#11-výpis-událostí-pro-zadaný-den)
    - [1.2 Vyhledávání podle klíčového slova v názvu události](#12-vyhledávání-podle-klíčového-slova-v-názvu-události)
    - [1.3 Přidání události do kalendáře](#13-přidání-události-do-kalendáře)
    - [1.4 Úprava události](#14-úprava-události)
    - [1.5 Odstranění události z kalendáře](#15-odstranění-události-z-kalendáře)
  - [2. Webové rozhraní](#2-webové-rozhraní)
    - [2.1 Komunikace s backendem](#21-komunikace-s-backendem)
    - [2.2 Zahájení dialogu, autentizace](#22-zahájení-dialogu-autentizace)
    - [2.3 Více uživatelů](#23-více-uživatelů)
    - [2.4 Ukončení dialogu](#24-ukončení-dialogu)
 
Cílem práce je implementace dialogového systému pro komunikaci uživatele s kalendářem. Dialog bude probíhat v přirozeném jazyce, do budoucna je možné rozšíření do hlasové podoby. Cílovým jazykem je čeština. 
 
V základní variantě půjde o konzolovou aplikaci psanou v programovacím jazyce Python s možností spuštění s webovým frontendem používajícím AJAX.
 
Následuje přehled funkcí.
 
### 1. Manipulace s kalendářem
Zpracování kalendářových dat bude probíhat přes Google Calendar API. Dohromady bude dávat možnost dotázat se ohledně naplánovaných událostí (zadáním data nebo názvu), a také možnost události přidávat, měnit a odebírat.

Konkrétní seznam podporovaných funkcí:

#### 1.1 Výpis událostí pro zadaný den
Vypíše události pro zadaný den ("dnes"/"zítra"/datum) spolu s časem a místem konání.
#### 1.2 Vyhledávání podle klíčového slova v názvu události
Vyhledá událost obsahující v názvu zadané slovo a vypíše všechny výskyty, opět s časem a místem konání.
#### 1.3 Přidání události do kalendáře
Přidá do kalendáře událost s daným názvem, datem, časem a místem konání.
#### 1.4 Úprava události
Změní údaje u dřívevyhledané události.
#### 1.5 Odstranění události z kalendáře
Odstraní dříve vyhledanou událost z kalendáře.
 
### 2. Webové rozhraní
Webové rozhraní bude zajišťovat běh aplikace jakožto serveru s možností přístupu přes prohlížeč s jednoduchou stránkou.

Konkrétní seznam podporovaných funkcí:

#### 2.1 Komunikace s backendem
Webové rozhraní bude používat AJAX pro komunikaci s backendem, předávat požadavky z prohlížeče na běžící server.
#### 2.2 Zahájení dialogu, autentizace
Stiskem tlačítka bude zahájen dialog a uživatel vyzván k autorizaci aplikace k úpravě kalendáře.
#### 2.3 Více uživatelů
Server bude podporovat více uživatelů najednou, rozlišování budou pomocí `session id` a odbavováni budou synchronně, stav dialogu bude pro každého uživatele průběžně ukládán.
#### 2.4 Ukončení dialogu
Ukončení dialogu proběhne stiskem tlačítka, nebo po přibližně 3 minutách neaktivity automaticky.
