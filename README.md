# What it is
Very simple to script export your [sens-critique](https://senscritique.com/) collection (history and watch list) to csv files.
I used to import it on my [letterboxd account](https://letterboxd.com/mattchete) but it can be used elsewhere.

# Init
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Config
- Log into [sens-critique](https://senscritique.com/)
- Find an ajax request on `https://apollo.senscritique.com/`
- Get the `Authorization` header value
- Put it in the `.env` file in this format:
```env
SENSCRITIQUE_AUTHORIZATION_KEY=THE_AUTH_KEY
```

# Run
## Activate the venv
```bash
source .venv/bin/activate
```

## Run the script
```bash
python sc-collection-exporter.py
```

## Enjoy
Two csv files will be written:
- `sc_to_lbxd_seen.csv` : your watch history (rated by you)
- `sc_to_lbxd_watchlist.csv` : your watch list

