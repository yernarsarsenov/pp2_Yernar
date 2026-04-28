-- Procedure to add a new phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id FROM contacts 
    WHERE first_name = p_first_name AND last_name = p_last_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact % % not found', p_first_name, p_last_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;

-- Procedure to move a contact to a different group; creates the group if it does not exist
CREATE OR REPLACE PROCEDURE move_to_group(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
    v_contact_id INTEGER;
BEGIN
    -- Get or create group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;

    -- Get contact
    SELECT id INTO v_contact_id FROM contacts 
    WHERE first_name = p_first_name AND last_name = p_last_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact % % not found', p_first_name, p_last_name;
    END IF;

    -- Update contact
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

-- Function to search contacts matching email, name, or any of their phones
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INTEGER,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id, 
        c.first_name, 
        c.last_name, 
        c.email, 
        c.birthday, 
        g.name as group_name,
        string_agg(p.phone || ' (' || p.type || ')', ', ') as phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE 
        c.first_name ILIKE '%' || p_query || '%' OR
        c.last_name ILIKE '%' || p_query || '%' OR
        c.email ILIKE '%' || p_query || '%' OR
        c.id IN (SELECT contact_id FROM phones WHERE phone ILIKE '%' || p_query || '%')
    GROUP BY c.id, g.name;
END;
$$;

-- Paginated query function (adapted for new schema)
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INTEGER, p_offset INTEGER)
RETURNS TABLE (
    id INTEGER,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    phones TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id, 
        c.first_name, 
        c.last_name, 
        c.email, 
        c.birthday, 
        g.name as group_name,
        string_agg(p.phone || ' (' || p.type || ')', ', ') as phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    GROUP BY c.id, g.name
    ORDER BY c.first_name, c.last_name
    LIMIT p_limit OFFSET p_offset;
END;
$$;
