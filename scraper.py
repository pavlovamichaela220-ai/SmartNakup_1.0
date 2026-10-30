import re
from playwright.sync_api import sync_playwright

SHOPS = [
    "Globus", "Tesco", "Lidl", "Kaufland", "Albert", 
    "BILLA", "Penny", "COOP", "TERNO", "FLOP", "Košík.cz", "Rohlik.cz"
]

def search_shopping_list(items):
    results = []
    total = 0.0

    with sync_playwright() as p:
        # Spustíme prohlížeč jednou pro celý seznam
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for item in items:
            product_clean = item.lower().strip()
            url = f"https://www.kupi.cz/hledej?f={product_clean.replace(' ', '+')}"
            
            print(f"Hledám na Kupi: {product_clean}")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
                # Počkáme na načtení výsledků vyhledávání nebo slevových karet
                page.wait_for_selector(".discounts_list, .group_discounts, .no_results", timeout=5000)
            except Exception:
                pass

            cheapest = None

            # Vyhledáme všechny slevové karty na stránce
            cards = page.locator(".discount_row, .group_item, .discounts_list .item").all()

            for card in cards:
                try:
                    card_text = card.inner_text()
                    
                    # 1. Extrakce ceny z karty
                    price_match = re.search(r"(\d+[\s,.]?\d*)\s*Kč", card_text)
                    if not price_match:
                        continue
                    
                    price_str = price_match.group(1).replace(" ", "").replace(",", ".")
                    price = float(price_str)

                    # 2. Určení obchodu z textu karty nebo alt/title obrázku
                    shop = "Akce Supermarket"
                    for s in SHOPS:
                        if s.lower() in card_text.lower():
                            shop = s
                            break

                    # 3. Určení platnosti akce
                    valid_match = re.search(r"platí do\s*([0-9.]+|dnes|zítra)", card_text, re.IGNORECASE)
                    valid_until = f"Platí do {valid_match.group(1)}" if valid_match else "Neuvedeno"

                    offer = {
                        "product": product_clean,
                        "shop": shop,
                        "price": price,
                        "valid_until": valid_until,
                        "url": url
                    }

                    # Uložíme nejlevnější nalezenou nabídku pro daný produkt
                    if cheapest is None or price < cheapest["price"]:
                        cheapest = offer

                except Exception:
                    continue

            # Záložní varianta: Pokud CSS selektor nezabral, vezmeme první cenu z textu stránky
            if not cheapest:
                try:
                    full_text = page.locator("body").inner_text()
                    match = re.search(r"(\d+,\d+)\s*Kč", full_text)
                    if match:
                        price = float(match.group(1).replace(",", "."))
                        cheapest = {
                            "product": product_clean,
                            "shop": "Kupi.cz",
                            "price": price,
                            "valid_until": "Neuvedeno",
                            "url": url
                        }
                except Exception:
                    pass

            if cheapest:
                results.append(cheapest)
                total += cheapest["price"]
            else:
                print(f"⚠️ Pro '{product_clean}' se nepodařilo najít žádnou cenu.")

        browser.close()

    return {
        "items": results,
        "total": round(total, 2)
    }


def get_prices(items):
    """Metoda určená pro volání z app.py"""
    res = search_shopping_list(items)
    return res["items"], res["total"]


if __name__ == "__main__":
    shopping_list = [
        "mleko",
        "eidam 30",
        "gouda",
        "jahody",
        "olivovy olej"
    ]

    result = search_shopping_list(shopping_list)

    print("\n" + "=" * 50)
    print("NAKUPNI SEZNAM (REÁLNÉ CENY Z KUPI)")
    print("=" * 50)

    for item in result["items"]:
        print(
            f"{item['product'].capitalize()} | "
            f"{item['shop']} | "
            f"{item['price']} Kč | "
            f"{item['valid_until']}"
        )

    print("=" * 50)
    print(f"CELKEM: {result['total']} Kč")