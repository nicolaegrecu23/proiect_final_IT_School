"""
Fisier utilitar pentru popularea bazei de date pentru test.

Adauga elemente doar daca baza de date este goala.
"""

from baza_de_date import DatabaseManager
from clase import Primar, Specialist, Rezident, LinieGarda

def populeaza():
    """Populeaza DB-ul cu date de test daca e gol."""
    db = DatabaseManager()
    
    if len(db.listare_linii_garda()) == 0:
        db.adauga_linie_garda(LinieGarda(nume="Linia 1 - Sef de garda"))
        db.adauga_linie_garda(LinieGarda(nume="Linia 2 - Urgente"))
        db.adauga_linie_garda(LinieGarda(nume="Linia 3 - Sectie"))
        print("Linii de garda adaugate.")
    else:
        print(f"Liniile exista deja ({len(db.listare_linii_garda())} linii).")
    
    if len(db.listare_medici()) == 0:
        db.adauga_medic(Primar("popescu", "ion"))
        db.adauga_medic(Primar("ionescu", "maria"))
        
        db.adauga_medic(Specialist("marin", "andrei"))
        db.adauga_medic(Specialist("dumitru", "ana"))
        db.adauga_medic(Specialist("vasile", "george"))
        db.adauga_medic(Specialist("oprea", "cristian"))
        
        db.adauga_medic(Rezident("stan", "mihai", an=3))
        db.adauga_medic(Rezident("radu", "elena", an=3))
        db.adauga_medic(Rezident("toma", "alex", an=4))
        db.adauga_medic(Rezident("nica", "vlad", an=4))
        db.adauga_medic(Rezident("preda", "ioana", an=5))
        db.adauga_medic(Rezident("matei", "bogdan", an=5))
        
        print(f"Medici adaugati: {len(db.listare_medici())}.")
    else:
        print(f"Medicii exista deja ({len(db.listare_medici())} medici).")
    
    print(f"\nTotal medici: {len(db.listare_medici())}")
    print(f"Total linii: {len(db.listare_linii_garda())}")


if __name__ == "__main__":
    populeaza()