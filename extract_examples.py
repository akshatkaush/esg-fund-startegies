import pandas as pd
import re

INPUT_CSV ="result_together.csv"
STRAT_COL = "investment_strategy"
df = pd.read_csv(INPUT_CSV, dtype=str)

df.insert(0, "uid", df.index)
class_keywords = {
    1: [
        "exclude", "harmful", "exclusion", "alcohol", "tobacco", "gambling",
        "guns", "weapons", "fossil fuel", "thermal coal extraction",
        "Arctic exploration", "sans drilling", "avoid"
    ],
    2: [
        "ESG risk", "ESG rating", "climate-related risk",
        "ESG integration", "ESG momentum"
    ],
    3: [
        "Seek ESG opportunities", "sustainability leader", "best in class",
        "positive screening", "best ESG rating", "better ESG rating",
        "ESG performance", "leading in sustainability practices",
        "leader in sustainability practices", "lead in sustainability practices"
    ],
    4: [
        "active owner", "active ownership", "stewardship", "engagement",
        "shareholder resolutions", "proxy voting", "actively engage"
    ],
    5: [
        "target sustainability theme", "targets sustainability theme",
        "renewable energy", "Sustainability-themed investments",
        "Sustainable Development Goals", r"\bSDG\b", "themes",
        "healthy ecosystem", "natural resource security", "human development"
    ],
    6: [
        "assess impact", "impact assessment", "benefit people", "benefit planet",
        "impact framework", "carbon footprint reduction"
    ],
}

class_names = {
    1: "Apply exclusions",
    2: "Limit ESG Risk",
    3: "Seek ESG opportunities",
    4: "Practice Active Ownership",
    5: "Target Sustainability Themes",
    6: "Assess Impact"
}

regex_patterns = {}
for cid, kws in class_keywords.items():
    esc = [re.escape(k) for k in kws]
    base = r"(?:" + "|".join(esc) + r")"

    if cid == 2:
        near = r"(?:\bESG\b(?:\W+\w+){0,100}?\W+\brisk\b|\brisk\b(?:\W+\w+){0,100}?\W+\bESG\b)"
        pattern = f"{base}|{near}"
    elif cid == 5:
        near = r"(?:\bESG\b(?:\W+\w+){0,100}?\W+\btheme\b|\btheme\b(?:\W+\w+){0,100}?\W+\bESG\b)"
        pattern = f"{base}|{near}"
    elif cid == 6:
        near = r"(?:\bESG\b(?:\W+\w+){0,100}?\W+\bimpact\b|\bimpact\b(?:\W+\w+){0,100}?\W+\bESG\b)"
        pattern = f"{base}|{near}"
    else:
        pattern = base

    regex_patterns[cid] = re.compile(pattern, flags=re.IGNORECASE)

masks = {cid: df[STRAT_COL].fillna("").str.contains(rx) for cid, rx in regex_patterns.items()}

for cid, mask in masks.items():
    out = df[mask]
    fname = f"{class_names[cid]}.csv"
    out.to_csv(fname, index=False)
    print(f"Wrote {len(out)} rows to “{fname}”")

combined_mask = pd.Series(False, index=df.index)
for m in masks.values():
    combined_mask |= m

uncls = df[~combined_mask]
uncls.to_csv("unclassified.csv", index=False)
print(f"Wrote {len(uncls)} rows to “unclassified.csv”")
