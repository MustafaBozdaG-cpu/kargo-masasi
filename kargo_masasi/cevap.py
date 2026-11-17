"""Satış temsilcisi için özet ve müşteriye cevap taslağı (şablon; Claude kullanmaz)."""

from __future__ import annotations

from .kontrol import SORULAR, KontrolSonucu


def _kg(x: float) -> str:
    return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def ozet(talep: dict, k: KontrolSonucu) -> str:
    satirlar = [
        "TALEP ÖZETİ",
        f"  Müşteri     : {talep.get('musteri_firma') or '-'} ({talep.get('iletisim_kisi') or '-'})",
        f"  Rota        : {talep.get('kalkis') or '?'} -> {talep.get('varis') or '?'}",
        f"  Tarih       : {talep.get('istenen_tarih') or '?'}",
        f"  Mal cinsi   : {talep.get('mal_cinsi') or '?'}",
    ]
    if k.agirlik:
        a = k.agirlik
        satirlar += [
            f"  Parça       : {a.toplam_adet} adet, {a.hacim_m3} m³",
            f"  Brüt        : {_kg(a.brut_kg)} kg",
            f"  Hacim ağ.   : {_kg(a.hacim_kg)} kg (cm³/6000)",
            f"  ÜCRETE ESAS : {_kg(a.ucrete_esas_kg)} kg  <- {"hacim ağırlığı" if a.esas_alinan == "hacim" else "brüt ağırlık"} esas alındı",
        ]
    satirlar.append("")
    if k.teklife_hazir:
        satirlar.append("DURUM: Teklif için bilgiler tam.")
    else:
        satirlar.append("DURUM: Eksik bilgi var -> " + ", ".join(SORULAR[e][0] for e in k.eksikler))
    for u in k.uyarilar:
        satirlar.append(f"  ! {u}")
    if talep.get("notlar"):
        satirlar.append(f"  Not: {talep['notlar']}")
    return "\n".join(satirlar)


def taslak(talep: dict, k: KontrolSonucu) -> str:
    en = talep.get("dil") == "en"
    kisi = talep.get("iletisim_kisi")
    rota = f"{talep.get('kalkis') or '?'} - {talep.get('varis') or '?'}"

    if en:
        selam = f"Dear {kisi}," if kisi else "Dear Sir/Madam,"
        govde = [selam, "", f"Thank you for your enquiry for {rota}."]
        if k.teklife_hazir:
            govde.append(
                f"Based on the details provided, the chargeable weight is "
                f"{k.agirlik.ucrete_esas_kg:.1f} kg. We will share our offer shortly."
            )
        else:
            govde.append("To prepare our offer, could you please confirm the following:")
            govde += [f"  - {SORULAR[e][1]}" for e in k.eksikler]
        govde += ["", "Kind regards,"]
    else:
        selam = f"Sayın {kisi}," if kisi else "Merhaba,"
        govde = [selam, "", f"{rota} talebiniz için teşekkür ederiz."]
        if k.teklife_hazir:
            govde.append(
                f"İlettiğiniz bilgilere göre ücrete esas ağırlık "
                f"{_kg(k.agirlik.ucrete_esas_kg)} kg'dır. Teklifimizi kısa süre içinde iletiyoruz."
            )
        else:
            govde.append("Teklif hazırlayabilmemiz için aşağıdaki bilgileri paylaşabilir misiniz?")
            govde += [f"  - {SORULAR[e][0]}" for e in k.eksikler]
        govde += ["", "Saygılarımızla,"]
    return "\n".join(govde)
