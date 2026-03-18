from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 1. Hvordan lage datoer enkelt (Konvertering fra string til datetime)
def create_date(date_str):
    # PyDriller bruker datetime-objekter. Format: ÅR-MND-DAG
    return datetime.strptime(date_str, "%Y-%m-%d")

# 2. Oppsett av testdata (datapoints)
datapoints = [
    {"added": 5,  "deleted": 1, "commitdate": create_date("2026-01-03"), "id": 36},
    {"added": 20, "deleted": 5, "commitdate": create_date("2025-11-28"), "id": 888},
    {"added": 3,  "deleted": 1, "commitdate": create_date("2025-02-01"), "id": 19},
    {"added": 15, "deleted": 0, "commitdate": create_date("2025-11-05"), "id": 54},
    {"added": 8,  "deleted": 2, "commitdate": create_date("2025-10-15"), "id": 95},
    {"added": 10, "deleted": 2, "commitdate": create_date("2026-02-01"), "id": 67}, # Nyligst
    {"added": 12, "deleted": 4, "commitdate": create_date("2025-09-10"), "id": 22},
    {"added": 12, "deleted": 4, "commitdate": create_date("2025-09-10"), "id": 23},
    {"added": 3,  "deleted": 1, "commitdate": create_date("2025-08-20"), "id": 18},
    {"added": 30, "deleted": 0, "commitdate": create_date("2025-06-15"), "id": 90},
    {"added": 2,  "deleted": 0, "commitdate": create_date("2025-06-02"), "id": 46},
]

datapoints.sort(key=lambda x: x["commitdate"], reverse=True)

merged_data = {}

for entry in datapoints:
    # Vi bruker bare .date() delen som nøkkel
    d_key = entry["commitdate"].date()
    
    if d_key in merged_data:
        # Hvis datoen finnes, oppdater eksisterende objekt
        merged_data[d_key]["added"] += entry["added"]
        merged_data[d_key]["deleted"] += entry["deleted"]
        # Vi legger til ID-en i en liste bare for å ha kontroll
        # if isinstance(merged_data[d_key]["id"], list):
        #     merged_data[d_key]["id"].append(entry["id"])
        # else:
        #     merged_data[d_key]["id"] = [merged_data[d_key]["id"], entry["id"]]
    else:
        # Hvis ny dato, lagre en kopi av objektet
        merged_data[d_key] = entry.copy()
        merged_data[d_key]["commitdate"] = d_key

datapoints = sorted(merged_data.values(), key=lambda x: x["commitdate"], reverse=True)

# 3. Finn nyligste dato (Programmet finner ut at det er 1. feb)
most_recent_date = datapoints[0]["commitdate"]
most_recent_obj = datapoints[0]
if (most_recent_obj["id"] == 67):
    print("Riktig tidligste dato er hentet ut")
else:
    print(f"Ikke riktig dato, id skulle vært '67', fikk {most_recent_obj['id']}")

# 4. Definer tidsperiodene basert på nyligste dato
# Periode 1: 0-2 måneder siden
p1_limit = most_recent_date - relativedelta(months=2)
# Periode 2: 3-4 måneder siden
p2_limit = most_recent_date - relativedelta(months=4)
# Periode 3: 5-6 måneder siden
p3_limit = most_recent_date - relativedelta(months=6)

# Lister for lagring
period_0_2 = []
period_3_4 = []
period_5_6 = []
trash_pile = []

# 5. Sorteringslogikk
for entry in datapoints:
    dt = entry["commitdate"]
    
    if dt >= p1_limit:
        period_0_2.append(entry)
    elif dt >= p2_limit:
        period_3_4.append(entry)
    elif dt >= p3_limit:
        period_5_6.append(entry)
    else:
        trash_pile.append(entry)

# --- UTSKRIFT FOR OVERSIKT ---
print(f"--- ANALYSE STARTET ---")
print(f"Nyligste commit funnet: {most_recent_date.date()}\n")

def print_bucket(name, bucket):
    print(f"[{name.upper()}] ({len(bucket)} items):")
    for item in bucket:
        print(f"  - Dato: {item['commitdate'].date()} | +{item['added']} -{item['deleted']}")
    print("-" * 30)

print_bucket("0-2 måneder (Nyligst)", period_0_2)
print_bucket("3-4 måneder", period_3_4)
print_bucket("5-6 måneder", period_5_6)
print_bucket("Trash (Eldre enn 6 mnd)", trash_pile)