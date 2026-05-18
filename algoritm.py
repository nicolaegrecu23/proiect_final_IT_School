"""
Algoritm de atribuire a garzilor.
"""

import calendar
import random
from datetime import date

from clase import Garda, EroareAtribuireGarda
import logging

class Algoritm:
    """
    Algoritm de generare a programului de garzi.

    Respecta constrangeri "hard" (eligibilitate, indisponibilitate, pauza minima intre garzi, limita lunara) si optimizeaza in
     functie de constrangeri "soft" (preferinte, echitate).
    """
    LIMITA_GARZI_PE_LUNA = 10
    LIMITA_WEEKENDURI_PE_LUNA = 3
    PAUZA_MINIMA_ZILE = 2
    BONUS_PREFERINTA_PRIORITATE_1 = 500
    BONUS_PREFERINTA_PRIORITATE_2 = 100
    MULTIPLICATOR_ECHITATE = 50
    MULTIPLICATOR_WEEKEND = 100
    
    def __init__(self, db):
        """
        Args:
            db: instanta DatabaseManager folosita pentru citirea datelor
        """
        self._db = db
    
    def genereaza_program(self, an: int, luna: int) -> list[Garda]:
        """
        Genereaza programul de garzi pentru luna specificata - atribuire in 2 etape:
        1) Filtrare in mai multe etape: pentru fiecare zi, pentru fiecare linie, sunt verificati medicii eligibili, apoi cei care
         sunt disponibili, apoi respectarea limitelor de numar de garzi si a pauzei dintre garzi.
        2) Se calculeaza un scor pentru fiecare medic in functie de constantele de clasa, iar medicului cu scorul cel mai mare ii
         este atribuita garda; suplimentar, se adauga o valoare aleatoare intre 0 si 0.5 pentru departajare in caz de egalitate.
        
        Args:
            an: anul (ex: 2025)
            luna: luna (1-12)
        
        Returns:
            Lista de obiecte Garda atribuite.
        
        Raises:
            EroareAtribuireGarda: daca nu se poate atribui vreo garda.
        """
        logging.info(f"Incep generarea programului pentru {an}-{luna:02d}")
        
        medici = self._db.listare_medici()
        linii = self._db.listare_linii_garda()
        indisponibilitati = self._db.listare_indisponibilitati()
        preferinte = self._db.listare_preferinte()
        
        garzi_atribuite = []
        
        zile = self._zilele_lunii(an, luna)
        
        for zi in zile:
            for linie in linii:
                eligibili_pe_linie = self._medici_eligibili_pe_linie(medici, linie)
                
                disponibili = [m for m in eligibili_pe_linie if self._este_disponibil(m, zi, indisponibilitati)]
                
                candidati = [m for m in disponibili if self._verifica_constrangeri(m, zi, garzi_atribuite)]
                if not candidati:
                    msg = (f"Conflict atribuire: nu exista medic eligibil pentru linia '{linie.nume}' in {zi}.")
                    logging.error(msg)
                    raise EroareAtribuireGarda(msg)
                
                scor_maxim = 0
                medic_ales = None
                for m in candidati:
                    scor = self._calculeaza_scor(m, zi, garzi_atribuite, preferinte)
                    if scor >= scor_maxim:
                        scor_maxim = scor
                        medic_ales = m
                
                garda = Garda(medic_id=medic_ales.id, linie_id=linie.id, data=zi)
                garzi_atribuite.append(garda)
        
        logging.info(f"Program generat cu succes: {len(garzi_atribuite)} garzi pentru {an}-{luna:02d}")

        return garzi_atribuite
    
    def _zilele_lunii(self, an: int, luna: int) -> list[date]:
        """
        Returneaza lista cu toate zilele din luna.
        """
        zile = []
        zi = 1
        while True:
            try:
                zile.append(date(an, luna, zi))
                zi += 1
            except ValueError:
                break
        return zile
    
    def _medici_eligibili_pe_linie(self, medici, linie):
        """
        Returneaza medicii care pot face garda pe linia specificata.
        """
        return [m for m in medici if linie.id in m.verifica_eligibilitate()]
    
    def _este_disponibil(self, medic, zi, indisponibilitati) -> bool:
        """
        Verifica daca medicul nu are indisponibilitate in ziua data.
        """
        indisp_medic = [i for i in indisponibilitati if i.medic_id == medic.id]
        for indisp in indisp_medic:
            if indisp.este_indisponibil(zi):
                return False
        return True
    
    def _verifica_constrangeri(self, medic, zi, garzi_atribuite) -> bool:
        """
        Verifica constrangerile obligatorii: sub limita LIMITA_GARZI_PE_LUNA, respecta PAUZA_MINIMA_ZILE intre garzi
        """
        garzi_medic = [g for g in garzi_atribuite if g.medic_id == medic.id]
        
        if len(garzi_medic) >= self.LIMITA_GARZI_PE_LUNA:
            return False
        
        for g in garzi_medic:
            diferenta_zile = abs((zi - g.data).days)
            if diferenta_zile < self.PAUZA_MINIMA_ZILE:
                return False
        
        return True
    
    def _calculeaza_scor(self, medic, zi, garzi_atribuite, preferinte) -> float:
        """
        Calculeaza scorul candidatului pentru aceasta zi.
        """
        scor = 0.0
        
        for pref in preferinte:
            if pref.medic_id == medic.id and pref.data == zi:
                if pref.prioritate == 1:
                    scor += self.BONUS_PREFERINTA_PRIORITATE_1
                else:
                    scor += self.BONUS_PREFERINTA_PRIORITATE_2
                break
        
        garzi_medic_actuale = sum(1 for g in garzi_atribuite if g.medic_id == medic.id)
        ramase = self.LIMITA_GARZI_PE_LUNA - garzi_medic_actuale
        scor += ramase * self.MULTIPLICATOR_ECHITATE
        
        if zi.weekday() >= 5:
            weekenduri_medic = sum(1 for g in garzi_atribuite if g.medic_id == medic.id and g.data.weekday() >= 5)
            ramase_weekend = self.LIMITA_WEEKENDURI_PE_LUNA - weekenduri_medic
            scor += ramase_weekend * self.MULTIPLICATOR_WEEKEND
        
        scor += random.uniform(0, 0.5)
        
        return scor
