"""
Fisier care contine codul SQLite pentru baza de date.
"""

import os
import sqlite3
from datetime import date
from clase import Medic, Primar, Specialist, Rezident, LinieGarda, Indisponibilitate, Preferinta
import logging

FOLDER = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(FOLDER, "garzi.db")

class DatabaseManager:
    """
    Gestioneaza baza de date SQLite pentru aplicatia de garzi.
    
    Operatii CRUD pentru toate entitatile:
    - medici (cu 3 subclase via single table inheritance)
    - linii_garda
    - indisponibilitati
    - preferinte
    - garzi_generate
    """
    
    def __init__(self, db_nume: str = DB_PATH):
        """
        Initializeaza managerul de DB.
        
        Args:
            db_nume: calea catre fisierul DB (default: garzi.db in folderul proiectului)
        """
        self.db_nume = db_nume
        self._creare_tabele()
    
    def _creare_tabele(self) -> None:
        """
        Creeaza toate tabelele daca nu exista deja.
        """
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medici (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nume TEXT NOT NULL,
                    prenume TEXT NOT NULL,
                    grad TEXT NOT NULL,
                    an INTEGER,
                    telefon TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS linii_garda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nume TEXT NOT NULL UNIQUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS indisponibilitati (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medic_id INTEGER NOT NULL,
                    data_start TEXT NOT NULL,
                    data_stop TEXT NOT NULL,
                    FOREIGN KEY (medic_id) REFERENCES medici(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferinte (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medic_id INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    prioritate INTEGER NOT NULL CHECK (prioritate IN (1, 2)),
                    FOREIGN KEY (medic_id) REFERENCES medici(id)
                )
            """)
            
            connection.commit()
        
        logging.info(f"Baza de date initializata: {self.db_nume}.")
    
    def adauga_medic(self, medic: Medic) -> int:
        """
        Adauga un medic in DB. Returneaza id-ul atribuit automat de SQLite.
        """
        nume = medic.nume
        prenume = medic.prenume
        telefon = medic.telefon
        grad = medic.__class__.__name__.lower()
        an = medic.an if isinstance(medic, Rezident) else None
        
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO medici (nume, prenume, grad, an, telefon)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nume, prenume, grad, an, telefon)
            )
            connection.commit()
            id_nou = cursor.lastrowid
        
        logging.info(f"Medic adaugat: id={id_nou}, {nume} {prenume} ({grad})")
        return id_nou
    
    def listare_medici(self) -> list[Medic]:
        """
        Returneaza lista cu toti medicii din DB.
        """
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, nume, prenume, grad, an, telefon
                FROM medici
                ORDER BY id
            """)
            
            lista_medici = []
            for row in cursor.fetchall():
                id, nume, prenume, grad, an, telefon = row
                if grad == "primar":
                    medic = Primar(nume=nume, prenume=prenume, id=id, telefon=telefon)
                elif grad == "specialist":
                    medic = Specialist(nume=nume, prenume=prenume, id=id, telefon=telefon)
                elif grad == "rezident":
                    medic = Rezident(nume=nume, prenume=prenume, an=an, id=id, telefon=telefon)
                else:
                    raise ValueError(f"Grad necunoscut in DB: '{grad}' (medic_id={id})")
                lista_medici.append(medic)
        
        return lista_medici
    
    def gaseste_medic_dupa_id(self, medic_id: int) -> Medic | None:
        """
        Returneaza un medic dupa id, sau None daca nu exista.
        """
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, nume, prenume, grad, an, telefon
                FROM medici
                WHERE id = ?
            """, (medic_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            id, nume, prenume, grad, an, telefon = row
            if grad == "primar":
                return Primar(nume=nume, prenume=prenume, id=id, telefon=telefon)
            elif grad == "specialist":
                return Specialist(nume=nume, prenume=prenume, id=id, telefon=telefon)
            elif grad == "rezident":
                return Rezident(nume=nume, prenume=prenume, an=an, id=id, telefon=telefon)
            else:
                raise ValueError(f"Grad necunoscut in DB: '{grad}' (medic_id={id}).")
    
    def update_medic(self, medic: Medic) -> None:
        """
        Actualizeaza datele unui medic existent dupa id.
        """
        if medic.id is None:
            raise ValueError("Medicul nu are id setat — nu poate fi actualizat.")
        
        nume = medic.nume
        prenume = medic.prenume
        telefon = medic.telefon
        grad = medic.__class__.__name__.lower()
        an = medic.an if isinstance(medic, Rezident) else None
        
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE medici
                SET nume = ?, prenume = ?, grad = ?, an = ?, telefon = ?
                WHERE id = ?
                """,
                (nume, prenume, grad, an, telefon, medic.id)
            )
            connection.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Nu exista medic cu id={medic.id} in DB.")
        
        logging.info(f"Medic actualizat: id={medic.id}, {nume} {prenume}")
    
    def sterge_medic(self, medic_id: int) -> None:
        """
        Sterge un medic din DB dupa id (sterge de asemenea si indisponibilitatile si preferintele).
        """
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM indisponibilitati WHERE medic_id = ?",
                (medic_id,)
            )
            cursor.execute(
                "DELETE FROM preferinte WHERE medic_id = ?",
                (medic_id,)
            )
            cursor.execute("DELETE FROM medici WHERE id = ?", (medic_id,))
            connection.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Nu exista medic cu id={medic_id} in DB.")
        
        logging.info(f"Medic sters: id={medic_id}")
    
    def adauga_linie_garda(self, linie: LinieGarda) -> int:
        """Adauga o linie de garda. Returneaza id-ul atribuit."""
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO linii_garda (nume) VALUES (?)", (linie.nume,))
            connection.commit()
            id_nou = cursor.lastrowid
        
        logging.info(f"Linie garda adaugata: id={id_nou}, '{linie.nume}'")
        return id_nou
    
    def listare_linii_garda(self) -> list[LinieGarda]:
        """Returneaza toate liniile de garda din DB."""
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, nume FROM linii_garda ORDER BY id")
            return [LinieGarda(id=row[0], nume=row[1]) for row in cursor.fetchall()]
    
    def update_linie_garda(self, linie: LinieGarda) -> None:
        """Actualizeaza numele unei linii de garda."""
        if linie.id is None:
            raise ValueError("Linia nu are id setat — nu poate fi actualizata.")
        
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE linii_garda SET nume = ? WHERE id = ?", (linie.nume, linie.id))
            connection.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Nu exista linie cu id={linie.id}.")
        
        logging.info(f"Linie garda actualizata: id={linie.id}")
    
    def sterge_linie_garda(self, linie_id: int) -> None:
        """Sterge o linie de garda dupa id."""
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM linii_garda WHERE id = ?", (linie_id,))
            connection.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Nu exista linie cu id={linie_id}.")
        
        logging.info(f"Linie garda stearsa: id={linie_id}")
    
    def adauga_indisponibilitate(self, indisp: Indisponibilitate) -> int:
        """Adauga o indisponibilitate. Returneaza id-ul atribuit."""
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO indisponibilitati (medic_id, data_start, data_stop)
                VALUES (?, ?, ?)
                """,
                (indisp.medic_id, indisp.data_start.isoformat(), indisp.data_stop.isoformat())
            )
            connection.commit()
            id_nou = cursor.lastrowid
        
        logging.info(f"Indisponibilitate adaugata: id={id_nou}, medic={indisp.medic_id}, {indisp.data_start} - {indisp.data_stop}")
        return id_nou
    
    def listare_indisponibilitati(self, medic_id: int | None = None) -> list[Indisponibilitate]:
        """
        Returneaza indisponibilitatile.
        
        Args:
            medic_id: daca este setat, filtreaza doar indisponibilitatile acestui medic; daca este None, returneaza toate indisponibilitatile.
        """
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            
            if medic_id is None:
                cursor.execute("""
                    SELECT id, medic_id, data_start, data_stop
                    FROM indisponibilitati
                    ORDER BY data_start
                """)
            else:
                cursor.execute("""
                    SELECT id, medic_id, data_start, data_stop
                    FROM indisponibilitati
                    WHERE medic_id = ?
                    ORDER BY data_start
                """, (medic_id,))
            
            rezultat = []
            for row in cursor.fetchall():
                id, m_id, d_start_str, d_stop_str = row
                indisp = Indisponibilitate(id=id, medic_id=m_id, data_start=date.fromisoformat(d_start_str), data_stop=date.fromisoformat(d_stop_str))
                rezultat.append(indisp)
            return rezultat
    
    def sterge_indisponibilitate(self, indisp_id: int) -> None:
        """Sterge o indisponibilitate dupa id."""
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM indisponibilitati WHERE id = ?", (indisp_id,))
            connection.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Nu exista indisponibilitate cu id={indisp_id}.")
        
        logging.info(f"Indisponibilitate stearsa: id={indisp_id}")
    
    def adauga_preferinta(self, pref: Preferinta) -> int:
        """Adauga o preferinta. Returneaza id-ul atribuit."""
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO preferinte (medic_id, data, prioritate)
                VALUES (?, ?, ?)
                """,
                (pref.medic_id, pref.data.isoformat(), pref.prioritate)
            )
            connection.commit()
            id_nou = cursor.lastrowid
        
        logging.info(f"Preferinta adaugata: id={id_nou}, medic={pref.medic_id}, {pref.data}, prioritate={pref.prioritate}")
        return id_nou
    
    def listare_preferinte(self, medic_id: int | None = None) -> list[Preferinta]:
        """
        Returneaza preferintele (toate sau filtrate dupa medic).
        """
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            
            if medic_id is None:
                cursor.execute("""
                    SELECT id, medic_id, data, prioritate
                    FROM preferinte
                    ORDER BY data
                """)
            else:
                cursor.execute("""
                    SELECT id, medic_id, data, prioritate
                    FROM preferinte
                    WHERE medic_id = ?
                    ORDER BY data
                """, (medic_id,))
            
            return [Preferinta(id=row[0], medic_id=row[1], data=date.fromisoformat(row[2]), prioritate=row[3]) for row in cursor.fetchall()]
    
    def sterge_preferinta(self, pref_id: int) -> None:
        """Sterge o preferinta dupa id."""
        with sqlite3.connect(self.db_nume) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM preferinte WHERE id = ?", (pref_id,))
            connection.commit()
            if cursor.rowcount == 0:
                raise ValueError(f"Nu exista preferinta cu id={pref_id}.")
        
        logging.info(f"Preferinta stearsa: id={pref_id}")