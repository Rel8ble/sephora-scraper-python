"""Sephora product data with Python: run the Sephora Products Scraper on Apify,
save every product to CSV and print a ranked shortlist.

Usage:
  python example.py --token <YOUR_APIFY_TOKEN> --category mascara --max 100
  python example.py --token <YOUR_APIFY_TOKEN> --search "vitamin c serum" --country ca
  python example.py --from-json sample.json        # offline, no token needed
"""
import argparse
import csv
import json
import statistics
from collections import Counter

FIELDS = ["productId", "brand", "name", "price", "priceMax", "regularPrice", "salePrice",
          "isOnSale", "currency", "rating", "reviews", "variantsCount", "isNew",
          "isBestseller", "isSephoraExclusive", "url"]


def fetch(args):
    from apify_client import ApifyClient
    client = ApifyClient(args.token)
    run_input = {"maxItemsPerQuery": args.max, "country": args.country, "sortBy": args.sort}
    if args.search:
        run_input["searchQueries"] = args.search
    if args.category:
        run_input["categories"] = args.category
    if args.brand:
        run_input["brands"] = args.brand
    if args.on_sale:
        run_input["onSaleOnly"] = True
    run = client.actor("rel8ble/sephora-products-scraper").call(run_input=run_input)
    return list(client.dataset(run["defaultDatasetId"]).iterate_items())


def weighted_rating(rating, reviews, prior_mean, prior_weight=500):
    """Rating pulled toward the average until a product has enough reviews,
    so a 5.0 with 4 reviews does not outrank a 4.6 with 3,000."""
    return (rating * reviews + prior_mean * prior_weight) / (reviews + prior_weight)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token")
    ap.add_argument("--search", action="append")
    ap.add_argument("--category", action="append")
    ap.add_argument("--brand", action="append")
    ap.add_argument("--country", default="us", choices=["us", "ca"])
    ap.add_argument("--sort", default="bestSelling")
    ap.add_argument("--on-sale", action="store_true")
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--from-json")
    ap.add_argument("--out", default="sephora_products.csv")
    args = ap.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            items = json.load(f)
    else:
        if not args.token or not (args.search or args.category or args.brand):
            ap.error("give --token and at least one --search, --category or --brand (or use --from-json)")
        items = fetch(args)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(items)
    print(f"{len(items)} products -> {args.out}")

    rated = [p for p in items if p.get("rating") and p.get("reviews")]
    if not rated:
        return
    cur = items[0].get("currency", "")
    prices = [p["price"] for p in items if p.get("price") is not None]
    print(f"Price from {min(prices)} to {max(prices)} {cur}, median {statistics.median(prices)}")
    on_sale = [p for p in items if p.get("isOnSale")]
    print(f"On sale: {len(on_sale)} of {len(items)}")

    mean = sum(p["rating"] * p["reviews"] for p in rated) / sum(p["reviews"] for p in rated)
    for p in rated:
        p["_score"] = weighted_rating(p["rating"], p["reviews"], mean)
    print(f"\nTop rated after review-count weighting (average {mean:.2f}):")
    for p in sorted(rated, key=lambda p: p["_score"], reverse=True)[:5]:
        print(f"  {p['_score']:.2f}  {p['rating']:.2f} ({p['reviews']:,} reviews)  {p['price']} {cur}  {p['brand']} - {p['name']}")

    print("\nMost-reviewed under the median price:")
    cheap = [p for p in rated if p["price"] <= statistics.median(prices)]
    for p in sorted(cheap, key=lambda p: p["reviews"], reverse=True)[:5]:
        print(f"  {p['reviews']:>6,} reviews  {p['rating']:.2f}  {p['price']} {cur}  {p['brand']} - {p['name']}")

    print("\nBrands with the most products:")
    for brand, n in Counter(p["brand"] for p in items).most_common(5):
        print(f"  {n}  {brand}")


if __name__ == "__main__":
    main()
