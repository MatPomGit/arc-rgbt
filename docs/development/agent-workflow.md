# Autonomiczna praca agentów i rygor badawczy

Wersja 1.0.0 (2026-10-31). Uzupełnienie [AGENTS.md](../../AGENTS.md), nie zastępuje szczególnych kontraktów projektu.

## Rozpoznaj, wybierz, zarezerwuj

Przeczytaj aktualny `main`, Issues, PR, zadania innych agentów, dokumentację projektu i dotychczasowe dowody. Najpierw dokończ istniejące PR, naprawy i blokady. Wybierz jeden mierzalny JUMP z określonym DoR: cel, wejście, zależności, wynik, kryteria i prawo do wykonania. Rezerwuj pracę w istniejącym mechanizmie Autopilota, nie twórz drugiego schedulera, kolejki ani rejestru. Limit: jeden aktywny feature PR w repozytorium i pięć w zarządzanym portfelu. Sprawdź pochodzenie, wersję, uprawnienia i wykluczenia skilli. Nie uruchamiaj niezaufanych narzędzi.

## Implementuj i dokumentuj

Czytaj PROJECT_STATE.yaml, AUTOPILOT_PLAN.md i tracker M0-M6. M0 wymaga prawa do danych. P07/P08 pozostają OPTIONAL HOLD. Nie pobieraj modeli ani zbiorów danych, nie ujawniaj partnerów. Symulacja i testy syntetyczne nie są empiryczną walidacją termiczną.

KISS, DRY, YAGNI, separation of concerns, istniejące interfejsy i najmniejsze uprawnienia mają pierwszeństwo przed nowymi abstrakcjami. W Pythonie stosuj odpowiednie PEP 8, 20, 257 i 484 oraz PEP pakietowania tylko przy rzeczywistym pakietowaniu. Nie dodawaj zbędnych zależności ani plików konfiguracji. Rozróżniaj hipotezę, symulację, syntetyczne fixture, dane empiryczne i wynik potwierdzony. Rejestruj źródło danych, warunki, wersje, SHA, seedy, podziały danych, ryzyko leakage, niepewność, wyniki negatywne i ograniczenia. Nie fabrykuj DOI, cytowań, wyników ani zatwierdzeń etycznych. Nie przesyłaj prywatnych danych do Issues, logów ani publicznego CI.

## Zweryfikuj, zintegruj i posprzątaj

Testy i dowody muszą dotyczyć exact SHA. Zapisz komendy, wersje narzędzi, środowisko oraz PASS, FAIL, BLOCKED, UNAVAILABLE lub NOT_RUN. Testy jednostkowe nie dowodzą skuteczności naukowej. Nie uruchamiaj niezaufanego PR na stałym runnerze. Zero wydatków bez autoryzacji. Sprawdź aktualne branch rules, CI i niezależne review; komentarz własnego konta nie zastępuje formalnej aprobaty GitHub. Po zmianie HEAD ponów odpowiednie kontrole.

DoD: rzeczywiste kryteria spełnione, testy i dokumentacja zgodne, Issue uaktualnione, PR scalony wyłącznie przy spełnionych bramkach, oddzielne wdrożenie sprawdzone, jeśli było wymagane; usunięta jedynie własna scalona gałąź i worktree. Przy blokadzie zapisz przyczynę, warunek wyjścia i następny JUMP.

Teksty dla użytkownika: poprawna polszczyzna, zdaniowe nagłówki, bez U+2013 i U+2014 poza cytatami i danymi. Dla materiałów dydaktycznych: polecenia konkretne, cztery wiarygodne opcje w pytaniach i klucz przechowywany oddzielnie.
