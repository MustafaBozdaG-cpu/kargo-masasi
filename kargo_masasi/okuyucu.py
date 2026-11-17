"""Claude ile müşteri talep mailinden yapılandırılmış bilgi çıkarma.

Claude yalnız okur ve alanları doldurur; hesap yapmaz, tahmin etmez.
Mailde olmayan alan null döner. Hesaplar agirlik.py'de yapılır.
"""

from __future__ import annotations

import json

import anthropic

MODEL = "claude-opus-5-5"

_SAYI_YA_DA_NULL = {"type": ["number", "null"]}
_METIN_YA_DA_NULL = {"type": ["string", "null"]}

SEMA = {
    "type": "object",
    "properties": {
        "dil": {"type": "string", "enum": ["tr", "en"]},
        "musteri_firma": _METIN_YA_DA_NULL,
        "iletisim_kisi": _METIN_YA_DA_NULL,
        "kalkis": _METIN_YA_DA_NULL,
        "varis": _METIN_YA_DA_NULL,
        "istenen_tarih": _METIN_YA_DA_NULL,
        "mal_cinsi": _METIN_YA_DA_NULL,
        "parcalar": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "adet": {"type": "integer"},
                    "uzunluk": _SAYI_YA_DA_NULL,
                    "genislik": _SAYI_YA_DA_NULL,
                    "yukseklik": _SAYI_YA_DA_NULL,
                    "olcu_birimi": {"type": "string", "enum": ["cm", "m", "mm", "in"]},
                    "birim_agirlik": _SAYI_YA_DA_NULL,
                    "agirlik_birimi": {"type": "string", "enum": ["kg", "lb", "t"]},
                },
                "required": [
                    "adet", "uzunluk", "genislik", "yukseklik",
                    "olcu_birimi", "birim_agirlik", "agirlik_birimi",
                ],
                "additionalProperties": False,
            },
        },
        "toplam_brut_agirlik": _SAYI_YA_DA_NULL,
        "toplam_agirlik_birimi": {"type": "string", "enum": ["kg", "lb", "t"]},
        "ozel_durumlar": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["tehlikeli_madde", "soguk_zincir", "degerli", "canli_hayvan",
                         "bozulabilir", "ilac", "asiri_boyut"],
            },
        },
        "notlar": _METIN_YA_DA_NULL,
    },
    "required": [
        "dil", "musteri_firma", "iletisim_kisi", "kalkis", "varis", "istenen_tarih",
        "mal_cinsi", "parcalar", "toplam_brut_agirlik", "toplam_agirlik_birimi",
        "ozel_durumlar", "notlar",
    ],
    "additionalProperties": False,
}

SISTEM = """Sen bir hava kargo satış masasında çalışan asistansın. Görevin, müşteriden \
gelen fiyat talebi mailini okuyup istenen alanları doldurmak.

Kurallar:
- Yalnız mailde açıkça yazanı al. Yazmayan alanı null bırak; tahmin etme, uydurma.
- Ölçüleri ve ağırlıkları mailde yazan birimle ver; birim çevirme, hesap yapma.
- "3 palet, her biri 120x80x150 cm, 200 kg" gibi ifadelerde birim_agirlik tek parçanın \
ağırlığıdır. Mailde yalnız toplam ağırlık varsa parça ağırlığını null bırak, toplamı \
toplam_brut_agirlik alanına yaz.
- Kalkış ve varışı mailde yazdığı gibi yaz (şehir ya da havalimanı kodu).
- dil: mailin yazıldığı dil.
- ozel_durumlar: yalnız mailde işaret varsa ekle (ör. lityum pil, UN numarası -> \
tehlikeli_madde; +2/+8 °C -> soguk_zincir). Yoksa boş liste.
- notlar: satış temsilcisinin bilmesi gereken başka bir şey varsa kısaca, yoksa null."""


def oku(mail_metni: str, client: anthropic.Anthropic | None = None) -> dict:
    """Mail metnini Claude'a okutur, şemaya uygun sözlük döndürür."""
    client = client or anthropic.Anthropic()
    yanit = client.beta.messages.create(
        model=MODEL,
        max_tokens=4000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SISTEM,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SEMA}},
        messages=[{"role": "user", "content": f"<mail>\n{mail_metni}\n</mail>"}],
    )
    if yanit.stop_reason == "refusal":
        raise RuntimeError("Claude bu maili işlemeyi reddetti.")
    if yanit.stop_reason == "max_tokens":
        raise RuntimeError("Yanıt yarıda kesildi (max_tokens).")
    metin = next(b.text for b in yanit.content if b.type == "text")
    return json.loads(metin)
