# AAP Brevanalyse

Her deler vi koden for analyse av AAP-brevene. 

## Jobb lokalt på egen maskin

Opprett et virtuelt miljø med venv.

```bash
python3.10 -m venv .venv
```

Start miljøet

```bash
source .venv/bin/activate
```

Installer pakker

```bash
make install
```

Oppdatér pakker

```bash
make update
```

Formater python-koden med black

```bash
make format
```