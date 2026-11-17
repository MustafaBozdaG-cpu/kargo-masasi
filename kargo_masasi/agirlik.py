"""Ücrete esas ağırlık (chargeable weight) hesabı.

Hava kargoda fiyat, gerçek (brüt) ağırlık ile hacim ağırlığından büyük olana göre
kesilir. Hacim ağırlığı IATA standardı: cm³ / 6000 = kg. Sonuç bir üst 0,5 kg'a
yuvarlanır. Bu dosya Claude kullanmaz; hesap her zaman aynı sonucu verir.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

HACIM_BOLENI = 6000  # cm³ / kg (IATA)

_UZUNLUK_CM = {"cm": 1.0, "m": 100.0, "mm": 0.1, "in": 2.54}
_AGIRLIK_KG = {"kg": 1.0, "lb": 0.45359237, "t": 1000.0}


@dataclass
class Parca:
    adet: int
    uzunluk: float
    genislik: float
    yukseklik: float
    olcu_birimi: str = "cm"
    birim_agirlik: float | None = None  # tek parçanın ağırlığı
    agirlik_birimi: str = "kg"

    def hacim_cm3(self) -> float:
        k = _UZUNLUK_CM[self.olcu_birimi]
        return self.adet * (self.uzunluk * k) * (self.genislik * k) * (self.yukseklik * k)

    def brut_kg(self) -> float | None:
        if self.birim_agirlik is None:
            return None
        return self.adet * self.birim_agirlik * _AGIRLIK_KG[self.agirlik_birimi]


def yarim_kiloya_yuvarla(kg: float) -> float:
    """Bir üst 0,5 kg'a yuvarlar: 101,2 -> 101,5 ; 101,6 -> 102,0."""
    return math.ceil(round(kg * 2, 6)) / 2


@dataclass
class AgirlikSonucu:
    toplam_adet: int
    hacim_m3: float
    brut_kg: float
    hacim_kg: float
    ucrete_esas_kg: float
    esas_alinan: str  # "brüt" veya "hacim"


def hesapla(parcalar: list[Parca], toplam_brut_kg: float | None = None) -> AgirlikSonucu:
    """Parçalardan ücrete esas ağırlığı hesaplar.

    Parça başına ağırlık yoksa mailde verilen toplam brüt ağırlık kullanılır.
    """
    if not parcalar:
        raise ValueError("En az bir parça gerekli.")
    hacim = sum(p.hacim_cm3() for p in parcalar)
    parca_brutleri = [p.brut_kg() for p in parcalar]
    if all(b is not None for b in parca_brutleri):
        brut = sum(parca_brutleri)
    elif toplam_brut_kg is not None:
        brut = toplam_brut_kg
    else:
        raise ValueError("Brüt ağırlık yok: ne parça başına ne toplam verilmiş.")
    hacim_kg = hacim / HACIM_BOLENI
    esas = max(brut, hacim_kg)
    return AgirlikSonucu(
        toplam_adet=sum(p.adet for p in parcalar),
        hacim_m3=round(hacim / 1_000_000, 3),
        brut_kg=round(brut, 1),
        hacim_kg=round(hacim_kg, 1),
        ucrete_esas_kg=yarim_kiloya_yuvarla(esas),
        esas_alinan="hacim" if hacim_kg > brut else "brüt",
    )
