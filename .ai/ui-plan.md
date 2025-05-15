# Architektura UI dla FindMail
Frontend - Boostrap / html / flask
- Bootstrap 5 (CDN) + Jinja2 (Flask templating)
- Dla polling co 60s proste odświeżanie w JS
- Osobny plik CSS do custom-owego stylowania
- Blueprints Flask + tagi Jinja2 do przekazywania danych z BE


## 1. Przegląd struktury UI

FindMail to jednostronicowa aplikacja (SPA) zoptymalizowana pod Chrome, podzielona na kilka głównych sekcji:
- **Ekran autoryzacji** (Rejestracja / Logowanie)
- **Dashboard** z headerem i panelem głównym:
  - **Panel wyboru skrzynki** (wejście nazwy + generowanie losowego)
  - **Lista wiadomości** (polling co 60 s + przycisk „Odśwież”)
  - **Podgląd wiadomości** (modal/iframe z sandbox)
- **Globalny handler błędów** (stały pasek powiadomień)
- **Modal potwierdzenia usunięcia**

Całość nawigowana przez stan aplikacji i prosty pasek breadcrumb w headerze.

## 2. Lista widoków

### 2.1. Ekran Rejestracji / Logowania
- **Ścieżka**: `/auth`
- **Cel**: Umożliwić nowym użytkownikom rejestrację z kluczem zaproszenia oraz zalogowanie.
- **Kluczowe informacje**:
  - Formularz rejestracji: e-mail, hasło, klucz zaproszenia
  - Formularz logowania: e-mail, hasło
- **Kluczowe komponenty**:
  - Pola formularza z walidacją długości/formatu
  - Przełącznik między zakładkami Rejestracja/Logowanie
  - Komponent alertów do komunikatów o błędach („Nieprawidłowy klucz…”, „Nieprawidłowy e-mail…”)
- **UX / dostępność / bezpieczeństwo**:
  - Wyraźne etykiety i aria-attributes
  - Ukrywanie hasła z opcją podglądu
  - CSRF token w żądaniu
  - Bieżąca walidacja klienta przed wysłaniem

### 2.2. Dashboard – wybór skrzynki
- **Ścieżka**: `/mailbox`
- **Cel**: Pozwolić użytkownikowi wybrać lub wygenerować skrzynkę.
- **Kluczowe informacje**:
  - Pole tekstowe nazwy (1–20 znaków, regex dozwolonych)
  - Przycisk „Generuj losowy”
  - Komunikat walidacyjny („Za długa nazwa”, „Brak dostępu”)
- **Komponenty**:
  - Input z ograniczeniem length i pattern
  - Przycisk generate
  - Spinner/loading przy generowaniu
- **UX / dostępność / bezpieczeństwo**:
  - aria-invalid i aria-describedby dla walidacji
  - Obsługa błędów 409 (konflikt nazwy)
  - Automatyczne focusowanie na polu

### 2.3. Lista wiadomości
- **Ścieżka**: `/mailbox/:name/messages`
- **Cel**: Wyświetlić paginowaną listę maili wraz z meta: data, nadawca, temat.
- **Kluczowe informacje**:
  - Tabela (Data | Nadawca | Temat)
  - Oznaczenie najnowszej wiadomości
  - Czas ostatniego odświeżenia
- **Komponenty**:
  - Tabela responsywna Bootstrap
  - Spinner/loading dla polling i „Odśwież”
  - Nagłówek kolumn z domyślnym sortowaniem
  - Nie robimy Paginacji (wyswietlane jest max 10 wiadomosci)
- **UX / dostępność / bezpieczeństwo**:
  - aria-live dla automatycznego odświeżania
  - Odświeżanie co 60 s + retry przy błędach sieciowych
  - Błąd sieciowy → stały banner „Coś poszło nie tak…”

### 2.4. Podgląd wiadomości (modal)
- **Cel**: Bezpieczne renderowanie treści maila.
- **Kluczowe informacje**:
  - Treść HTML/TXT w `<iframe sandbox>`
  - Meta: nadawca, data, temat
- **Komponenty**:
  - Modal Bootstrap z headerem/meta i body=iframe
  - Funkcja stripowania `<script>`
- **UX / dostępność / bezpieczeństwo**:
  - `allow-same-origin` bez `allow-scripts`
  - aria-modal, role=dialog, focus trap
  - Fallback „Nieobsługiwany format”

### 2.5. Potwierdzenie usunięcia (modal)
- **Cel**: Zabezpieczyć przed przypadkowym usunięciem.
- **Kluczowe informacje**:
  - Tekst potwierdzenia
  - Przycisk „Usuń” (red) i „Anuluj”
- **Komponenty**:
  - Modal Bootstrap
- **UX / dostępność / bezpieczeństwo**:
  - aria-modal, focus trap
  - 204 No Content → usunięcie z widoku + polling

### 2.6. Globalny banner błędów
- **Cel**: Wyświetlać centralny komunikat o błędach API.
- **Komponenty**:
  - Sticky banner na górze
  - Znikający po 5 s lub po zamknięciu
- **UX / dostępność / bezpieczeństwo**:
  - aria-live=assertive
  - Logowanie błędów klienta

## 3. Mapa podróży użytkownika

1. **Wejście** → `/auth`
2. **Rejestracja** lub **Logowanie**  
   • Po sukcesie → redirect `/mailbox`
3. **Wybór skrzynki**  
   • Wpisanie nazwy lub losowe → GET `/api/mailboxes/{name}` → redirect `/mailbox/:name/messages`
4. **Przegląd listy maili**  
   • Polling co 60 s, manualne odświeżenie  
   • Kliknięcie w wiersz → otwarcie modala podglądu
5. **Podgląd maila**  
   • Zamknięcie → powrót do listy  
6. **Usuwanie**  
   • Klik „Usuń” → modal potwierdzenia → potwierdź → DELETE i odśwież listę
7. **Wylogowanie** (opcjonalny przycisk w headerze)

## 4. Układ i struktura nawigacji

- **Header** (widoczny po auth):
  - Logo „FindMail”
  - Nazwa aktywnej skrzynki + breadcrumb
  - Przycisk Wyloguj
- **Sidebar** (opcjonalnie, jeśli przyszłe rozszerzenia):
  - Link do dashboardu
  - (Placeholder na przyszłe funkcje)
- **Główny panel**:
  - Wstawia aktualny widok (lista, podgląd, formy)

## 5. Kluczowe komponenty

- **FormField** – etykieta + input + error message (aria-attributes)
- **Button** – stan normal/loading/disabled
- **Table** – obsługa paginacji i aria-live
- **Modal** – generyczny wrapper z focus trap
- **IframeViewer** – iframe + sanitization
- **Banner** – globalny komunikat błędu
- **Spinner** – dla operacji asynchronicznych

