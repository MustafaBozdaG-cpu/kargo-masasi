import unittest

from kargo_masasi.agirlik import Parca, hesapla, yarim_kiloya_yuvarla
from kargo_masasi.kontrol import kontrol_et


class AgirlikTesti(unittest.TestCase):
    def test_yuvarlama(self):
        self.assertEqual(yarim_kiloya_yuvarla(101.2), 101.5)
        self.assertEqual(yarim_kiloya_yuvarla(101.6), 102.0)
        self.assertEqual(yarim_kiloya_yuvarla(100.0), 100.0)

    def test_brut_esas(self):
        # 4 x 120x80x110 = 4.224 m³ -> 704 kg hacim; brüt 720 kg
        s = hesapla([Parca(4, 120, 80, 110, birim_agirlik=180)])
        self.assertEqual(s.hacim_kg, 704.0)
        self.assertEqual(s.ucrete_esas_kg, 720.0)
        self.assertEqual(s.esas_alinan, "brüt")

    def test_hacim_esas_toplam_agirlikla(self):
        # 12 x 60x40x40 = 1.152 m³ -> 192 kg hacim; brüt 150 kg
        s = hesapla([Parca(12, 60, 40, 40)], toplam_brut_kg=150)
        self.assertEqual(s.ucrete_esas_kg, 192.0)
        self.assertEqual(s.esas_alinan, "hacim")

    def test_birim_cevirme(self):
        s = hesapla([Parca(1, 1.2, 0.8, 1.0, olcu_birimi="m", birim_agirlik=100, agirlik_birimi="lb")])
        self.assertEqual(s.hacim_kg, 160.0)
        self.assertEqual(s.brut_kg, 45.4)

    def test_eksik_tarih(self):
        talep = {"kalkis": "IST", "varis": "FRA", "istenen_tarih": None, "mal_cinsi": "x",
                 "parcalar": [{"adet": 1, "uzunluk": 10, "genislik": 10, "yukseklik": 10,
                               "olcu_birimi": "cm", "birim_agirlik": 5, "agirlik_birimi": "kg"}],
                 "toplam_brut_agirlik": None, "toplam_agirlik_birimi": "kg", "ozel_durumlar": []}
        k = kontrol_et(talep)
        self.assertEqual(k.eksikler, ["istenen_tarih"])
        self.assertIsNotNone(k.agirlik)


if __name__ == "__main__":
    unittest.main()
