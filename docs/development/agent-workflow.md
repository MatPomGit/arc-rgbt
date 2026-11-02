# Autonomiczna praca agentów i rygor badawczy

Wersja 1.1.2 (2026-11-02). Uzupełnienie `AGENTS.md` w katalogu głównym, nie zastępuje szczególnych kontraktów projektu.

## Rozpoznaj, wybierz, zarezerwuj

Przeczytaj aktualny `main`, Issues, PR, zadania innych agentów, dokumentację projektu i dotychczasowe dowody. Najpierw dokończ istniejące PR, naprawy i blokady. Wybierz jeden mierzalny JUMP z określonym DoR: cel, wejście, zależności, wynik, kryteria i prawo do wykonania. Rezerwuj pracę w istniejącym mechanizmie Autopilota, nie twórz drugiego schedulera, kolejki ani rejestru. Limit: jeden aktywny feature PR w repozytorium i pięć w zarządzanym portfelu. Sprawdź pochodzenie, wersję, uprawnienia i wykluczenia skilli. Nie uruchamiaj niezaufanych narzędzi.

## Implementuj i dokumentuj

Czytaj PROJECT_STATE.yaml, AUTOPILOT_PLAN.md i tracker M0-M6. M0 wymaga prawa do danych. P07/P08 pozostają OPTIONAL HOLD. Nie pobieraj modeli ani zbiorów danych, nie ujawniaj partnerów. Symulacja i testy syntetyczne nie są empiryczną walidacją termiczną.

KISS, DRY, YAGNI, separation of concerns, istniejące interfejsy i najmniejsze uprawnienia mają pierwszeństwo przed nowymi abstrakcjami. W Pythonie stosuj odpowiednie PEP 8, 20, 257 i 484 oraz PEP pakietowania tylko przy rzeczywistym pakietowaniu. Nie dodawaj zbędnych zależności ani plików konfiguracji. Rozróżniaj hipotezę, symulację, syntetyczne fixture, dane empiryczne i wynik potwierdzony. Rejestruj źródło danych, warunki, wersje, SHA, seedy, podziały danych, ryzyko leakage, niepewność, wyniki negatywne i ograniczenia. Nie fabrykuj DOI, cytowań, wyników ani zatwierdzeń etycznych. Nie przesyłaj prywatnych danych do Issues, logów ani publicznego CI.

## Zweryfikuj, zintegruj i posprzątaj

Testy i dowody muszą dotyczyć exact SHA. Zapisz komendy, wersje narzędzi, środowisko oraz PASS, FAIL, BLOCKED, UNAVAILABLE lub NOT_RUN. Testy jednostkowe nie dowodzą skuteczności naukowej. Nie uruchamiaj niezaufanego PR na stałym runnerze. Zero wydatków bez autoryzacji. Sprawdź aktualne branch rules, CI i niezależne review; komentarz własnego konta nie zastępuje formalnej aprobaty GitHub. Po zmianie HEAD ponów odpowiednie kontrole.

DoD: rzeczywiste kryteria spełnione, testy i dokumentacja zgodne, Issue uaktualnione, PR scalony wyłącznie przy spełnionych bramkach, oddzielne wdrożenie sprawdzone, jeśli było wymagane; usunięta jedynie własna scalona gałąź i worktree. Przy blokadzie zapisz przyczynę, warunek wyjścia i następny JUMP.

Teksty dla użytkownika: poprawna polszczyzna, zdaniowe nagłówki, bez U+2013 i U+2014 poza cytatami i danymi. Dla materiałów dydaktycznych: polecenia konkretne, cztery wiarygodne opcje w pytaniach i klucz przechowywany oddzielnie.

## Obowiazkowy plan przed kazdym przebiegiem

Przed wybraniem Issue lub wykonaniem jakiejkolwiek pracy **zawsze odczytaj najnowszy [AUTOPILOT_PLAN.md](https://github.com/MatPomGit/arc-rgbt/blob/main/AUTOPILOT_PLAN.md)**, aktualny `PROJECT_STATE.yaml`, [tracker M0-M6 #21](https://github.com/MatPomGit/arc-rgbt/issues/21), biezace PR i protokol konkretnego badania. W logu zapisz wersje/SHA planu, numer zadania i warunek zakonczenia. Plan stanowi aktualna kolejke wykonawcza, nie zastawia bezpieczenstwa `AGENTS.md`, merytorycznych protokolow ani statusow dowodow. Po zmianie planu ponow odczyt przy kolejnym JUMP.

Dla P01 PR #44 zostal scalony jako kod syntetycznego audytu (main SHA `18c9b754164fc5208ce7c8aaa3f81c8d6ade9e66`), a jego galaz usunieta. Kolejne priorytety to #45 (zrodla danych) i #49 (NIEZAKONCZONA niezalezna recenzja metod), kolejne zadania #46-#53 przed 2026-11-13, #54-#57 do 2026-12-11, #58-#60 po rzeczywistym G01 PASS, #61-#62 przed recenzja i #40 przed podjeciem decyzji o zgloszeniu. Wpis terminu nie jest zgoda na obejscie bramki naukowej. Przestrzegaj zaleznosci opisanych w planie; nie uruchamiaj na raz wielu nowych PR.

## Bezplatne GitHub Actions w publicznym repozytorium

Dokumentacja GitHub potwierdzona 2026-11-02: standardowe GitHub-hosted runnery dla publicznych repozytoriow maja **bezplatne, nielimitowane miesiecznie minuty wykonania**. Bezplatnosc nie znosi limitow rownoleglosci, czasu, przestrzeni artefaktow i zasad uzytkowania. Dla self-hosted brak oplaty za minute Actions, ale istnieje koszt lokalnej infrastruktury. **Larger runners, platne uslugi, nadmiar przechowywanych artefaktow i inne oplaty pozostaja zabronione bez oddzielnej autoryzacji.**

**Interpretacja zasady zero-cost:** bezpłatne wykonywanie standardowych `GitHub Actions` w publicznym `arc-rgbt` jest dozwolone i **nie narusza zasady zero-cost**. Agenci moga uruchamiac i ponawiac konieczne testy, lint, walidacje i dokumentacje bez sztucznego oszczedzania minut; musza jednak przestrzegac limitow technicznych, regulaminu GitHub, uprawnien i bezpieczenstwa. Wlasciciel deklaruje aktywny pakiet edukatorski GitHub Education. Uprawnienia edukatorskie moga obejmowac dodatkowe darmowe uslugi, lecz nie stanowia automatycznej gwarancji darmowosci `larger runners`, uslug platnych, nadmiarowego storage ani limitow innych repozytoriow. Rozliczenie darmowego CI wynika tutaj przede wszystkim z PUBLICZNEGO statusu repozytorium. Zero-cost nie upowaznia do wydatkow.

W tym repozytorium `research-pr-validation.yml` i `pages.yml` korzystaja ze standardowego `ubuntu-latest`. `offline-tests.yml` i `docs-check.yml` sa zastrzezone do recznego uruchamiania na zaufanym runnerze self-hosted dla `main`. Nie otwieraj stalego runnera na kod niezaufanego PR. Preferuj izolowane standardowe runnery dla CI PR, exact SHA, krotkie timeouty i `concurrency` z anulowaniem starszych przebiegow. Zasady finansowania APC przez uczelnie sa zapisane w planie i nie autoryzuja platnosci ani wyslania manuskryptu.

Zrodla: https://docs.github.com/en/actions/concepts/billing-and-usage ; https://docs.github.com/en/actions/reference/runners/github-hosted-runners ; https://docs.github.com/en/billing/concepts/product-billing/github-actions .
