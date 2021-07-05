## Testování
Číslované soubory ukazují funkčnost programu v různých fázích projektu. 

`credentials.json` jsou potřeba pro funkci Google API.

V této složce je případně vytvořen `token.json` používaný k opětovné autentizaci uživatele.

### 01 Koncept
`01-example-dialogues.md` ukazuje vzorové dialogy, jaká byla zamýšlená funkčnost systému. `01-planner-flowchart.png` ukazuje zamýšlený běh dialogu na diagramu.

### 02 NLU
`02-nlu-README.md` popisuje možné trojice intent-slot-value v NLU, `02-nlu-testing.json` je vzorový vstupní soubor, `02-nlu-examples.tsv` ukazuje výstupy naprogramované NLU na daných vstupech.

### 03 DST
`03-state-tracking-testing.txt` ukazuje výstup z DST (tedy stav dialogu, včetně NLU) na vstupech z `02-nlu-testing.json` postupně zadávaných v rámci jednoho dialogu.

### 04 DP
`04-policy-testing.txt` ukazuje výstup z DP (za použití NLU a DST) na uvedených testovacích vstupech.

### 05 API
`05-api-readme.md` obsahuje pracovní poznámky k funkčnosti Google API. `05-api-testing.txt` ukazuje několik dialogů používajících vše až po DP, ale DP navíc posílá požadavky na Google API.

### 06 NLG (kompletní)
`06-complete-testing.txt` ukazuje opět několik dialogů, tentokrát je ale výstup DP poslán ještě do NLG a vygenerován výstup v přirozeném jazyce. Ukazuje tedy dialogy za použití celého systému (byť od té doby byl mírně vylepšen).