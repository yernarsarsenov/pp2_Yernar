-- ============================================================
-- TSIS1: New Stored Procedures & Updated Function
-- (Practice 8 procedures upsert_contact, insert_many_contacts,
--  delete_contact and pagination/search functions are kept as-is;
--  only NEW objects are defined here.)
-- ============================================================

-- 3.4.1  Add a phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR   -- 'home' | 'work' | 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE name = p_contact_name;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home, work, or mobile.', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);
END;
$$;


-- 3.4.2  Move a contact to a group (creates group if missing)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id   INTEGER;
    v_contact_id INTEGER;
BEGIN
    -- Ensure group exists
    INSERT INTO groups (name) VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;


-- 3.4.3  Extended search: name, email, ALL phones, group name
--        Replaces / extends the Practice 8 search_contacts function.
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    phone    VARCHAR,
    ptype    VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.name, ph.phone)
           c.name,
           c.email,
           c.birthday,
           g.name      AS grp,
           ph.phone,
           ph.type     AS ptype
    FROM   contacts c
    LEFT JOIN groups g  ON g.id  = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE  c.name    ILIKE '%' || p_query || '%'
        OR c.email   ILIKE '%' || p_query || '%'
        OR ph.phone  ILIKE '%' || p_query || '%'
        OR g.name    ILIKE '%' || p_query || '%'
    ORDER BY c.name, ph.phone;
END;
$$ LANGUAGE plpgsql;


-- Helper: return all contacts with full details (used by export & list)
CREATE OR REPLACE FUNCTION get_all_contacts_full()
RETURNS TABLE(
    id       INTEGER,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email, c.birthday,
           g.name AS grp, c.created_at
    FROM   contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    ORDER BY c.name;
END;
$$ LANGUAGE plpgsql;


-- Helper: paginated contact list (wraps Practice 8 logic with full fields)
CREATE OR REPLACE FUNCTION get_contacts_paginated_full(p_limit INT, p_offset INT)
RETURNS TABLE(
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.email, c.birthday, g.name AS grp
    FROM   contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    ORDER BY c.name
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
