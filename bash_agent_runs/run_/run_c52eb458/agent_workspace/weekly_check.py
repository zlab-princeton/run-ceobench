"""Weekly checkup script - run at start of each week"""
import novamind_api as nm

print("=== WEEKLY CHECKUP ===")
print(f"Day: {nm.vars.current_day}")

# Subscriber counts
r = nm.query("""
SELECT c.group_id, COUNT(*) as n, 
       SUM(CASE WHEN s.plan='A' THEN 1 ELSE 0 END) as plan_a,
       SUM(CASE WHEN s.plan='B' THEN 1 ELSE 0 END) as plan_b,
       SUM(CASE WHEN s.plan='C' THEN 1 ELSE 0 END) as plan_c
FROM customers c 
JOIN subscriptions s ON c.customer_id = s.customer_id 
WHERE s.status='subscribed'
GROUP BY c.group_id
""")
if r['rows']:
    print("\nSubscribers by group:")
    for row in r['rows']:
        print(f"  {row['group_id']}: {row['n']} total (A:{row['plan_a']}, B:{row['plan_b']}, C:{row['plan_c']})")
else:
    print("\nNo active subscribers yet")

# Enterprise seats
r2 = nm.query("""
SELECT c.group_id, SUM(s.seat_count) as total_seats, COUNT(*) as accounts
FROM customers c 
JOIN subscriptions s ON c.customer_id = s.customer_id 
WHERE s.status='subscribed' AND c.customer_type='enterprise'
GROUP BY c.group_id
""")
if r2['rows']:
    print("\nEnterprise seats:")
    for row in r2['rows']:
        print(f"  {row['group_id']}: {row['total_seats']} seats across {row['accounts']} accounts")

# Financial summary
r3 = nm.query("""
SELECT category, SUM(amount) as total 
FROM ledger 
GROUP BY category
ORDER BY total DESC
""")
print("\nLedger summary:")
total_rev = 0
total_cost = 0
for row in r3['rows']:
    amt = row['total']
    if amt > 0:
        total_rev += amt
    else:
        total_cost += abs(amt)
    print(f"  {row['category']}: ${amt:,.2f}")
print(f"  Net: ${total_rev - total_cost:,.2f}")

# Pending enterprise turns
r4 = nm.query("SELECT COUNT(*) as n FROM enterprise_turns WHERE closed=0")
print(f"\nPending enterprise negotiations: {r4['rows'][0]['n']}")

# Recent enterprise turns (last 7 days)
r5 = nm.query("""
SELECT et.customer_id, c.group_id, et.thread_type, et.status, et.message_text
FROM enterprise_turns et 
JOIN customers c ON et.customer_id = c.customer_id
WHERE et.closed=0
ORDER BY et.day DESC LIMIT 10
""")
if r5['rows']:
    print("\nOpen enterprise negotiations:")
    for row in r5['rows']:
        print(f"  Customer {row['customer_id']} ({row['group_id']}): {row['thread_type']} - {row['message_text'][:100] if row['message_text'] else 'N/A'}")

# Social posts
posts = nm.analytics.get_social_posts(days=7, limit=10)
if posts['posts']:
    print("\nRecent social posts:")
    for p in posts['posts']:
        print(f"  Day {p['day']} [{p['group_id']}]: {p['content'][:100]}")