# Dokument wymagań produktu (PRD) - FindMail
## 1. Przegląd produktu

FindMail to webowy klient pocztowy dla domeny `@findmail.pl`, umożliwiający rejestrację z kluczem zaproszenia, logowanie, tworzenie i przeglądanie dowolnych skrzynek pocztowych w domenie oraz podstawowe operacje na wiadomościach (listowanie, podgląd, usuwanie). Aplikacja w wersji MVP wspiera wyłącznie przeglądarkę Chrome, korzysta z polling co 60 s oraz ręcznego odświeżania, a konfiguracja SMTP odbywa się przez plik konfiguracyjny.

## 2. Problem użytkownika

Użytkownicy potrzebują prostego i szybkiego dostępu do wiadomości w domenie `@findmail.pl` bez konieczności konfiguracji klienta pocztowego. Oczekują natychmiastowego podglądu nowych wiadomości, możliwości zarządzania skrzynkami i bezpiecznego usuwania treści.

## 3. Wymagania funkcjonalne

1. Zarządzanie kluczami zaproszeń
   - Tabela `invitation_keys` z kolumnami `id`, `klucz`
   - Klucze dodawane ręcznie, usuwane jednorazowo po użyciu

2. Rejestracja i logowanie
   - Rejestracja: e-mail, hasło, klucz zaproszenia; 
   - Logowanie: e-mail, hasło

3. Generowanie i przeglądanie skrzynki
   - Możliwość wpisania dowolnej nazwy skrzynki (max 20 znaków, dozwolone znaki nazwy e-mail)
   - Skrzynki współdzielone, dostępne dla wszystkich użytkowników

4. Lista wiadomości
   - Tabela z kolumnami: Data, Nadawca, Temat
   - Automatyczne zaznaczenie najnowszej wiadomości
   - Polling co 60 s oraz przycisk „Odśwież”  

5. Podgląd wiadomości
   - Renderowanie plików TXT i HTML w `iframe` z atrybutem `sandbox`
   - Usunięcie tagów `<script>` przed renderowaniem

6. Usuwanie wiadomości
   - Modal z potwierdzeniem
   - Trwałe usunięcie bez możliwości przywrócenia

7. Konfiguracja SMTP
   - Parametry host, port, TLS w pliku konfiguracyjnym
   - Zewnętrzna usługa SMTP

8. Obsługa błędów
   - Centralny handler w UI, komunikat „Coś poszło nie tak, spróbuj ponownie”

9. Wymagania techniczne
   - Obsługa tylko w przeglądarce Chrome
   - Brak weryfikacji e-mail, brak zaawansowanej złożoności hasła, brak limitowania

## 4. Granice produktu

- Brak obsługi załączników
- Brak aplikacji mobilnych
- Brak weryfikacji adresów e-mail
- Brak monitoringu i limitowania zapytań
- Brak dokumentacji użytkownika i zaawansowanych metryk
- KPI przyjęte, ale nie mierzone w MVP

## 5. Historyjki użytkowników

US-001  
Tytuł: Rejestracja z kluczem zaproszenia  
Opis: Nowy użytkownik rejestruje się w systemie, podając e-mail, hasło oraz klucz zaproszenia.  
Kryteria akceptacji:  
- Formularz waliduje obecność i poprawność klucza  
- Po poprawnym zapisie klucz jest usuwany z bazy  
- Użytkownik otrzymuje potwierdzenie rejestracji  
- W przypadku nieprawidłowego klucza wyświetlany jest komunikat „Nieprawidłowy klucz zaproszenia”

US-002  
Tytuł: Logowanie  
Opis: Zarejestrowany użytkownik loguje się przy użyciu e-mail i hasła.  
Kryteria akceptacji:  
- Formularz waliduje zgodność danych z bazą  
- Po poprawnym zalogowaniu użytkownik jest przekierowany do dashboardu  
- W przypadku błędnych danych wyświetlany jest komunikat „Nieprawidłowy e-mail lub hasło”

US-003  
Tytuł: Dostęp do skrzynki pocztowej  
Opis: Użytkownik wpisuje nazwę skrzynki (max 20 znaków) i uzyskuje dostęp do jej zawartości.  
Kryteria akceptacji:  
- Nazwa skrzynki jest walidowana pod kątem długości i dozwolonych znaków  
- Po zatwierdzeniu wyświetlana jest lista maili (Data, Nadawca, Temat)  
- W przypadku nieistniejącej skrzynki wyświetlany jest komunikat „Brak wiadomości”

US-004  
Tytuł: Automatyczne odświeżanie listy maili  
Opis: Lista maili jest odświeżana co 60 sekund bez interakcji użytkownika.  
Kryteria akceptacji:  
- Polling co 60 s pobiera nowe dane z serwera  
- Najnowsza wiadomość jest zaznaczana automatycznie  
- W przypadku błędu odświeżania wyświetlany jest komunikat „Coś poszło nie tak...” 

US-005  
Tytuł: Ręczne odświeżanie listy maili  
Opis: Użytkownik może wcisnąć przycisk „Odśwież”, aby pobrać najnowsze maile.  
Kryteria akceptacji:  
- Kliknięcie przycisku wywołuje natychmiastowe pobranie danych  
- Pulsujący stan ładowania podczas oczekiwania  
- Obsługa błędów analogiczna do polling

US-006  
Tytuł: Podgląd wiadomości  
Opis: Użytkownik klika w mail, aby zobaczyć jego treść w `iframe` z `sandbox`.  
Kryteria akceptacji:  
- Treść HTML/TXT jest renderowana bez skryptów  
- `iframe` ma atrybuty `sandbox` bez `allow-scripts`  
- W przypadku nieobsługiwanego formatu wyświetlany jest komunikat „Nieobsługiwany format pliku”

US-007  
Tytuł: Usuwanie wiadomości  
Opis: Użytkownik inicjuje usunięcie maila, potwierdza w modalu i mail jest trwale usuwany.  
Kryteria akceptacji:  
- Modal wymaga potwierdzenia  
- Po potwierdzeniu mail znika z widoku i bazy danych  
- W przypadku anulowania nic się nie zmienia

US-008  
Tytuł: Bezpieczne uwierzytelnianie i autoryzacja  
Opis: System zapewnia dostęp do zasobów tylko zalogowanym użytkownikom.  
Kryteria akceptacji:  
- Nieautoryzowany użytkownik jest przekierowywany do strony logowania  
- Sesja wygasa po określonym czasie bez aktywności (konfiguracja backend)  
- Próba odczytu zasobu bez tokena zwraca błąd 401

US-009  
Tytuł: Generowanie losowego adresu  
Opis: Użytkownik może wygenerować unikalny, losowy adres z domeną `@findmail.pl`.  
Kryteria akceptacji:  
- Adres jest generowany wg wzoru `[losowy ciąg]@findmail.pl`  
- Adres jest wyświetlany użytkownikowi i zapisywany jako możliwa skrzynka  
- Adres nie zawiera niedozwolonych znaków i ma max 20 znaków przed @

US-010  
Tytuł: Obsługa błędów w UI  
Opis: W przypadku awarii backendu UI wyświetla centralny komunikat o błędzie.  
Kryteria akceptacji:  
- Każdy nieobsłużony wyjątek w UI pokazuje komunikat „Coś poszło nie tak, spróbuj ponownie”  
- Błędy sieciowe i serwerowe są łapane i przekazywane do centralnego handlera

## 6. Metryki sukcesu

1. 80% maili wyświetla się w interfejsie użytkownika w ciągu 5 sekund od momentu wysłania  
2. Aplikacja działa w przeglądarce Chrome bez krytycznych błędów  
3. Czas od kliknięcia „Odśwież” do pełnego załadowania listy maili mieści się w akceptowalnych granicach podczas testu manualnego 