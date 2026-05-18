# Program gestionare garzi

Aplicatie desktop pentru gestionarea garzilor intr-o sectie de spital - structurat pe 3 linii de garda. Permite administrarea medicilor, a indisponibilitatilor si preferintelor lor, si genereaza automat programul lunar de garzi respectand criterii de eligibilitate pentru fiecare linie de garda, pauza minima intre garzi si echitate in distributia acestora.

## Functionalitati

- Gestionare medici (CRUD) - adaugare, modificare, stergere, vizualizare medici cu 3 grade: primar, specialist, rezident (cu an de rezidentiat)
- Filtrare medici dupa grad
- Export medici in format CSV
- Gestionare indisponibilitati - perioade in care medicii nu pot face garda
- Gestionare preferinte - zile in care medicii prefera sa faca garda, cu prioritate inalta sau moderata
- Generare automata a programului lunar de garzi cu un algoritm care:
  - Respecta eligibilitatea pe linii de garda dupa grad
  - Evita atribuirea in zilele de indisponibilitate
  - Asigura pauza minima de 2 zile intre garzile aceluiasi medic
  - Limiteaza la 10 garzi pe luna per medic (3 weekend-uri)
  - Optimizeaza echitatea distributiei (gardi totale + weekend-uri)
  - Respecta preferintele pozitive ale medicilor
- Export program garzi in format CSV
- Export statistici de echitate in format CSV

## Structura proiectului

proiect_final/
-> main.py                          # punct de intrare
-> clase.py                         # modelele de date (Medic, LinieGarda, etc.)
-> baza_de_date.py                  # operatii SQLite (CRUD pe entitati)
-> algoritm.py                      # algoritm de generare a programului
-> logger_config.py                 # configurare logging
-> populeaza_db.py                  # script pentru date de test
-> README.md                        # fisier de descriere
-> .gitignore                       # fisiere excluse din Git
-> garzi.db                         # baza de date SQLite (auto-generata)
-> garzi_app.log                    # log aplicatie (auto-generat)
-> interfata/                       # pachet interfata grafica
-----> __init__.py
-----> fereastra_principala.py      # fereastra cu Notebook si tab-uri
-----> tab_medici.py                # tab CRUD medici + export CSV
-----> tab_indisponibilitati.py     # tab CRUD indisponibilitati
-----> tab_preferinte.py            # tab CRUD preferinte
-----> tab_program.py               # tab generare + export program si statistici

## Cerinte

- Python 3.10+ (pentru sintaxa `int | None`)
- Module incluse in Python: tkinter, sqlite3, csv, logging

## Instalare si rulare

1. Se cloneaza repository-ul https://github.com/nicolaegrecu23/proiect_final_IT_School.git
2. Se ruleaza aplicatia prin main.py pentru a genera baza de date si liniile de garda; este de asemenea pornita interfata grafica.
3. Se poate popula baza de date cu date de test disponibile in populeaza_db.py. Aceasta comanda adauga in DB 12 medici de test (2 primari, 4 specialisti, 6 rezidenti). Alternativ, se pot introduce manual datele.

## Utilizare

### Tab "Medici"

- Se completeaza formularul cu datele medicului (nume, prenume, grad, telefon [optional])
- Pentru rezidenti, selecteaza si anul (notificare in caz de neselectare)
- Se apasa "Adauga" pentru a salva datele introduse
- Se alege un medic din lista si se apasa "Modifica" sau "Sterge" pentru a modifica, respectiv a sterge, datele medicului
- Se pot filtra medicii in functie de grad prin alegerea acestuia din combobox si apoi prin apasarea butonului "Aplica filtru"
- Se poate exporta lista de medici in format .csv prin apasarea butonului "Exporta in CSV".

### Tab "Indisponibilitati"

- Se selecteaza un medic din combobox; in cazul in care acesta a fost recent introdus si nu apare in lista se apasa butonul "Refresh medici"
- Se scrie data inceput si data sfarsit pentru perioada de indisponibilitate in format `YYYY-MM-DD` (ex: `2026-05-18`)
- Se apasa "Adauga" pentru a salva indisponibilitatea
- Se poate afisa lista individuala de indisponibilitati pentru fiecare medic prin selectarea acestuia si apoi prin apasarea butonului "Aplica filtru"; daca nu se selecteaza niciun medic si se apasa acest buton va fi afisata lista intreaga de indisponibilitati.

### Tab "Preferinte"

- Similar cu indisponibilitati, dar pentru o singura data
- Suplimentar, trebuie selectata prioritatea - 1 (inalta) sau 2 (moderata) - pentru preferinta din data introdusa.

### Tab "Program garzi"

- Se selecteaza luna si anul
- Butonul "Genereaza si exporta program" - ruleaza algoritmul de garzi, iar programul se salveaza in `program_garzi_<an>_<luna>.csv`
- Butonul "Genereaza si exporta statistici" - salveaza statisticile de echitate in `statistici_garzi_<an>_<luna>.csv`

## Tehnologii si concepte folosite

- OOP: clase de baza si subclase (Medic → Primar/Specialist/Rezident), polimorfism (`verifica_eligibilitate`, `@property grad`), encapsulare
- SQLite: baza de date relationala cu 4 tabele, foreign keys, constrangeri (NOT NULL, UNIQUE)
- tkinter: interfata grafica cu Notebook, Frame, Treeview, Combobox, Entry, Button, messagebox
- Logging: inregistrare evenimente in fisier
- Type hints: adnotari de tip pentru claritate
- Separation of concerns: fiecare fisier are responsabilitate clara (date, DB, algoritm, GUI)
- CSV: import/export prin modulul standard `csv`

## Algoritmul de generare

Pentru fiecare zi din luna si pentru fiecare linie de garda:
1. Filtrare: medici eligibili pe linie (dupa grad)
2. Disponibilitate: filtrare dupa indisponibilitati
3. Constrangeri "hard": limita garzi pe luna + pauza minima intre garzi
4. Atribuire scor: fiecare candidat primeste un scor pe baza de:
   - Preferinte pozitive (bonus mare daca medicul a cerut acea zi)
   - Echitate generala (cati garzi mai poate face)
   - Echitate weekend (doar in weekend)
   - Departajare in caz de egalitate (pentru cazuri de scoruri egale)
5. Atribuire: medicul cu scorul cel mai mare primeste garda.

Daca nu exista niciun candidat pentru o zi-linie, algoritmul ridica `EroareAtribuireGarda`.

## Logging

Toate operatiile importante sunt inregistrate in `garzi_app.log`:
- Initializarea bazei de date
- Adaugari, modificari, stergeri (medici, indisponibilitati, preferinte)
- Generare program (start, succes, eroare).

Fisierul de log se creeaza automat in folderul proiectului la prima rulare.
