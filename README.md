# Kargo Masası

Hava kargo satış ve operasyon ekipleri için küçük, günlük kullanılabilecek araçlar.

## 1. Satış: talep maili okuyucu

Müşteriden gelen fiyat talebi maili genelde dağınıktır: ölçüler bir yerde, ağırlık başka bir yerdedir, tarih çoğu zaman yazmaz. Satış temsilcisi teklif hazırlamadan önce şunları yapar:

1. Maildeki bilgileri ayıklar.
2. Ücrete esas ağırlığı hesaplar.
3. Eksik bilgileri müşteriye sorar.

Bu araç bu üç adımı saniyeler içinde yapar.

```
TALEP ÖZETİ
  Müşteri     : Sample Apparel Inc. (Mark Lee)
  Rota        : IST -> JFK
  Parça       : 12 adet, 1.152 m³
  Brüt        : 150,0 kg
  Hacim ağ.   : 192,0 kg (cm³/6000)
  ÜCRETE ESAS : 192,0 kg  <- hacim ağırlığı esas alındı
DURUM: Teklif için bilgiler tam.
```

### İşbölümü

| Adım | Kim yapar | Neden |
|---|---|---|
| Maili okuyup alanları çıkarmak | Claude | Serbest metni anlamak bir dil modelinin işidir. |
| Ücrete esas ağırlık (cm³/6000, 0,5 kg yuvarlama) | Python | Hesap her seferinde aynı sonucu vermelidir. |
| Eksik bilgi kontrolü ve özel kargo uyarıları | Python | Kurallar açık ve denetlenebilir olmalıdır. |
| Cevap taslağı (TR/EN) | Şablon | Müşteriye giden metne uydurma bilgi karışmamalıdır. |

Claude'a "mailde yazmayanı boş bırak, tahmin etme" talimatı verilir. Çıktı JSON şemasına bağlıdır.

### Fiyat yok, bilerek

Fiyatlar her kurumun kendi tarifesine bağlıdır ve gizlidir. Araç fiyat vermez; temsilcinin teklif hazırlamak için ihtiyaç duyduğu her şeyi hazır eder.

## Çalıştırma

Python 3.12 veya üstü gerekir.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# API anahtarı olmadan, kayıtlı örnek okumalarla:
python satis.py --kayitli ornekler/talep_2_tam.json

# Claude ile gerçek okuma (ANTHROPIC_API_KEY gerekir):
python satis.py ornekler/talep_1_eksik.txt

# Testler:
python -m unittest discover -s tests -t .
```

`ornekler/` klasöründe üç hayali mail var: biri eksik bilgili (TR), biri eksiksiz (EN), biri soğuk zincirli ilaç gönderisi (TR).

## 2. Operasyon: vardiya devir özeti

Yakında.
