# Generator Kodów QR (Statyczne & Dynamiczne)

Kompletne narzędzie do generowania kodów QR do druku na opakowaniach zbiorczych, kartonach i etykietach.

## Funkcje:
- **Kody Statyczne:** Bezpośrednie zakodowanie adresu URL.
- **Kody Dynamiczne:** Stały adres URL przekierowujący na właściwy plik PDF. Możliwość podmiany linku do instrukcji bez zmiany nadruku na opakowaniu.
- **Wektorowy format SVG:** Gotowe pliki dla grafików / drukarni z poziomem korekcji błędów `H` (30% odporności na zniszczenia/zagięcia).
- **Trwała baza JSON:** Rejestr wszystkich skrótów dynamicznych zapisywany w pliku `routes.json`.

## Uruchomienie (Krok po kroku):

1. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```

2. Uruchom aplikację:
   ```bash
   python app.py
   ```

3. Otwórz w przeglądarce adres:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)
