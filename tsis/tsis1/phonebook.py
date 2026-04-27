"""
TSIS1: PhoneBook — Extended Contact Management
New features on top of Practice 7 & 8:
  - Extended schema (phones table, groups, email, birthday)
  - Filter by group, search by email, sort results
  - Paginated navigation (next / prev / quit)
  - Export to JSON, import from JSON with duplicate handling
  - Extended CSV import (new fields)
  - Stored procedures: add_phone, move_to_group
  - Extended search_contacts function (all fields + all phones)
"""
 
import csv
import json
from datetime import date, datetime
from connect import connect

def _date_serializer(obj):
    """JSON serializer for date / datetime objects."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializable")
 
 
def _print_row(row):
    """Pretty-print a single contact row."""
    name, email, birthday, grp, phone, ptype = row
    print(
        f"  Name: {name or '-':<20} "
        f"Email: {email or '-':<25} "
        f"Birthday: {str(birthday) or '-':<12} "
        f"Group: {grp or '-':<10} "
        f"Phone: {phone or '-':<15} "
        f"Type: {ptype or '-'}"
    )
 
 
def _get_groups(cur):
    cur.execute("SELECT name FROM groups ORDER BY name")
    return [r[0] for r in cur.fetchall()]
 
 
def _get_or_create_group(cur, grp):
    if not grp:
        return None
    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (grp,))
    cur.execute("SELECT id FROM groups WHERE name = %s", (grp,))
    return cur.fetchone()[0]
 
 
# ──────────────────────────────────────────────
# Feature implementations
# ──────────────────────────────────────────────
 
# 1. Add contact manually
def add_contact():
    print("\n— New Contact —")
    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
 
    email    = input("Email (Enter to skip): ").strip() or None
    birthday = input("Birthday (yyyy-mm-dd, Enter to skip): ").strip() or None
 
    conn = connect(); cur = conn.cursor()
    groups = _get_groups(cur)
    print("Available groups:", ", ".join(groups))
    grp = input("Group (Enter for Other): ").strip() or "Other"
    gid = _get_or_create_group(cur, grp)
 
    try:
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()
 
        if existing:
            print(f"Contact '{name}' already exists. Updating data.")
            cur.execute("""
                UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s
            """, (email, birthday, gid, existing[0]))
            cid = existing[0]
        else:
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, email, birthday, gid))
            cid = cur.fetchone()[0]
 
        # Add phone numbers
        while True:
            phone = input("Phone number (Enter to skip): ").strip()
            if not phone:
                break
            print("Type: 1=mobile  2=home  3=work")
            ptype = {"1": "mobile", "2": "home", "3": "work"}.get(input("Choose: ").strip(), "mobile")
            cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)", (cid, phone, ptype))
            more = input("Add another number? [y/n]: ").strip().lower()
            if more != "y":
                break
 
        conn.commit()
        print(f"Contact '{name}' saved!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close(); conn.close()
 
 
# 2. Filter by group
def filter_by_group():
    conn = connect()
    cur = conn.cursor()
 
    groups = _get_groups(cur)
    print("\nAvailable groups:", ", ".join(groups))
    grp = input("Enter group name: ").strip()
 
    sort_map = {"1": "c.name", "2": "c.birthday", "3": "c.created_at"}
    print("Sort by: 1=Name  2=Birthday  3=Date added")
    col = sort_map.get(input("Choose: ").strip(), "c.name")
 
    cur.execute(f"""
        SELECT c.name, c.email, c.birthday, g.name AS grp, ph.phone, ph.type
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE g.name ILIKE %s
        ORDER BY {col}, ph.phone
    """, (grp,))
 
    rows = cur.fetchall()
    cur.close(); conn.close()
 
    print(f"\nContacts in group '{grp}':")
    if rows:
        for row in rows:
            _print_row(row)
    else:
        print("  No contacts found.")
 
 
# 3. Search by email
def search_by_email():
    pattern = input("Enter email pattern (e.g. gmail): ").strip()
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()
    cur.close(); conn.close()
 
    print(f"\nEmail search results for '{pattern}':")
    if rows:
        for row in rows:
            _print_row(row)
    else:
        print("  No contacts found.")
 
 
# 4. General search with sort
def general_search():
    query = input("Enter name / phone / email / group: ").strip()
 
    sort_map = {"1": "name", "2": "birthday", "3": "grp"}
    print("Sort by: 1=Name  2=Birthday  3=Group")
    key = sort_map.get(input("Choose: ").strip(), "name")
 
    conn = connect(); cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()
    cur.close(); conn.close()
 
    col_idx = {"name": 0, "birthday": 2, "grp": 3}
    idx = col_idx[key]
    rows.sort(key=lambda r: (r[idx] is None, r[idx]))
 
    print(f"\nSearch results for '{query}':")
    if rows:
        for row in rows:
            _print_row(row)
    else:
        print("  No contacts found.")
 
 
# 5. Paginated navigation
def paginated_view():
    page_size = int(input("Rows per page: ").strip() or "5")
    offset = 0
 
    while True:
        conn = connect(); cur = conn.cursor()
        cur.execute(
            "SELECT * FROM get_contacts_paginated_full(%s, %s)",
            (page_size, offset)
        )
        rows = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM contacts")
        total = cur.fetchone()[0]
        cur.close(); conn.close()
 
        print(f"\n─── Page (offset {offset}) ─── total contacts: {total}")
        if rows:
            for r in rows:
                name, email, birthday, grp = r
                print(f"  {name:<20} {email or '-':<25} {str(birthday) or '-':<12} {grp or '-'}")
        else:
            print("  (no data)")
 
        cmd = input("\n[N]ext  [P]rev  [Q]uit: ").strip().lower()
        if cmd == "n":
            if offset + page_size < total:
                offset += page_size
            else:
                print("  Already on the last page.")
        elif cmd == "p":
            offset = max(0, offset - page_size)
        elif cmd in ("q", "quit"):
            break
 
 
# 6. Export to JSON
def export_to_json():
    filename = input("Output filename [contacts_export.json]: ").strip() or "contacts_export.json"
    conn = connect(); cur = conn.cursor()
 
    cur.execute("SELECT id, name, email, birthday, grp, created_at FROM get_all_contacts_full()")
    contacts = cur.fetchall()
 
    output = []
    for cid, name, email, birthday, grp, created_at in contacts:
        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
            (cid,)
        )
        phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]
        output.append({
            "name": name,
            "email": email,
            "birthday": birthday,
            "group": grp,
            "created_at": created_at,
            "phones": phones
        })
 
    cur.close(); conn.close()
 
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=_date_serializer, ensure_ascii=False)
 
    print(f"Exported {len(output)} contacts → {filename}")
 
 
# 7. Import from JSON with duplicate handling
def import_from_json():
    filename = input("JSON filename [contacts_export.json]: ").strip() or "contacts_export.json"
 
    try:
        with open(filename, encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return
 
    conn = connect(); cur = conn.cursor()
    imported = skipped = overwritten = 0
 
    for rec in records:
        name = (rec.get("name") or "").strip()
        if not name:
            continue
 
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()
 
        if existing:
            action = input(
                f"Contact '{name}' already exists. [S]kip / [O]verwrite? "
            ).strip().lower()
            if action != "o":
                skipped += 1
                continue
            cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing[0],))
            gid = _get_or_create_group(cur, rec.get("group"))
            cur.execute("""
                UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s
            """, (rec.get("email"), rec.get("birthday"), gid, existing[0]))
            cid = existing[0]
            overwritten += 1
        else:
            gid = _get_or_create_group(cur, rec.get("group"))
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, rec.get("email"), rec.get("birthday"), gid))
            cid = cur.fetchone()[0]
            imported += 1
 
        for ph in (rec.get("phones") or []):
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (cid, ph.get("phone"), ph.get("type") or "mobile")
            )
 
    conn.commit(); cur.close(); conn.close()
    print(f"Import done — imported: {imported}, overwritten: {overwritten}, skipped: {skipped}")
 
 
# 8. Extended CSV import
def import_from_csv():
    filename = input("CSV filename [contacts.csv]: ").strip() or "contacts.csv"
 
    try:
        f = open(filename, encoding="utf-8")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return
 
    conn = connect(); cur = conn.cursor()
    imported = invalid = 0
 
    with f:
        reader = csv.DictReader(f)
        for row in reader:
            name     = (row.get("name")     or "").strip()
            phone    = (row.get("phone")    or "").strip()
            ptype    = (row.get("type")     or "mobile").strip()
            email    = (row.get("email")    or "").strip() or None
            birthday = (row.get("birthday") or "").strip() or None
            grp      = (row.get("group")    or "Other").strip()
 
            if not name or not phone:
                invalid += 1
                continue
 
            gid = _get_or_create_group(cur, grp)
 
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()
 
            if existing:
                cur.execute("""
                    UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s
                """, (email, birthday, gid, existing[0]))
            else:
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s)
                """, (name, email, birthday, gid))
 
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
            imported += 1
 
    conn.commit(); cur.close(); conn.close()
    print(f"CSV import done — imported/updated: {imported}, invalid rows: {invalid}")
 
 
# 9. Add phone number to existing contact
def add_phone():
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    print("Type: 1=mobile  2=home  3=work")
    ptype = {"1": "mobile", "2": "home", "3": "work"}.get(input("Choose: ").strip(), "mobile")
 
    conn = connect(); cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("Phone number added.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close(); conn.close()
 
 
# 10. Delete contact
def delete_contact():
    name = input("Enter contact name to delete: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
 
    conn = connect(); cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()
 
        if not existing:
            print(f"Contact '{name}' not found.")
            return
 
        confirm = input(f"Are you sure you want to delete '{name}'? [y/n]: ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return
 
        # phones are deleted automatically via ON DELETE CASCADE
        cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
        conn.commit()
        print(f"Contact '{name}' deleted.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close(); conn.close()
 
 
# 11. Move contact to group
def move_to_group():
    name = input("Contact name: ").strip()
    print("Available groups: Family, Work, Friend, Other (or enter a new one)")
    grp  = input("Group name: ").strip()
 
    conn = connect(); cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, grp))
        conn.commit()
        print(f"Contact '{name}' moved to group '{grp}'.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close(); conn.close()
 
 
# ──────────────────────────────────────────────
# Main menu
# ──────────────────────────────────────────────
 
def menu():
    options = {
        "1":  ("Add contact manually",               add_contact),
        "2":  ("Filter by group",                    filter_by_group),
        "3":  ("Search by email",                    search_by_email),
        "4":  ("General search (name/phone/email)",  general_search),
        "5":  ("Paginated navigation",               paginated_view),
        "6":  ("Export contacts to JSON",            export_to_json),
        "7":  ("Import contacts from JSON",          import_from_json),
        "8":  ("Import contacts from CSV",           import_from_csv),
        "9":  ("Add phone number to contact",        add_phone),
        "10": ("Delete contact",                     delete_contact),
        "11": ("Move contact to group",              move_to_group),
        "0":  ("Exit",                               None),
    }
 
    while True:
        print("\n" + "=" * 55)
        print("  TSIS1: PhoneBook — Extended Contact Management")
        print("=" * 55)
        for key, (label, _) in options.items():
            print(f"  {key}. {label}")
 
        choice = input("\nChoose: ").strip()
 
        if choice == "0":
            print("Goodbye!")
            break
        elif choice in options:
            _, fn = options[choice]
            try:
                fn()
            except KeyboardInterrupt:
                print("\n(cancelled)")   
        else:
            print("Invalid choice, try again.")
 
 
if __name__ == "__main__":
    menu()