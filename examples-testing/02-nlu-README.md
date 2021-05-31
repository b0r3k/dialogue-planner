# Dialogue acts

## Intents, slots, values

### Intent `task`
- slot: `goal`    -   values: `ask_day, ask_event, add_event, specify_event, change_event, delete_event, plan_commute`

### Intent `inform`
- slot: `name`  -   values: `/open/` (string)
- slot: `date`  -   values: `date`
- slot: `time_start`    -   values: `time` or `anytime`
- slot: `time_end`    -   values: `time` or `anytime`
- slot: `duration`  -   values: `timedelta`
- slot: `place` -   values: `/open/` (string)
- slot: `repeating`  -   values: `none/day/week/month/year`
- slot: `place_start` -   values: `home` / `work` / `/open/` (string name of place)
- slot: `place_end` -   values: `home` / `work` / `/open/` (string name of place)

### Intent `confirm`
- slot: `value`   -   values: `True/False`

### Intent `undo`

## Examples

- Co mám v plánu zítra? -   `task(goal=ask_day) & inform(date=tomorrow)`
- Ano, přidat cvičit, každý den.  -   `confirm(value=True) & task(goal=add_event) & inform(repeating=day) & inform(name=cvičit)`
- V sedm večer, hodinu. -   `inform(time=19:00) & inform(duration=0:01:00)`
- Naplánovat dopravu, ráno z domu, večer domů.  -   `task(goal=plan_commute) & inform(place_start=home) & inform(place_end=home)`
- Naplánovat kadeřnictví u Anny 13.5. od 3 odpoledne na hodinu.  -   `task(goal=add_event) & inform(date=2021-05-13,time_start='15:00',duration='1:00',name='kadeřnictví u anny')`
- Ne, konec.    -   `confirm(value=False)`