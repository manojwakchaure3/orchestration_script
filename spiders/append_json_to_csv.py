import os, csv, json
BASE = os.path.dirname(os.path.abspath(__file__))
J, C = os.path.join(BASE,"bankrate_loans.json"), os.path.join(BASE,"bankrate_rates_history.csv")
FIELDS = ["loan_product","interest_rate","apr_percent","loan_term_years","lender_name","updated_date"]

def main():
    if not os.path.exists(J): 
        print("JSON missing; nothing to append."); return
    with open(J,"r",encoding="utf-8") as f:
        recs = json.load(f) if os.path.getsize(J)>0 else []
    today = date.today().isoformat()
    recs = [r for r in recs if r.get("updated_date")==today and all(k in r for k in FIELDS)]
    if not recs:
        print("No today’s valid records to append."); return
    seen = set()
    if os.path.exists(C):
        with open(C,newline="",encoding="utf-8") as f:
            for r in csv.DictReader(f):
                seen.add((r["loan_product"],r["updated_date"]))
    new = [r for r in recs if (r["loan_product"],r["updated_date"]) not in seen]
    if not new:
        print("No new, non-duplicate today’s records to append."); return
    write_hdr = not os.path.exists(C) or os.path.getsize(C)==0
    os.makedirs(os.path.dirname(C),exist_ok=True)
    with open(C,"a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if write_hdr: w.writeheader()
        w.writerows(new)
    print(f"Appended {len(new)} rows to CSV successfully.")
    with open(J,"w",encoding="utf-8") as f: f.write("[]")
    print("Cleared JSON")

if __name__=="__main__":
    from datetime import date
    main()
