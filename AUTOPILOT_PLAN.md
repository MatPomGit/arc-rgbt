# Plan badawczy arc-rgbt: RGB–Thermal Fusion

**Wersja dokumentu: 1.0.0. Stan wejściowy: 24.10.2026.**
**Repozytorium:** https://github.com/MatPomGit/arc-rgbt
**Snapshot źródłowy:** `9d9809589d4dbd0601230e1604f8fc0d0e0434b1`

Ten dokument opisuje oddzielną linię badawczą w portfelu ARC.
Stan wykonania, bramki i dowody są w [PROJECT_STATE.yaml](PROJECT_STATE.yaml),
a metodologia w [RESEARCH.md](RESEARCH.md), [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
oraz [dokumentacji MkDocs](docs/index.md).
Nie reprezentuje zatwierdzonych artykułów ani wyników z rzeczywistych sensorów.

## Cel i hipotezy

Weryfikować granice rozdzielczości oraz jakość synchronizacji i rejestracji
w fuzji danych RGB, NIR i LWIR, ze szczególnym uwzględnieniem tanich
sensorów i zasobowo ograniczonych platform. Projekt jest otwarty,
niezależny od producenta sprzętu i od konkretnego zastosowania.

| Ścieżka | Hipoteza i plan | Istniejący dowód | Warunek wyniku publikacyjnego |
| --- | --- | --- | --- |
| P01 | Wpływ liczby pikseli obiektu i degradacji na lokalizację | E00: siedem symulowanych siatek, P01 summary | Niezależne etykiety rzeczywistych obrazów, kontrola optyki, analiza niepewności |
| P02 | Wpływ przesunięcia czasowego i jakości kanałów na fuzję | E01: 4 syntetyczne warianty; E02: 84 analityczne scenariusze | Nie-oraklowy estymator jakości, pomiary czasowe, kalibracja, dane testowe poza treningiem |
| P03 | Kompromis dokładność–pamięć–opóźnienie–energia | EdgeLab: pomiary referencyjne host CPU | Pomiary na wskazanym MCU i udokumentowany koszt kwantyzacji/przycinania |

E01 jest demonstracją heurystyki wag, bez kalibracji prawdopodobieństw.
IoU z E02 jest wynikiem analitycznej geometrii, **nie** metryką detekcji modelu.
Współczynnik wielkości rozdzielczości nie poprawia ciągłego, znormalizowanego
IoU w modelu E02 przy stałym FOV. Żadna z tych symulacji nie potwierdza
skuteczności detekcji ludzi/pojazdów na rzeczywistych sensorach.

## Pakiety pracy i kryteria ukończenia

| ID | Pakiet | Zależności | Weryfikowalny rezultat |
| --- | --- | --- | --- |
| RGBT-01 | Zamrożenie pytań badawczych, porównań i metryk P01/P02 | Aktualne protokoły i ograniczenia | Wersjonowany prerejestrowany opis hipotez i jednostek analizy |
| RGBT-02 | Dobór danych RGB/LWIR i audyt licencji, podziałów oraz etykiet | RGBT-01 | Manifesty danych z pochodzeniem i kompletnymi adnotacjami |
| RGBT-03 | Walidacja zegarów, geometrii i wsparcia interpolacji | RGBT-02 | Zmierzone przesunięcia czasu i reszty reprojekcji |
| RGBT-04 | P01: kontrolowane eksperymenty rozdzielczości i degradacji | RGBT-02–03 | Metryki na danych niezależnych, niepewność i porównanie z E00 |
| RGBT-05 | P02: porównanie RGB-only, LWIR-only, fusion i wag adaptacyjnych | RGBT-02–03 | Abladacje, analiza synchronizacji i wynik out-of-sample |
| RGBT-06 | P03: profiling i pomiary na urządzeniu | Wybór docelowego MCU, budżetu i testowego modelu | RAM, flash, energia i opóźnienie na fizycznym urządzeniu |
| RGBT-07 | Macierz publikacyjna P01–P03 i niezależna recenzja | Dowody z właściwych pakietów | GO/NO-GO osobno dla każdej ścieżki, bez automatycznego submission |

Kolejność 1–7 wyraża zależności logiczne, a nie daty końcowe.
Liczba trzech ścieżek oznacza **kandydatów badawczych**, a nie
trzy gotowe publikacje lub gwarantowane zgłoszenia.

## Odtwarzalna weryfikacja referencyjna

```bash
python -m pip install -e '.[dev,docs]'
python -m pytest -q
python -m ruff check src tests tools
python -m tools.check_docs
python -m mkdocs build --strict --clean
arc-rgbt-e00 --config experiments/E00/config.yaml --output reports/E00
arc-rgbt-e01 --dataset datasets/manifests/e01-synthetic-quality.json --output reports/E01
arc-rgbt-e02 --config experiments/E02/config.json --output reports/E02
```

Odnotowane testy Andromedy wykonano dla przypiętych HEAD PR
`c2fc01d...` (131 PASS) i `7c8c335...` (136 PASS + MkDocs).
Nie wolno uznawać tych wyników za nowy test commita `9d9809589d4dbd0601230e1604f8fc0d0e0434b1`
bez wykonania na nim niezależnej walidacji.

## Strategia publikacyjna i koszty

Preferuj czasopisma z punktacją 200 przy rzeczywistym dopasowaniu
zakresu i jakości rezultatów; wykorzystanie jednego finansowanego APC
100/140 wymaga oceny kosztu alternatywnego. Potencjalne dopasowania
obejmują multimodalną fuzję, detekcję na sensorach i embedded AI,
lecz żadne czasopismo nie jest przypisane ani zarezerwowane.
Sprawdź aktualne kryteria punktowe i finansowe przed wyborem.
Wszelkie prace przygotowawcze i CI prowadź lokalnie/self-hosted,
bez płatnych API i bez automatycznego wysyłania manuskryptów.

## Zasada synchronizacji portfela

`PROJECT_STATE.yaml` oraz źródła protokołów są kanoniczne.
`MatPomGit/research-autopilot` utrzymuje rejestr i indeks planu;
dashboard jest tylko widokiem pochodnym. Zmiana statusu eksperymentu
lub manuskryptu musi opierać się na dokładnym SHA i dowodach.
Nie duplikuj aktywnych zadań w osobnych automatyzacjach.
