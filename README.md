# Sephora Scraper Python - Sephora product, price, rating and shade data as JSON

Get Sephora US and Sephora Canada products by keyword, category, brand or product URL with Python, as clean JSON or CSV: brand, name, price and price range, sale price, rating, review count, number of shades / sizes, badges (new, bestseller, Sephora exclusive), image and URL. Turn on details for the description, ingredients, loves count, category path and every shade / size with its own price and stock flag.

This repo is a small, runnable example that calls the [Sephora Products Scraper](https://apify.com/rel8ble/sephora-products-scraper) actor on Apify with the official `apify-client`.

> I built this actor; it's a paid tool on Apify (pay per result; Apify gives new accounts free monthly credit).

## Quick start

```bash
pip install -r requirements.txt
python example.py --token <YOUR_APIFY_TOKEN> --category mascara --max 100
python example.py --token <YOUR_APIFY_TOKEN> --search "vitamin c serum" --country ca
python example.py --token <YOUR_APIFY_TOKEN> --brand the-ordinary --on-sale
python example.py --from-json sample.json   # offline, uses the real sample in this repo
```

`example.py` saves every product to `sephora_products.csv` and prints the price range, how many items are on sale, a top-rated list weighted by review count (so a 5.0 with 4 reviews does not beat a 4.6 with 3,000), the most-reviewed products under the median price, and the brands with the most products.

## Minimal Python

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")
run = client.actor("rel8ble/sephora-products-scraper").call(run_input={
    "categories": ["face-serum"],
    "sortBy": "bestSelling",
    "minRating": "4",
    "maxItemsPerQuery": 50,
})
for p in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(p["brand"], "|", p["name"], "|", p["price"], p["currency"], "|", p["rating"], p["reviews"])
```

## Node.js

```javascript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/sephora-products-scraper').call({
    brands: ['the-ordinary'],
    country: 'ca',
    includeDetails: true,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const p of items) console.log(p.name, p.price, p.currency, (p.variants || []).length, 'variants');
```

## Main inputs

| Input | What it does |
|---|---|
| `searchQueries` | Keywords, answered by Sephora's own search (`"mascara"`) |
| `categories` | Category slugs or ids (`"face-serum"`, `"foundation-makeup"`, `"cat60026"`) or a sephora.com/shop URL |
| `brands` | Brand slugs as in sephora.com/brand/&lt;slug&gt; (`"the-ordinary"`) or the brand page URL |
| `startUrls` | Product URLs |
| `country` | `us` (USD) or `ca` (Sephora Canada, CAD) |
| `includeDetails` | Adds description, ingredients, loves count, category path, images and every variant with stock flags |
| `sortBy` | `relevance`, `bestSelling`, `topRated`, `newest`, `priceLowToHigh`, `priceHighToLow` |
| `minPrice`, `maxPrice`, `minRating`, `brandFilter`, `onSaleOnly`, `newOnly` | Filters applied by Sephora before anything is charged |
| `maxItemsPerQuery`, `maxItems` | Caps (default 100 per query, 1,000 per run) |

## Output sample (real row, `mascara` search, 22 Oct 2026, trimmed)

```json
{
  "productId": "P467208",
  "name": "Lash Idôle Lengthening & Volumizing Mascara",
  "brand": "Lancôme",
  "listPrice": "$16.00 - $30.00",
  "price": 16,
  "priceMax": 30,
  "regularPrice": 16,
  "salePrice": null,
  "isOnSale": false,
  "rating": 4.4998,
  "reviews": 10785,
  "variantsCount": 2,
  "isNew": false,
  "isBestseller": true,
  "currency": "USD",
  "url": "https://www.sephora.com/product/lancome-lash-idole-lash-lifting-volumizing-mascara-P467208?skuId=2417145",
  "position": 1,
  "sourceType": "search",
  "sourceQuery": "mascara"
}
```

## Example output (`python example.py --from-json sample.json`)

Run on the 20 real `mascara` rows in `sample.json`:

```
20 products -> sephora_products.csv
Price from 9 to 34 USD, median 16.0
On sale: 0 of 20

Top rated after review-count weighting (average 4.04):
  4.55  4.62 (3,228 reviews)  16 USD  Benefit Cosmetics - Fan Fest Fanning & Volumizing Mascara
  4.48  4.50 (10,785 reviews)  16 USD  Lancôme - Lash Idôle Lengthening & Volumizing Mascara
  4.46  4.48 (11,238 reviews)  16 USD  Lancôme - Mini Lash Idôle Lengthening & Volumizing Mascara
  4.36  4.51 (1,032 reviews)  34 USD  Yves Saint Laurent - Lash Latex Sculpting & Lengthening Mascara
  4.33  4.54 (664 reviews)  16 USD  MERIT - Clean Volume - Volumizing Tubing Mascara

Most-reviewed under the median price:
  19,692 reviews  3.72  16 USD  Too Faced - Better Than Sex Volumizing & Lengthening Mascara
  16,141 reviews  3.70  16 USD  Too Faced - Mini Better Than Sex Volumizing & Lengthening Mascara
  11,238 reviews  4.48  16 USD  Lancôme - Mini Lash Idôle Lengthening & Volumizing Mascara
  10,785 reviews  4.50  16 USD  Lancôme - Lash Idôle Lengthening & Volumizing Mascara
   6,120 reviews  3.83  16 USD  Benefit Cosmetics - BADgal BANG! Volumizing 36-Hour Longwear Mascara
```

The most-reviewed mascara in the sample (Too Faced, 19,692 reviews) is also one of the lowest rated (3.72): review count alone is a popularity signal, not a quality one.

## Ideas

- **Daily sale tracker**: `--on-sale` on a few categories once a day, diff against yesterday's CSV.
- **Launch tracker**: `newOnly: true, sortBy: "newest"`.
- **Brand audit**: one brand with `includeDetails: true`; diff each variant's `isOutOfStock` day to day to spot sell-outs.
- **Ingredient search**: details on, then filter `ingredients` for `Niacinamide` or `Retinol`.

Full walkthrough with a sale-tracker script: [Tracking Sephora prices, sales and new launches with Python](https://dev.to/rel8ble/tracking-sephora-prices-sales-and-new-launches-with-python-no-browser-no-api-key-2pme).

## Price and limits

- **$0.85 per 1,000 products**, no start fee, same price with or without details. Failed requests are never charged.
- Listings come about 100 products per request (451 products took 86 seconds in a cloud test). Details add one request per product.
- Keyword search returns what Sephora's search returns; use categories or brands for an exact set.
- Stock flags are per variant and only in detailed rows.
- Reviews themselves are not collected, only rating, review count, loves count and Sephora's sentiment tags.
- US and Canada only; sephora.fr, .co.uk, .com.au and other Sephora sites are separate platforms and not covered.

Apify Store: https://apify.com/rel8ble/sephora-products-scraper

Related: [Amazon Best Sellers scraper](https://github.com/Rel8ble/amazon-best-sellers-scraper-python) · [Shopify store products scraper](https://apify.com/rel8ble/shopify-store-products-scraper)

## License

MIT

Need a custom scraper or a ready dataset? Hire me on Fiverr: https://www.fiverr.com/rel8ble
