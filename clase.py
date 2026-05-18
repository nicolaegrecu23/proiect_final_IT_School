"""Modelele de date (Medic [+ clase derivate], LinieGarda, Indisponibilitate, Preferinta, Garda)."""

from datetime import date

class Medic:
    """
    Clasa de baza pentru toti medicii.
    
    Attributes:
        nume: numele de familie al medicului
        prenume: prenumele medicului
        id: identificatorul din baza de date (None pentru medic nesalvat inca)
        telefon: numar de telefon (optional)
    """
    
    def __init__(self, nume: str, prenume: str, id: int | None = None, telefon: str | None = None):
        self.nume = nume
        self.prenume = prenume
        self.id = id
        self.telefon = telefon
    
    @property
    def grad(self) -> str:
        """
        Creaza gradul medicului ca atribut din numele subclasei.
        """
        return self.__class__.__name__.lower()
    
    def verifica_eligibilitate(self) -> tuple[int, ...]:
        """
        Returneaza tuplul cu liniile de garda pe care le poate face acest medic (eligibilitate variabila pe linii de garda in functie de grad).
        
        Este suprascrisa de catre fiecare subclasa -> daca este apelata direct de catre o instanta Medic ridica eroare.
        """
        raise ValueError("Instanta trebuie redefinita cu unul dintre grade pentru a verifica eligibilitatea.")
    
    def __str__(self):
        return f"Nume: {self.nume.title()} {self.prenume.title()} - Grad: {self.grad}"
    
    def __repr__(self):
        return f"{self.__class__.__name__} - (id={self.id}, nume={self.nume!r}, prenume={self.prenume!r})"

class Primar(Medic):
    """
    Medic primar. Eligibil sa efectueze doar garzi pe Linia 1 (sef de garda).
    """
    
    def verifica_eligibilitate(self) -> tuple[int, ...]:
        return (1,)

class Specialist(Medic):
    """
    Medic specialist. Eligibil pe Linia 1 (sef garda) si Linia 2 (urgente).
    """

    def verifica_eligibilitate(self) -> tuple[int, ...]:
        return (1, 2)

class Rezident(Medic):
    """
    Medic rezident. Are atribut suplimentar 'an' (3, 4 sau 5 - anii 1 si 2 nu sunt eligibili).
    
    Eligibilitatea depinde de an:
        - an 3: doar Linia 3 (sectie)
        - an 4 sau 5: Linia 2 (urgente) sau Linia 3 (sectie)
    """
    
    def __init__(self, nume: str, prenume: str, an: int, id: int | None = None, telefon: str | None = None):
        super().__init__(nume=nume, prenume=prenume, id=id, telefon=telefon)
        if an not in (3, 4, 5):
            raise ValueError("An de rezidentiat invalid sau neeligibil pentru garda.")
        self.an = an
    
    @property
    def grad(self) -> str:
        """
        Genereaza gradul similar cu clasa parinte (Medic), insa adauga suplimentar atributul specific clasei Rezident (an).
        """
        return f"{self.__class__.__name__.lower()} an {self.an}"
    
    def verifica_eligibilitate(self) -> tuple[int, ...]:
        if self.an == 3:
            return (3,)
        else:
            return (2, 3)

class LinieGarda:
    """
    Reprezinta o linie de garda care trebuie acoperita zilnic.
    Exemple: "Linia 1 - Sef garda", "Linia 2 - Urgente", "Linia 3 - Sectie".
    """
    
    def __init__(self, nume: str, id: int | None = None):
        self.nume = nume
        self.id = id
    
    def __str__(self):
        return self.nume
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, nume={self.nume!r})"

class Indisponibilitate:
    """
    Reprezinta o perioada (sau o singura zi) in care un medic nu poate face garda.
    
    Daca medicul e indisponibil doar o zi, data_start == data_stop.
    """
    
    def __init__(self, medic_id: int, data_start: date, data_stop: date, id: int | None = None):
        if medic_id is None:
            raise ValueError("ID-ul medicului este obligatoriu.")
        if data_stop < data_start:
            raise ValueError("Data de sfarsit nu poate fi mai mica decat data de inceput.")
        self.medic_id = medic_id
        self.data_start = data_start
        self.data_stop = data_stop
        self.id = id
    
    def este_indisponibil(self, data: date) -> bool:
        """
        Verifica daca data furnizata se afla in perioada de indisponibilitate
        """
        return self.data_start <= data <= self.data_stop
    
    def __str__(self):
        if self.data_start == self.data_stop:
            return f"Indisponibil in {self.data_start}."
        return f"Indisponibil intre {self.data_start} si {self.data_stop}."
    
    def __repr__(self):
        return f"Indisponibilitate(id={self.id}, medic_id={self.medic_id}, data_start={self.data_start}, data_stop={self.data_stop})"
    
class Preferinta:
    """
    Reprezinta o zi in care medicul prefera sa faca garda.
    
    Prioritate:
        1 = inalta (medicul vrea neaparat acea zi)
        2 = moderata (medicul ar prefera, dar e flexibil)
    """
    
    def __init__(self, medic_id: int, data: date, prioritate: int, id: int | None = None):
        if medic_id is None:
            raise ValueError("ID-ul medicului este obligatoriu.")
        if prioritate not in (1, 2):
            raise ValueError("Prioritatea trebuie sa fie 1 (inalta) sau 2 (moderata).")
        self.medic_id = medic_id
        self.data = data
        self.prioritate = prioritate
        self.id = id
    
    def __str__(self):
        return f"Preferinta pentru {self.data} (prioritate {self.prioritate})."
    
    def __repr__(self):
        return f"Preferinta(id={self.id}, medic_id={self.medic_id}, data={self.data}, prioritate={self.prioritate})"
    
class Garda:
    """
    Reprezinta o garda atribuita: medic, linie de garda, data. Este rezultatul algoritmului de generare.
    """
    
    def __init__(self, medic_id: int, linie_id: int, data: date, id: int | None = None):
        if medic_id is None:
            raise ValueError("ID-ul medicului este obligatoriu.")
        if linie_id is None:
            raise ValueError("ID-ul liniei de garda este obligatoriu.")
        if data is None:
            raise ValueError("Data este obligatorie.")
        self.medic_id = medic_id
        self.linie_id = linie_id
        self.data = data
        self.id = id
    
    def este_weekend(self) -> bool:
        """
        Returneaza True daca garda e in weekend (sambata sau duminica).
        """
        return self.data.weekday() >= 5
    
    def __str__(self):
        return f"In data de {self.data} linia id={self.linie_id} de garda este asigurata de catre medicul id={self.medic_id}."
    
    def __repr__(self):
        return f"Garda(id={self.id}, data={self.data}, linie_id={self.linie_id}, medic_id={self.medic_id})"
    
class EroareAtribuireGarda(Exception):
    """
    Ridicata atunci cand algoritmul nu poate atribui o garda.
    """
    pass

def construieste_medic(nume: str, prenume: str, grad: str, an: int | None = None, telefon: str | None = None, id: int | None = None) -> Medic:
    """
    Factory helper: construieste obiectul corect (Primar/Specialist/Rezident) pe baza string-ului 'grad'.
    """
    if grad == "primar":
        return Primar(nume=nume, prenume=prenume, id=id, telefon=telefon)
    elif grad == "specialist":
        return Specialist(nume=nume, prenume=prenume, id=id, telefon=telefon)
    elif grad == "rezident":
        if an is None:
            raise ValueError("Pentru rezident trebuie specificat anul.")
        return Rezident(nume=nume, prenume=prenume, an=an, id=id, telefon=telefon)
    else:
        raise ValueError(f"Grad necunoscut: '{grad}'")
