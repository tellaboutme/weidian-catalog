#!/usr/bin/env python3
"""Download every product of a Weidian shop to CSV (and JSON).

Usage:
  weidian <shopId | shop URL | item URL> [more ...] [-o DIR] [--no-json]

Examples:
  weidian 1350023534
  weidian "https://shop1350023534.v.weidian.com/?userid=1350023534"
  weidian "https://weidian.com/item.html?itemID=4722160010"
"""
import argparse, csv, datetime, json, os, re, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
API = "https://thor.weidian.com"
FIELDS = ["productId", "shopId", "createdAt", "name", "comment", "price_cny", "sold",
          "stock", "hasSku", "isPreSale", "tags", "thumbnail", "url"]


def call(path, param):
    url = f"{API}/{path}?" + urllib.parse.urlencode(
        {"param": json.dumps(param, separators=(",", ":")), "wdtoken": ""})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://weidian.com/"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # network hiccup / rate limit
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def shop_from_item(item_id):
    # the item page HTML links back to the seller as ...userid=<shopId>
    req = urllib.request.Request(f"https://weidian.com/item.html?itemID={item_id}",
                                 headers={"User-Agent": UA})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r'userid=(\d{5,})|"(?:shopId|sellerId|userId)"\s*:\s*"?(\d{5,})', page)
    if not m:
        sys.exit(f"не удалось найти магазин для товара {item_id}")
    return m.group(1) or m.group(2)


def resolve(arg):
    arg = arg.strip()
    if arg.isdigit():
        return arg
    m = re.search(r"[?&]itemI[dD]=(\d+)", arg)
    if m:
        return shop_from_item(m.group(1))
    for pat in (r"[?&]userid=(\d+)", r"shop(\d+)\.v\.weidian", r"weidian\.com/s/(\d+)"):
        m = re.search(pat, arg, re.I)
        if m:
            return m.group(1)
    sys.exit(f"не понял, что это за магазин: {arg}")


def scrape(shop):
    rows, seen, off = [], set(), 0
    while True:
        d = call("decorate/shopDetail.tab.getItemList/1.0",
                 {"shopId": shop, "tabId": 0, "sortOrder": "desc", "offset": off,
                  "limit": 50, "from": "h5", "showItemTag": True})
        if (d.get("status") or {}).get("code") not in (0, None):
            if rows:  # past the last page Weidian answers 参数错误 instead of an empty list
                break
            sys.exit(f"Weidian вернул ошибку: {d.get('status')}")
        items = (d.get("result") or {}).get("itemList") or []
        new = [i for i in items if i["itemId"] not in seen]
        if not new:
            break
        for i in new:
            seen.add(i["itemId"])
            tags = [t.get("tagName", "") if isinstance(t, dict) else str(t) for t in (i.get("itemTag") or [])]
            rows.append({
                "productId": i["itemId"], "shopId": shop,
                "createdAt": datetime.datetime.fromtimestamp(i["addTime"] / 1000).strftime("%Y-%m-%d") if i.get("addTime") else "",
                "name": i.get("itemName") or "", "comment": i.get("itemComment") or "",
                "price_cny": i.get("price"), "sold": i.get("sold") or 0, "stock": i.get("stock"),
                "hasSku": i.get("hasSku"), "isPreSale": i.get("preSale"), "tags": "|".join(filter(None, tags)),
                "thumbnail": i.get("itemImg") or "", "url": i.get("itemUrl") or f"https://weidian.com/item.html?itemID={i['itemId']}",
            })
        off += len(items)
        print(f"\r  {shop}: {len(rows)} товаров…", end="", file=sys.stderr, flush=True)
        time.sleep(0.4)
    print(file=sys.stderr)
    return rows


def main():
    ap = argparse.ArgumentParser(prog="weidian", description="Выгрузка всех товаров магазина Weidian в CSV")
    ap.add_argument("shops", nargs="+", help="ID магазина (userid), ссылка на магазин или на товар")
    ap.add_argument("-o", "--out", default=os.environ.get("WEIDIAN_DIR", os.path.expanduser("~/weidian")),
                    help="папка для файлов (по умолчанию ~/weidian или $WEIDIAN_DIR)")
    ap.add_argument("--no-json", action="store_true", help="не сохранять JSON рядом с CSV")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for arg in a.shops:
        shop = resolve(arg)
        rows = scrape(shop)
        if not rows:
            print(f"  {shop}: товаров нет (или магазин не существует)", file=sys.stderr)
            continue
        base = os.path.join(a.out, f"weidian_{shop}")
        with open(base + ".csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        if not a.no_json:
            with open(base + ".json", "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f"{base}.csv  ({len(rows)} товаров)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
