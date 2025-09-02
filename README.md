# Hiking Map: Gipuzkoa & Navarra

Interactive map with provincial polygons and peaks (green = climbed, red = pending).
**Demo**: enable GitHub Pages (branch `main`, folder `/docs`) and open:
`https://<your_username>.github.io/hiking-map/hiking_map.html`.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/build_map.py
# => docs/hiking_map.html
