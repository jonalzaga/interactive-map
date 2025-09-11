#!/usr/bin/env python3
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "mountains_data.txt"

def main():
    print("=== New mountain entry ===")
    name = input("name: ").strip()
    if name.lower() == "exit":
        exit()  
        
    province = input("province: ").strip()
    latlon = input("lat,lon: ").strip()
    lat, lon = latlon.split(",")
    climbed = input("climbed: ").strip()
    climbed_date = input("climbed_date: ").strip()
    url = input("url: ").strip()
    challenge = input("challenge: ").strip()

    row = f"{name},{province},{lat},{lon},{climbed},{climbed_date},{url},{challenge}"
    DATA.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA, "a", encoding="utf-8") as f:
        f.write(row + "\n")
    print("Added:\n" + row)

if __name__ == "__main__":
    while True:
        main()
