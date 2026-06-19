🌐 [English](README.md) | [Français](README.fr.md) | [Deutsch](README.de.md)

# chirp-atc
CHIRP-Dateien für ATC-Frequenzen

Dieses Repository generiert CHIRP-Speicherdateien zum Laden in Ihr Quansheng-Funkgerät.


<p align="center">
  <img src="img/qs.jpg" />
</p>


# Inhaltsverzeichnis

- [Generierte CSVs](#generierte-csvs)
    - [Gebiets-Tabelle](#gebiets-tabelle)
- [get_frequencies.py](#get_frequenciespy)
    - [Funktionen](#funktionen)
    - [Installation](#installation)
    - [Verwendung](#verwendung)
        - [Kommandozeilen-Argumente](#kommandozeilen-argumente)
    - [Anwendungsbeispiele](#anwendungsbeispiele)
    - [Datenherkunft](#datenherkunft)
    - [Lizenz](#lizenz)

# Generierte CSVs

Die generierten CSVs sind im „Releases"-Tab dieses Repositories verfügbar. Die Dateien werden einmal täglich generiert.

Es gibt einen Satz pro Land und einen Satz pro spezifischem Gebiet (siehe [unten](#gebiets-tabelle)).

Für weitere CSVs erstellen Sie bitte einen Pull-Request oder eröffnen Sie ein Issue.

## Gebiets-Tabelle

Da ältere Quansheng-Funkgeräte nur etwa 200 Frequenzen im Speicher verwalten können, habe ich kleinere, gebietsspezifische Listen erstellt.

Die folgende Tabelle zeigt die aktuell generierten gebietsspezifischen CSVs:

| Land         | Gebietsname             | Postleitzahl | Radius (km) | Referenzstadt   |
|--------------|-------------------------|--------------|-------------|-----------------|
| Schweiz      | Geneva-Leman            | 1200         | 50          | Genf            |
| Schweiz      | Lausanne-Vaud           | 1000         | 50          | Lausanne        |
| Schweiz      | Fribourg-Gruyère        | 1700         | 50          | Freiburg        |
| Schweiz      | Neuchatel-Jura          | 2000         | 50          | Neuenburg       |
| Schweiz      | Bern-Capital            | 3000         | 50          | Bern            |
| Schweiz      | Basel-North             | 4000         | 50          | Basel           |
| Schweiz      | Valais-Mountains        | 1950         | 50          | Sitten          |
| Schweiz      | Lucerne-Central         | 6000         | 50          | Luzern          |
| Schweiz      | Zurich-Metropolis       | 8001         | 50          | Zürich          |
| Schweiz      | Ticino-South            | 6900         | 50          | Lugano          |
| Frankreich   | Île-de-France           | 45000        | 150         | Orléans         |
| Frankreich   | Normandie-Bretagne Est  | 50000        | 150         | Saint-Lô        |
| Frankreich   | Bretagne Ouest          | 29000        | 150         | Quimper         |
| Frankreich   | Pays de la Loire        | 49000        | 150         | Angers          |
| Frankreich   | Poitou-Charentes        | 86000        | 150         | Poitiers        |
| Frankreich   | Bordeaux-Aquitaine      | 33000        | 150         | Bordeaux        |
| Frankreich   | Midi-Pyrénées           | 31000        | 150         | Toulouse        |
| Frankreich   | Languedoc-Roussillon    | 34000        | 150         | Montpellier     |
| Frankreich   | Provence-Alpes-Côte d'Azur | 13000     | 150         | Marseille       |
| Frankreich   | Rhône-Alpes             | 69000        | 150         | Lyon            |
| Frankreich   | Bourgogne-Franche-Comté | 21000        | 150         | Dijon           |
| Frankreich   | Grand Est Ouest         | 54000        | 150         | Nancy           |
| Frankreich   | Grand Est Est           | 67000        | 150         | Straßburg       |
| Frankreich   | Hauts-de-France Ouest   | 80000        | 150         | Amiens          |
| Frankreich   | Hauts-de-France Est     | 59000        | 150         | Lille           |
| Großbritannien | London and South East | EC1A         | 150         | London          |
| Großbritannien | Midlands              | B1           | 150         | Birmingham      |
| Großbritannien | North West England    | M1           | 150         | Manchester      |
| Großbritannien | Yorkshire and Humber  | LS1          | 150         | Leeds           |
| Großbritannien | North East England    | NE1          | 150         | Newcastle upon Tyne |
| Großbritannien | South West England    | BS1          | 150         | Bristol         |
| Großbritannien | Wales                 | CF10         | 150         | Cardiff         |
| Großbritannien | Scotland Central Belt | G1           | 150         | Glasgow         |
| Großbritannien | Scotland North        | AB10         | 150         | Aberdeen        |
| Belgien       | Belgium               | 1000         | 100         | Brüssel         |

# get_frequencies.py

`get_frequencies.py` ist ein Kommandozeilen-Tool (CLI) zum Extrahieren von ATC-Frequenzen aus OpenAIP.

## Funktionen

- Extrahiert ATC-Frequenzen aus OpenAIP basierend auf Land oder Region.
- Ermöglicht Filterung nach Frequenztyp (Flughäfen, Lufträume).
- Unterstützt die Angabe einer Postleitzahl und eines Radius für ein gezieltes geografisches Gebiet.
- Gibt Daten im Format `CHIRP-CSV` oder `Console-JSON` aus.
- Unterstützt einen Debug-Modus zur Fehlersuche.

## Installation

Um `get_frequencies.py` zu verwenden, stellen Sie sicher, dass Python 3.x auf Ihrem System installiert ist. Folgen Sie dann den untenstehenden Schritten:

1. Repository klonen:

    ```bash
    git clone https://github.com/diaznet/chirp-atc.git
    cd chirp-atc
    git checkout
    ```

2. Abhängigkeiten installieren:

    ```bash
    pip install -r requirements.txt
    ```

3. Skript ausführen:

    ```bash
    python get_frequencies.py
    ```

## Verwendung

Sie können das Skript mit folgendem Befehl ausführen:

```bash
python get_frequencies.py -h
```

Dies zeigt die verfügbaren Optionen an:

```bash
usage: get_frequencies.py [-h] -c COUNTRY [COUNTRY ...] [-t TYPE [TYPE ...]] [-p POSTAL_CODE [POSTAL_CODE ...]] [-r RADIUS]
                          [-o {CHIRP-CSV,Console-JSON}] [-s SUFFIX] [-d]

Get frequencies for a specific country from openAIP.

options:
  -h, --help            show this help message and exit
  -c COUNTRY [COUNTRY ...], --country COUNTRY [COUNTRY ...]
                        ISO alpha-2 country codes.
  -t TYPE [TYPE ...], --type TYPE [TYPE ...]
                        Types of frequencies. Supported values are 'airports', 'airspaces'. Defaults to all.
  -p POSTAL_CODE [POSTAL_CODE ...], --postal-code POSTAL_CODE [POSTAL_CODE ...]
                        Postal code, to narrow down the output to a specific area.
  -r RADIUS, --radius RADIUS
                        Radius in kilometers around postal code, to narrow down the output to a specific area. Default is ().
  -o {CHIRP-CSV,Console-JSON}, --output {CHIRP-CSV,Console-JSON}
                        Output type. Default is Console-JSON.
  -s SUFFIX, --suffix SUFFIX
                        When writing a file, append the specified string to the filename.
  -d, --debug           Enable debug on STDERR.
```

### Kommandozeilen-Argumente

- `-c COUNTRY [COUNTRY ...], --country COUNTRY [COUNTRY ...]`: Geben Sie einen oder mehrere ISO-Alpha-2-Ländercodes an (z. B. `CH`, `DE`).
- `-t TYPE [TYPE ...], --type TYPE [TYPE ...]`: Geben Sie den Frequenztyp an. Optionen:
  - `airports`
  - `airspaces`
  - Standard: alle.
- `-p POSTAL_CODE [POSTAL_CODE ...], --postal-code POSTAL_CODE [POSTAL_CODE ...]`: Ergebnisse durch Angabe einer Postleitzahl eingrenzen.
- `-r RADIUS, --radius RADIUS`: Radius (in Kilometern) um eine Postleitzahl angeben. Standard: kein Radius.
- `-o {CHIRP-CSV,Console-JSON}, --output {CHIRP-CSV,Console-JSON}`: Ausgabeformat wählen. Standard: `Console-JSON`.
- `-s SUFFIX, --suffix SUFFIX`: Suffix an den Ausgabedateinamen anhängen.
- `-d, --debug`: Debug-Modus aktivieren (Ausgabe auf STDERR).

## Anwendungsbeispiele

1. **Frequenzen für die Schweiz (CH) abrufen:**

    ```bash
    python get_frequencies.py -c CH
    ```

2. **Flughafen-Frequenzen für Frankreich (FR) und Deutschland (DE) abrufen:**

    ```bash
    python get_frequencies.py -c FR DE -t airports
    ```

3. **Frequenzen im Umkreis von 50 km um eine Postleitzahl abrufen (z. B. 8001 in Zürich):**

    ```bash
    python get_frequencies.py -c CH -p 8001 -r 50
    ```

4. **Frequenzen im CSV-Format exportieren:**

    ```bash
    python get_frequencies.py -c CH -o CHIRP-CSV
    ```

## 8,33-kHz-Kanalabstand

Das europäische Flugfunkband verwendet einen Kanalabstand von 8,33 kHz. Die in den AIPs veröffentlichten Frequenzen sind **Kanalbezeichner**, keine tatsächlichen HF-Frequenzen. Dieses Tool konvertiert Kanalbezeichner in tatsächliche Mittenfrequenzen gemäß ICAO Doc 9718.

Referenzen:
- [ICAO Doc 9718 Vol II - Frequenz-/Kanal-Zuweisungstabelle](https://www.icao.int/sites/default/files/FSMP/Doc.9718-Vol-II_Supplement_30June2017.pdf)
- [Ofcom - Understanding 8.33kHz frequencies and their specific channel number](https://www.ofcom.org.uk/siteassets/resources/documents/manage-your-licence/aeronautical/guidance/understanding-8.33khz-frequencies-and-their-specific-channel-number.pdf?v=323879)

## Datenherkunft

Die von `get_frequencies.py` verwendeten Daten stammen von OpenAIP. Wenn Sie fehlerhafte Informationen finden (z. B. ungenaue Frequenzdaten oder Bezeichnungen), bitten wir Sie, ein Issue zu eröffnen oder es direkt an OpenAIP zu melden:

[OpenAIP RFC](https://www.openaip.net/)

Ihre Arbeit ist von unschätzbarem Wert, und wir schätzen ihren Beitrag zur Luftfahrt-Community.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert – siehe die [LICENSE](LICENSE)-Datei für Details.
