# Product Overview

## Purpose
Generate CHIRP-compatible CSV memory files for Quansheng radios containing ATC (Air Traffic Control) frequencies sourced from OpenAIP. Enables aviation enthusiasts to listen to EU airband communications.

## Key Features
- Extracts airport and airspace ATC frequencies from OpenAIP's public GCS bucket
- Converts 8.33 kHz channel designators to actual RF center frequencies per ICAO Doc 9718
- Filters by country (ISO alpha-2 codes), frequency type, postal code, and radius
- Outputs CHIRP-CSV format (ready to load into radio) or Console-JSON (for inspection)
- Automated daily/weekly CSV generation via GitHub Actions with release publishing
- Area-specific lists (≤200 frequencies) to fit Quansheng radio memory limits

## Target Users
- Aviation enthusiasts with Quansheng radios wanting to monitor ATC frequencies
- Pilots using handheld radios for situational awareness
- Users in Switzerland, France, Great Britain, and Belgium (currently supported areas)

## Value Proposition
Eliminates manual frequency lookup and entry — automatically produces radio-ready memory files with correct RF frequencies (not just channel designators) for the user's geographic area.
