"""Generate a complex 200-row dataset with realistic data quality issues"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

# Define realistic data
products = [
    ("Laptop Pro 15", 1299.99),
    ("Wireless Mouse", 29.99),
    ("USB-C Cable", 12.99),
    ("Monitor 27inch", 399.99),
    ("Keyboard Mechanical", 89.99),
    ("Webcam HD", 79.99),
    ("Headphones Bluetooth", 149.99),
    ("External SSD 1TB", 119.99),
    ("Docking Station", 199.99),
    ("Phone Stand", 19.99),
]

regions = ["North", "South", "East", "West", "Central"]
payment_methods = ["Credit Card", "PayPal", "Debit Card", "Bank Transfer", "Cash"]
customer_segments = ["Enterprise", "SMB", "Individual", "Education", "Government"]

# Generate base data
data = []
start_date = datetime(2024, 1, 1)

for i in range(200):
    product_name, base_price = random.choice(products)
    
    # Generate transaction date
    days_offset = random.randint(0, 180)
    transaction_date = start_date + timedelta(days=days_offset)
    
    # Generate customer info
    customer_id = f"CUST{1000 + i}"
    first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"{first_name.lower()}.{last_name.lower()}@email.com"
    
    # Generate transaction details
    quantity = random.randint(1, 10)
    unit_price = base_price * random.uniform(0.9, 1.1)  # Price variation
    discount_pct = random.choice([0, 5, 10, 15, 20, 25])
    
    region = random.choice(regions)
    payment_method = random.choice(payment_methods)
    customer_segment = random.choice(customer_segments)
    
    # Calculate amounts
    subtotal = quantity * unit_price
    discount_amount = subtotal * (discount_pct / 100)
    tax_amount = (subtotal - discount_amount) * 0.08  # 8% tax
    total_amount = subtotal - discount_amount + tax_amount
    
    # Shipping info
    shipping_cost = 0 if total_amount > 100 else 9.99
    
    data.append({
        'transaction_id': f"TXN{10000 + i}",
        'customer_id': customer_id,
        'customer_name': f"{first_name} {last_name}",
        'email': email,
        'phone': f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        'customer_segment': customer_segment,
        'product_name': product_name,
        'quantity': quantity,
        'unit_price': unit_price,
        'discount_pct': discount_pct,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'tax_amount': tax_amount,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount,
        'payment_method': payment_method,
        'transaction_date': transaction_date.strftime('%Y-%m-%d'),
        'region': region,
        'status': 'completed'
    })

df = pd.DataFrame(data)

print(f"Generated {len(df)} rows of clean data")
print(f"Columns: {list(df.columns)}")
print("\nNow introducing data quality issues...")

# Save clean version for reference
df.to_csv('data/input/clean_reference.csv', index=False)
print("✓ Saved clean reference")

# ============================================================================
# INTRODUCE DATA QUALITY ISSUES
# ============================================================================

df_messy = df.copy()

# Issue 1: EXACT DUPLICATES (5 pairs = 10 rows affected)
print("\n1. Creating exact duplicates...")
duplicate_indices = random.sample(range(len(df_messy)), 5)
for idx in duplicate_indices:
    # Insert duplicate right after original
    df_messy = pd.concat([
        df_messy.iloc[:idx+1],
        df_messy.iloc[idx:idx+1],
        df_messy.iloc[idx+1:]
    ]).reset_index(drop=True)

print(f"   ✓ Added 5 exact duplicates (now {len(df_messy)} rows)")

# Issue 2: NEAR DUPLICATES - Same transaction but different status
print("\n2. Creating near duplicates (same transaction, different status)...")
for i in range(3):
    idx = random.randint(0, len(df_messy)-1)
    near_dup = df_messy.iloc[idx].copy()
    near_dup['status'] = random.choice(['pending', 'cancelled', 'refunded'])
    df_messy = pd.concat([df_messy, pd.DataFrame([near_dup])]).reset_index(drop=True)

print(f"   ✓ Added 3 near duplicates (now {len(df_messy)} rows)")

# Issue 3: RETURNS/REFUNDS - Negative quantities (legitimate business data!)
print("\n3. Adding returns/refunds (negative quantities)...")
return_indices = random.sample(range(len(df_messy)), 8)
for idx in return_indices:
    df_messy.at[idx, 'quantity'] = -abs(df_messy.at[idx, 'quantity'])
    df_messy.at[idx, 'status'] = random.choice(['refunded', 'returned'])
    # Recalculate amounts for returns
    df_messy.at[idx, 'subtotal'] = -abs(df_messy.at[idx, 'subtotal'])
    df_messy.at[idx, 'total_amount'] = -abs(df_messy.at[idx, 'total_amount'])

print(f"   ✓ Added 8 returns/refunds with negative quantities")

# Issue 4: MISSING VALUES (various patterns)
print("\n4. Introducing missing values...")
missing_patterns = [
    ('email', 15, "Missing customer email"),
    ('phone', 20, "Missing phone number"),
    ('customer_name', 5, "Missing customer name"),
    ('discount_pct', 10, "Missing discount (should be 0)"),
    ('shipping_cost', 8, "Missing shipping cost"),
]

for col, count, desc in missing_patterns:
    indices = random.sample(range(len(df_messy)), count)
    for idx in indices:
        df_messy.at[idx, col] = np.nan
    print(f"   ✓ {desc}: {count} rows")

# Issue 5: INCONSISTENT FORMATTING - Prices
print("\n5. Messing up price formatting...")
price_issues = random.sample(range(len(df_messy)), 25)
for idx in price_issues:
    choice = random.randint(1, 5)
    if choice == 1:
        df_messy.at[idx, 'unit_price'] = f"${df_messy.at[idx, 'unit_price']:.2f}"
    elif choice == 2:
        df_messy.at[idx, 'unit_price'] = f"$ {df_messy.at[idx, 'unit_price']:.2f}"
    elif choice == 3:
        df_messy.at[idx, 'unit_price'] = f"{df_messy.at[idx, 'unit_price']:.2f} USD"
    elif choice == 4:
        df_messy.at[idx, 'unit_price'] = str(df_messy.at[idx, 'unit_price']).replace('.', ',')
    else:
        df_messy.at[idx, 'total_amount'] = f"${df_messy.at[idx, 'total_amount']:.2f}"

print(f"   ✓ Added inconsistent price formatting to 25 rows")

# Issue 6: INCONSISTENT FORMATTING - Dates
print("\n6. Messing up date formatting...")
date_issues = random.sample(range(len(df_messy)), 30)
for idx in date_issues:
    date_str = df_messy.at[idx, 'transaction_date']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    choice = random.randint(1, 6)
    if choice == 1:
        df_messy.at[idx, 'transaction_date'] = date_obj.strftime('%m/%d/%Y')
    elif choice == 2:
        df_messy.at[idx, 'transaction_date'] = date_obj.strftime('%d-%m-%Y')
    elif choice == 3:
        df_messy.at[idx, 'transaction_date'] = date_obj.strftime('%Y/%m/%d')
    elif choice == 4:
        df_messy.at[idx, 'transaction_date'] = date_obj.strftime('%b %d, %Y')
    elif choice == 5:
        df_messy.at[idx, 'transaction_date'] = "INVALID_DATE"
    else:
        df_messy.at[idx, 'transaction_date'] = ""

print(f"   ✓ Added inconsistent date formatting to 30 rows")

# Issue 7: INCONSISTENT CASING
print("\n7. Messing up text casing...")
casing_issues = random.sample(range(len(df_messy)), 40)
for idx in casing_issues:
    choice = random.randint(1, 4)
    if choice == 1:
        df_messy.at[idx, 'region'] = df_messy.at[idx, 'region'].upper()
    elif choice == 2:
        df_messy.at[idx, 'region'] = df_messy.at[idx, 'region'].lower()
    elif choice == 3:
        if pd.notna(df_messy.at[idx, 'email']):
            df_messy.at[idx, 'email'] = df_messy.at[idx, 'email'].upper()
    else:
        df_messy.at[idx, 'payment_method'] = df_messy.at[idx, 'payment_method'].lower()

print(f"   ✓ Added inconsistent casing to 40 rows")

# Issue 8: WHITESPACE ISSUES
print("\n8. Adding whitespace issues...")
whitespace_issues = random.sample(range(len(df_messy)), 35)
for idx in whitespace_issues:
    choice = random.randint(1, 4)
    if choice == 1:
        df_messy.at[idx, 'product_name'] = "  " + df_messy.at[idx, 'product_name']
    elif choice == 2:
        df_messy.at[idx, 'product_name'] = df_messy.at[idx, 'product_name'] + "  "
    elif choice == 3:
        if pd.notna(df_messy.at[idx, 'customer_name']):
            df_messy.at[idx, 'customer_name'] = "  " + df_messy.at[idx, 'customer_name'] + "  "
    else:
        df_messy.at[idx, 'region'] = " " + df_messy.at[idx, 'region'] + " "

print(f"   ✓ Added whitespace issues to 35 rows")

# Issue 9: INVALID EMAIL FORMATS
print("\n9. Creating invalid email formats...")
email_issues = random.sample([i for i in range(len(df_messy)) if pd.notna(df_messy.at[i, 'email'])], 20)
for idx in email_issues:
    choice = random.randint(1, 5)
    if choice == 1:
        df_messy.at[idx, 'email'] = df_messy.at[idx, 'email'].replace('@', '')
    elif choice == 2:
        df_messy.at[idx, 'email'] = df_messy.at[idx, 'email'].replace('.com', '')
    elif choice == 3:
        df_messy.at[idx, 'email'] = df_messy.at[idx, 'email'].split('@')[0]
    elif choice == 4:
        df_messy.at[idx, 'email'] = "invalid.email"
    else:
        df_messy.at[idx, 'email'] = df_messy.at[idx, 'email'] + ".invalid"

print(f"   ✓ Created invalid email formats in 20 rows")

# Issue 10: CALCULATION ERRORS (subtotal != quantity * unit_price)
print("\n10. Introducing calculation errors...")
calc_errors = random.sample(range(len(df_messy)), 15)
for idx in calc_errors:
    # Make subtotal wrong
    df_messy.at[idx, 'subtotal'] = float(df_messy.at[idx, 'subtotal']) * random.uniform(0.8, 1.2)

print(f"   ✓ Added calculation errors to 15 rows")

# Issue 11: OUTLIERS (suspiciously high/low values)
print("\n11. Adding outliers...")
outlier_indices = random.sample(range(len(df_messy)), 10)
for idx in outlier_indices:
    choice = random.randint(1, 4)
    if choice == 1:
        # Unrealistic quantity
        df_messy.at[idx, 'quantity'] = random.choice([0, 999, 1000])
    elif choice == 2:
        # Unrealistic discount
        df_messy.at[idx, 'discount_pct'] = random.choice([99, 100, 150])
    elif choice == 3:
        # Unrealistic price
        df_messy.at[idx, 'unit_price'] = 0.01
    else:
        # Negative total (but not a return)
        if df_messy.at[idx, 'status'] == 'completed':
            df_messy.at[idx, 'total_amount'] = -abs(float(df_messy.at[idx, 'total_amount']))

print(f"   ✓ Added outliers to 10 rows")

# Issue 12: INCONSISTENT PHONE FORMATS
print("\n12. Messing up phone formats...")
phone_issues = random.sample([i for i in range(len(df_messy)) if pd.notna(df_messy.at[i, 'phone'])], 25)
for idx in phone_issues:
    phone = df_messy.at[idx, 'phone']
    choice = random.randint(1, 5)
    if choice == 1:
        df_messy.at[idx, 'phone'] = phone.replace('+1-', '').replace('-', '')
    elif choice == 2:
        df_messy.at[idx, 'phone'] = phone.replace('-', '.')
    elif choice == 3:
        df_messy.at[idx, 'phone'] = phone.replace('+1-', '(1) ')
    elif choice == 4:
        df_messy.at[idx, 'phone'] = phone.replace('+1-', '')
    else:
        df_messy.at[idx, 'phone'] = "INVALID"

print(f"   ✓ Added phone format issues to 25 rows")

# Issue 13: TYPOS IN CATEGORICAL VALUES
print("\n13. Adding typos in categorical values...")
typo_indices = random.sample(range(len(df_messy)), 20)
typo_map = {
    'North': ['north', 'NORTH', 'Nrth', 'Norht'],
    'Credit Card': ['credit card', 'CreditCard', 'Credt Card', 'CC'],
    'Enterprise': ['enterprise', 'Enterprize', 'Ent'],
    'completed': ['Completed', 'COMPLETED', 'complete', 'done'],
}

for idx in typo_indices:
    choice = random.randint(1, 3)
    if choice == 1 and df_messy.at[idx, 'region'] in typo_map:
        df_messy.at[idx, 'region'] = random.choice(typo_map[df_messy.at[idx, 'region']])
    elif choice == 2 and df_messy.at[idx, 'payment_method'] in typo_map:
        df_messy.at[idx, 'payment_method'] = random.choice(typo_map[df_messy.at[idx, 'payment_method']])
    elif choice == 3 and df_messy.at[idx, 'status'] in typo_map:
        df_messy.at[idx, 'status'] = random.choice(typo_map[df_messy.at[idx, 'status']])

print(f"   ✓ Added typos to 20 rows")

# Issue 14: MIXED DATA TYPES IN NUMERIC COLUMNS
print("\n14. Mixing data types in numeric columns...")
mixed_type_indices = random.sample(range(len(df_messy)), 15)
for idx in mixed_type_indices:
    choice = random.randint(1, 3)
    if choice == 1:
        df_messy.at[idx, 'quantity'] = str(int(df_messy.at[idx, 'quantity'])) + " units"
    elif choice == 2:
        df_messy.at[idx, 'discount_pct'] = str(df_messy.at[idx, 'discount_pct']) + "%"
    else:
        df_messy.at[idx, 'tax_amount'] = "N/A"

print(f"   ✓ Added mixed data types to 15 rows")

# Issue 15: FUTURE DATES (data entry errors)
print("\n15. Adding future dates...")
future_date_indices = random.sample(range(len(df_messy)), 5)
for idx in future_date_indices:
    future_date = datetime.now() + timedelta(days=random.randint(1, 365))
    df_messy.at[idx, 'transaction_date'] = future_date.strftime('%Y-%m-%d')

print(f"   ✓ Added 5 future dates")

# Issue 16: SPECIAL CHARACTERS IN TEXT FIELDS
print("\n16. Adding special characters...")
special_char_indices = random.sample(range(len(df_messy)), 12)
for idx in special_char_indices:
    choice = random.randint(1, 3)
    if choice == 1:
        df_messy.at[idx, 'product_name'] = df_messy.at[idx, 'product_name'] + " ™"
    elif choice == 2 and pd.notna(df_messy.at[idx, 'customer_name']):
        df_messy.at[idx, 'customer_name'] = df_messy.at[idx, 'customer_name'] + " Jr."
    else:
        df_messy.at[idx, 'transaction_id'] = df_messy.at[idx, 'transaction_id'] + "#"

print(f"   ✓ Added special characters to 12 rows")

# Issue 17: ZERO VALUES WHERE THEY SHOULDN'T BE
print("\n17. Adding inappropriate zero values...")
zero_indices = random.sample(range(len(df_messy)), 8)
for idx in zero_indices:
    choice = random.randint(1, 2)
    if choice == 1:
        df_messy.at[idx, 'unit_price'] = 0
    else:
        df_messy.at[idx, 'total_amount'] = 0

print(f"   ✓ Added inappropriate zeros to 8 rows")

# ============================================================================
# SAVE MESSY DATASET
# ============================================================================

# Shuffle rows to make issues less obvious
df_messy = df_messy.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to CSV
output_path = 'data/input/complex_sales_data.csv'
df_messy.to_csv(output_path, index=False)

print("\n" + "="*80)
print("DATASET GENERATION COMPLETE")
print("="*80)
print(f"Total rows: {len(df_messy)}")
print(f"Total columns: {len(df_messy.columns)}")
print(f"\nSaved to: {output_path}")
print("\nData Quality Issues Summary:")
print("  1. ✓ Exact duplicates (5 pairs)")
print("  2. ✓ Near duplicates (3 cases)")
print("  3. ✓ Returns/refunds with negative quantities (8 rows)")
print("  4. ✓ Missing values (58 total across multiple columns)")
print("  5. ✓ Inconsistent price formatting (25 rows)")
print("  6. ✓ Inconsistent date formatting (30 rows)")
print("  7. ✓ Inconsistent casing (40 rows)")
print("  8. ✓ Whitespace issues (35 rows)")
print("  9. ✓ Invalid email formats (20 rows)")
print(" 10. ✓ Calculation errors (15 rows)")
print(" 11. ✓ Outliers (10 rows)")
print(" 12. ✓ Phone format issues (25 rows)")
print(" 13. ✓ Typos in categorical values (20 rows)")
print(" 14. ✓ Mixed data types (15 rows)")
print(" 15. ✓ Future dates (5 rows)")
print(" 16. ✓ Special characters (12 rows)")
print(" 17. ✓ Inappropriate zero values (8 rows)")
print("\n" + "="*80)
print("\nColumn List:")
for i, col in enumerate(df_messy.columns, 1):
    print(f"  {i:2d}. {col}")
print("="*80)

