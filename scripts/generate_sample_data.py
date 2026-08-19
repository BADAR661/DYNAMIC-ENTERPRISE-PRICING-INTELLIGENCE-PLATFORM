import csv
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(r'D:\Badar Nadeem\Enterprise-Dynamic-Pricing-Intelligence-Platform')
RAW_DIR = ROOT / 'data' / 'raw'
PROCESSED_DIR = ROOT / 'data' / 'processed'
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)
regions = ['Lahore', 'Karachi', 'Islamabad', 'Peshawar', 'Faisalabad']
segments = ['Budget', 'Standard', 'Premium']
products = [
    ('P001', 'Wireless Headphones', 'Electronics', 1000.00, 650.00, 120),
    ('P002', 'Smart Watch', 'Electronics', 1500.00, 950.00, 80),
    ('P003', 'USB-C Cable', 'Accessories', 300.00, 120.00, 250),
    ('P004', 'Laptop Stand', 'Accessories', 2500.00, 1500.00, 45),
    ('P005', 'Bluetooth Speaker', 'Electronics', 3500.00, 2200.00, 30),
    ('P006', 'Gaming Mouse', 'Electronics', 1200.00, 750.00, 110),
    ('P007', 'Mechanical Keyboard', 'Electronics', 2200.00, 1400.00, 60),
    ('P008', 'Portable Charger', 'Accessories', 900.00, 600.00, 95),
    ('P009', 'Tablet Sleeve', 'Accessories', 700.00, 450.00, 150),
    ('P010', 'Noise Cancelling Earbuds', 'Electronics', 1800.00, 1100.00, 70),
    ('P011', 'Webcam', 'Electronics', 1600.00, 1000.00, 85),
    ('P012', 'Monitor Lamp', 'Home Office', 800.00, 500.00, 65),
]

customers = []
for i in range(1, 251):
    signup_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 800))
    customers.append({
        'customer_id': f'C{i:03d}',
        'customer_name': f'Customer {i}',
        'region': random.choice(regions),
        'customer_segment': random.choice(segments),
        'signup_date': signup_date.strftime('%Y-%m-%d'),
    })

sales = []
for i in range(1, 601):
    product_id, _, _, base_price, _, _ = random.choice(products)
    sale_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 799))
    quantity_sold = random.randint(1, 5)
    selling_price = round(max(200, min(4000, base_price * random.uniform(0.9, 1.15))), 2)
    sales.append({
        'sale_id': f'S{i:04d}',
        'product_id': product_id,
        'customer_id': random.choice([c['customer_id'] for c in customers]),
        'sale_date': sale_date.strftime('%Y-%m-%d'),
        'quantity_sold': quantity_sold,
        'selling_price': selling_price,
        'region': random.choice(regions),
    })

inventory_rows = []
for sale in sales:
    inventory_rows.append({
        'product_id': sale['product_id'],
        'inventory_date': sale['sale_date'],
        'average_inventory': round(max(10, min(250, random.gauss(80, 20))), 2),
    })

competitor_rows = []
for sale in sales:
    product_id, _, _, base_price, _, _ = next(p for p in products if p[0] == sale['product_id'])
    competitor_rows.append({
        'product_id': sale['product_id'],
        'competitor_name': random.choice(['Competitor_A', 'Competitor_B', 'Competitor_C']),
        'competitor_price': round(max(200, min(4500, base_price * random.uniform(0.95, 1.08))), 2),
        'recorded_date': sale['sale_date'],
        'region': sale['region'],
    })


def write_csv(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

write_csv(RAW_DIR / 'products.csv', ['product_id','product_name','category','base_price','cost_price','current_inventory'], [
    {'product_id': pid, 'product_name': name, 'category': category, 'base_price': base_price, 'cost_price': cost_price, 'current_inventory': inv}
    for pid, name, category, base_price, cost_price, inv in products
])
write_csv(RAW_DIR / 'customers.csv', ['customer_id','customer_name','region','customer_segment','signup_date'], customers)
write_csv(RAW_DIR / 'sales.csv', ['sale_id','product_id','customer_id','sale_date','quantity_sold','selling_price','region'], sales)
write_csv(RAW_DIR / 'inventory.csv', ['product_id','inventory_date','average_inventory'], inventory_rows)
write_csv(RAW_DIR / 'competitor_prices.csv', ['product_id','competitor_name','competitor_price','recorded_date','region'], competitor_rows)

product_map = {pid: {'base_price': base_price, 'cost_price': cost_price} for pid, _, _, base_price, cost_price, _ in products}
processed_rows = []
for sale in sales:
    product_info = product_map[sale['product_id']]
    processed_rows.append({
        'sale_id': sale['sale_id'],
        'product_id': sale['product_id'],
        'customer_id': sale['customer_id'],
        'sale_date': sale['sale_date'],
        'quantity_sold': sale['quantity_sold'],
        'selling_price': sale['selling_price'],
        'region': sale['region'],
        'base_price': product_info['base_price'],
        'cost_price': product_info['cost_price'],
        'price_difference': round(sale['selling_price'] - product_info['base_price'], 2),
        'inventory_turnover': round(sale['quantity_sold'] / 80, 2),
        'recommended_price': round(product_info['base_price'] * (1 + 0.02 * sale['quantity_sold']), 2),
        'discount_flag': 1 if sale['selling_price'] < product_info['base_price'] else 0,
    })

competitor_features = defaultdict(list)
for row in processed_rows:
    competitor_features[row['product_id']].append(row['selling_price'])

competitor_feature_rows = []
for product_id, values in competitor_features.items():
    competitor_feature_rows.append({
        'product_id': product_id,
        'avg_competitor_price': round(sum(values) / len(values), 2),
        'min_competitor_price': round(min(values), 2),
        'max_competitor_price': round(max(values), 2),
        'observed_sales': len(values),
    })

customer_totals = defaultdict(lambda: {'total_spend': 0.0, 'total_units': 0, 'regions_seen': set()})
for row in processed_rows:
    c = customer_totals[row['customer_id']]
    c['total_spend'] += row['selling_price']
    c['total_units'] += row['quantity_sold']
    c['regions_seen'].add(row['region'])

customer_ltv_rows = []
for customer_id, values in customer_totals.items():
    customer_ltv_rows.append({
        'customer_id': customer_id,
        'total_spend': round(values['total_spend'], 2),
        'total_units': values['total_units'],
        'regions_seen': len(values['regions_seen']),
        'customer_ltv': round(values['total_spend'] * 0.35 + values['total_units'] * 50, 2),
    })

product_inventory_rows = []
for product_id in [p[0] for p in products]:
    matching_rows = [r for r in processed_rows if r['product_id'] == product_id]
    if not matching_rows:
        continue
    avg_selling = sum(r['selling_price'] for r in matching_rows) / len(matching_rows)
    avg_qty = sum(r['quantity_sold'] for r in matching_rows) / len(matching_rows)
    total_units = sum(r['quantity_sold'] for r in matching_rows)
    current_inventory = next(inv for pid, _, _, _, _, inv in products if pid == product_id)
    product_inventory_rows.append({
        'product_id': product_id,
        'average_selling_price': round(avg_selling, 2),
        'average_quantity_sold': round(avg_qty, 2),
        'total_units_sold': total_units,
        'current_inventory': current_inventory,
        'inventory_health': 'Low' if current_inventory < 50 else 'Healthy',
    })

enriched_customer_rows = []
for customer in customers:
    c = next((x for x in customer_ltv_rows if x['customer_id'] == customer['customer_id']), None)
    enriched_customer_rows.append({
        'customer_id': customer['customer_id'],
        'customer_name': customer['customer_name'],
        'region': customer['region'],
        'customer_segment': customer['customer_segment'],
        'signup_date': customer['signup_date'],
        'total_spend': c['total_spend'] if c else 0.0,
        'total_units': c['total_units'] if c else 0,
        'regions_seen': c['regions_seen'] if c else 0,
        'customer_ltv': c['customer_ltv'] if c else 0.0,
    })

write_csv(PROCESSED_DIR / 'competitor_price_features.csv', ['product_id','avg_competitor_price','min_competitor_price','max_competitor_price','observed_sales'], competitor_feature_rows)
write_csv(PROCESSED_DIR / 'customer_lifetime_value.csv', ['customer_id','total_spend','total_units','regions_seen','customer_ltv'], customer_ltv_rows)
write_csv(PROCESSED_DIR / 'enriched_customers.csv', ['customer_id','customer_name','region','customer_segment','signup_date','total_spend','total_units','regions_seen','customer_ltv'], enriched_customer_rows)
write_csv(PROCESSED_DIR / 'enriched_pricing_dataset.csv', ['sale_id','product_id','customer_id','sale_date','quantity_sold','selling_price','region','base_price','cost_price','price_difference','inventory_turnover','recommended_price','discount_flag'], processed_rows)
write_csv(PROCESSED_DIR / 'product_inventory_summary.csv', ['product_id','average_selling_price','average_quantity_sold','total_units_sold','current_inventory','inventory_health'], product_inventory_rows)

print('Generated 600 sales rows and 250 customer rows successfully.')
