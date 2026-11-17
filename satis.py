"""Satış masası: müşteri talep mailini oku, ücrete esas ağırlığı hesapla, cevap taslağı yaz.

Kullanım:
  python satis.py ornekler/talep_1_eksik.txt            # Claude ile oku (API anahtarı gerekir)
  python satis.py ornekler/talep_1_eksik.txt --kaydet   # okumayı .json olarak da kaydet
  python satis.py --kayitli ornekler/talep_1_eksik.json # kayıtlı okumayla, API'siz çalıştır
"""

import argparse
import json
import sys
from pathlib import Path

from kargo_masasi.cevap import ozet, taslak
from kargo_masasi.kontrol import kontrol_et


def main() -> int:
    ap = argparse.ArgumentParser(description="Kargo talep maili okuyucu")
    ap.add_argument("mail", nargs="?", help="Mail metni dosyası (.txt)")
    ap.add_argument("--kayitli", help="Daha önce kaydedilmiş okuma (.json); API çağrısı yapmaz")
    ap.add_argument("--kaydet", action="store_true", help="Claude okumasını mail yanına .json kaydet")
    a = ap.parse_args()

    if a.kayitli:
        talep = json.loads(Path(a.kayitli).read_text(encoding="utf-8"))
    elif a.mail:
        from kargo_masasi.okuyucu import oku
        talep = oku(Path(a.mail).read_text(encoding="utf-8"))
        if a.kaydet:
            hedef = Path(a.mail).with_suffix(".json")
            hedef.write_text(json.dumps(talep, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"(okuma kaydedildi: {hedef})\n")
    else:
        ap.print_help()
        return 1

    k = kontrol_et(talep)
    print(ozet(talep, k))
    print("\n" + "-" * 60 + "\nCEVAP TASLAĞI\n" + "-" * 60)
    print(taslak(talep, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
