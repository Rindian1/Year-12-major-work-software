import os
import sqlite3
import time
import requests

from ddgs import DDGS

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "instance",
    "cart.db",
)

CATEGORY_SUFFIX = {
    "Electric": "electric guitar",
    "Acoustic": "acoustic guitar",
    "Acoustic-Electric": "acoustic electric guitar",
    "Bass": "bass guitar",
    "Pedal": "guitar effects pedal",
    "Amplifier": "guitar amplifier",
    "Accessory": "",
    "Case": "guitar case",
    "guitars": "electric guitar",
    "amplifiers": "guitar amplifier",
    "effects": "guitar effects pedal",
    "accessories": "",
}


def get_all_products(db_path: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, name, category, image_url FROM products ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def image_file_exists(image_url: str) -> bool:
    relative = image_url.lstrip("/")
    full_path = os.path.normpath(
        os.path.join(os.path.dirname(DB_PATH), "..", relative)
    )
    return os.path.isfile(full_path)


def build_search_term(product_name: str, category: str) -> str:
    suffix = CATEGORY_SUFFIX.get(category, "")
    if suffix:
        return f"{product_name} {suffix}"
    return product_name


def download_first_image(search_term: str, save_path: str) -> bool:
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        results = list(DDGS().images(search_term, max_results=3))
        if not results:
            return False

        name_lower = search_term.lower()
        best_url = None
        for r in results:
            url = r.get("image")
            title = (r.get("title") or "").lower()
            src = (r.get("source") or "").lower()
            if not url:
                continue
            best_url = url
            if any(domain in url for domain in [".jpg", ".jpeg", ".png", ".webp"]):
                best_url = url
                break

        if not best_url:
            return False

        resp = requests.get(
            best_url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
        )
        if resp.status_code != 200:
            return False

        with open(save_path, "wb") as f:
            f.write(resp.content)
        return os.path.getsize(save_path) > 1000

    except Exception:
        return False


def main():
    products = get_all_products(DB_PATH)
    total = len(products)
    missing = [p for p in products if not image_file_exists(p["image_url"])]
    found_count = total - len(missing)

    print(f"Total products: {total}")
    print(f"Already have images: {found_count}")
    print(f"Missing images: {len(missing)}")
    print()

    if not missing:
        print("No missing images to fetch.")
        return

    success = 0
    fail = 0

    for i, p in enumerate(missing, 1):
        relative = p["image_url"].lstrip("/")
        save_path = os.path.normpath(
            os.path.join(os.path.dirname(DB_PATH), "..", relative)
        )
        search_term = build_search_term(p["name"], p["category"])

        print(f"  [{i}/{len(missing)}] {p['name']} ", end="", flush=True)
        ok = download_first_image(search_term, save_path)
        if ok:
            size = os.path.getsize(save_path)
            print(f"✓ ({size} bytes)")
            success += 1
        else:
            print(f"✗ No image found")
            fail += 1
        time.sleep(1.5)

    print()
    print(f"Done: {success} downloaded, {fail} failed")


if __name__ == "__main__":
    main()
