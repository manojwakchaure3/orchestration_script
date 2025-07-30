# bankrate_rates_spider.py
import scrapy, re, os, csv, json
from datetime import datetime, date
from scrapy.crawler import CrawlerProcess

class BankrateRatesSpider(scrapy.Spider):
    name = "bankrate_rates"
    start_urls = ["https://www.bankrate.com/mortgages/mortgage-rates/"]

    def __init__(self):
        super().__init__()
        base = os.path.dirname(os.path.abspath(__file__))
        self.csv_path  = os.path.join(base, "bankrate_rates_history.csv")
        self.json_path = os.path.join(base, "bankrate_loans.json")
        self.fields    = ["loan_product","interest_rate","apr_percent",
                          "loan_term_years","lender_name","updated_date"]
        self.today_items = []

    def parse(self, response):
        # parse “Rates as of” date
        raw = response.css('p.mb-0::text').re_first(r'Rates as of (.*)')
        try:
            run_date = datetime.strptime(raw.strip(), "%A, %B %d, %Y at %I:%M %p").date()
        except:
            run_date = date.today()
        if run_date != date.today():
            self.logger.info(f"Only processing today’s rates ({date.today()}); skipping {run_date}")
            return

        # load existing keys so CSV never repeats
        seen = set()
        if os.path.exists(self.csv_path):
            with open(self.csv_path, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    seen.add((r["loan_product"], r["updated_date"]))

        # scrape Purchase rows
        for row in response.css('div[aria-labelledby="purchase-0"] table tbody tr'):
            prod = row.css('th a::text').get(default="").strip()
            rate= row.css('td:nth-of-type(1)::text').get(default="").strip()
            apr = row.css('td:nth-of-type(2)::text').get(default="").strip()
            if not (prod and rate and apr): continue
            m = re.search(r'(\d+)-Year', prod)
            term = int(m.group(1)) if m else None
            key = (prod, run_date.isoformat())
            if key in seen: continue
            item = {
                "loan_product": prod,
                "interest_rate": rate,
                "apr_percent": apr,
                "loan_term_years": term,
                "lender_name": "Bankrate",
                "updated_date": run_date.isoformat()
            }
            self.today_items.append(item)
            yield item

    def closed(self, reason):
        if not self.today_items:
            print("⚠ No new rates for today. JSON unchanged, CSV untouched.")
            return

        # write today’s snapshot JSON
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.today_items, f, indent=2)
        print(f"✅ JSON snapshot saved ({len(self.today_items)} items)")

        # append these to CSV
        write_hdr = not os.path.exists(self.csv_path) or os.path.getsize(self.csv_path)==0
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=self.fields)
            if write_hdr: w.writeheader()
            w.writerows(self.today_items)
        print(f"✅ Appended {len(self.today_items)} new rows to CSV")

if __name__ == "__main__":
    CrawlerProcess({
        "USER_AGENT": "Mozilla/5.0",
        "LOG_LEVEL": "INFO",
        "FEED_FORMAT": None  # disable built-in feed
    }).crawl(BankrateRatesSpider).start()
