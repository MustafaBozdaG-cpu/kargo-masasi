"""Çıkarılan talepte teklif için eksik olan bilgileri bulur ve ağırlığı hesaplar."""

from __future__ import annotations

from dataclasses import dataclass, field

from .agirlik import AgirlikSonucu, Parca, _AGIRLIK_KG, hesapla

# Eksik alan -> (Türkçe soru, İngilizce soru)
SORULAR = {
    "kalkis": ("Gönderinin kalkış noktası (şehir/havalimanı)", "Origin (city/airport)"),
    "varis": ("Varış noktası (şehir/havalimanı)", "Destination (city/airport)"),
    "istenen_tarih": ("Gönderinin hazır olacağı / istenen uçuş tarihi", "Ready date / requested flight date"),
    "mal_cinsi": ("Malın cinsi (içerik)", "Commodity (nature of goods)"),
    "olculer": ("Her parçanın ölçüleri (U x G x Y)", "Dimensions of each piece (L x W x H)"),
    "agirlik": ("Brüt ağırlık (parça başına ya da toplam)", "Gross weight (per piece or total)"),
    "adet": ("Parça / koli adedi", "Number of pieces"),
}

OZEL_UYARILAR = {
    "tehlikeli_madde": "Tehlikeli madde: UN numarası, sınıf ve shipper's declaration istenmeli; operasyonla teyit.",
    "soguk_zincir": "Soğuk zincir: sıcaklık aralığı ve aktif/pasif konteyner bilgisi istenmeli.",
    "degerli": "Değerli kargo: beyan değeri ve güvenlik prosedürü teyit edilmeli.",
    "canli_hayvan": "Canlı hayvan: IATA LAR kuralları ve kafes ölçüleri teyit edilmeli.",
    "bozulabilir": "Bozulabilir kargo: raf ömrü ve depolama koşulu sorulmalı.",
    "ilac": "İlaç: GDP gereklilikleri ve sıcaklık aralığı teyit edilmeli.",
    "asiri_boyut": "Aşırı boyut: uçak tipi ve kapı ölçüsü uygunluğu operasyonla teyit edilmeli.",
}


@dataclass
class KontrolSonucu:
    eksikler: list[str] = field(default_factory=list)
    agirlik: AgirlikSonucu | None = None
    uyarilar: list[str] = field(default_factory=list)

    @property
    def teklife_hazir(self) -> bool:
        return not self.eksikler


def kontrol_et(talep: dict) -> KontrolSonucu:
    s = KontrolSonucu()
    for alan in ("kalkis", "varis", "istenen_tarih", "mal_cinsi"):
        if not talep.get(alan):
            s.eksikler.append(alan)

    parcalar_ham = talep.get("parcalar") or []
    if not parcalar_ham:
        s.eksikler.append("adet")
    olcu_tam = bool(parcalar_ham) and all(
        p.get("uzunluk") and p.get("genislik") and p.get("yukseklik") for p in parcalar_ham
    )
    if parcalar_ham and not olcu_tam:
        s.eksikler.append("olculer")

    toplam = talep.get("toplam_brut_agirlik")
    toplam_kg = None if toplam is None else toplam * _AGIRLIK_KG[talep.get("toplam_agirlik_birimi") or "kg"]
    parca_agirlik_tam = bool(parcalar_ham) and all(p.get("birim_agirlik") for p in parcalar_ham)
    if not parca_agirlik_tam and toplam_kg is None:
        s.eksikler.append("agirlik")

    if olcu_tam and (parca_agirlik_tam or toplam_kg is not None):
        parcalar = [
            Parca(
                adet=p["adet"], uzunluk=p["uzunluk"], genislik=p["genislik"],
                yukseklik=p["yukseklik"], olcu_birimi=p["olcu_birimi"],
                birim_agirlik=p["birim_agirlik"] if parca_agirlik_tam else None,
                agirlik_birimi=p["agirlik_birimi"],
            )
            for p in parcalar_ham
        ]
        s.agirlik = hesapla(parcalar, toplam_kg)

    s.uyarilar = [OZEL_UYARILAR[d] for d in talep.get("ozel_durumlar") or [] if d in OZEL_UYARILAR]
    return s
