import random
from datetime import datetime, timedelta

# Sample data for Sierra Leone districts and areas
DISTRICTS = [
    "Freetown", "Bo", "Kenema", "Makeni", "Koidu", 
    "Port Loko", "Waterloo", "Lunsar", "Kabala", "Moyamba"
]

STATUS_OPTIONS = ["green", "yellow", "red"]
CAUSE_OPTIONS = ["Drought", "Broken Pump", "Dry Well", "Contamination", "Overuse", "Seasonal"]

def generate_sample_data(count=100):
    data = []
    start_date = datetime(2026, 1, 1)
    
    for i in range(1, count + 1):
        district = random.choice(DISTRICTS)
        status = random.choices(STATUS_OPTIONS, weights=[70, 20, 10])[0]
        
        # Random coordinates roughly within Sierra Leone bounds
        lat = round(random.uniform(7.0, 10.0), 4)
        lon = round(random.uniform(-13.3, -10.3), 4)
        
        # Random update date within the last 30 days
        days_ago = random.randint(0, 30)
        update_date = datetime.now() - timedelta(days=days_ago)
        
        source = {
            "id": f"WELL{i:03d}",
            "name": f"{district} Source {i}",
            "district": district,
            "status": status,
            "cause": random.choice(CAUSE_OPTIONS) if status != "green" else "None",
            "latitude": lat,
            "longitude": lon,
            "last_updated": update_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        data.append(source)
    
    return data

if __name__ == "__main__":
    samples = generate_sample_data(100)
    
    # Generate SQL Insert statements for convenience
    with open("seed_data.sql", "w") as f:
        f.write("-- CleanFlow SL Sample Dataset (100 Records)\n")
        f.write("INSERT INTO water_sources (id, name, district, status, cause, latitude, longitude, last_updated) VALUES\n")
        
        values = []
        for s in samples:
            val = f"('{s['id']}', '{s['name']}', '{s['district']}', '{s['status']}', '{s['cause']}', {s['latitude']}, {s['longitude']}, '{s['last_updated']}')"
            values.append(val)
        
        f.write(",\n".join(values) + ";")
        
    print(f"Successfully generated 100 sample records in seed_data.sql")
