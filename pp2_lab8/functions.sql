CREATE OR REPLACE FUNCTION search_contacts(p TEXT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT n.id, n.first_name, n.last_name, n.phone
        FROM phone_nums n
        WHERE n.first_name ILIKE '%' || p || '%'
           OR n.last_name  ILIKE '%' || p || '%'
           OR n.phone      ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(lim INT, off INT)
RETURNS TABLE(id INT, first_name VARCHAR, last_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT n.id, n.first_name, n.last_name, n.phone
        FROM phone_nums n
        ORDER BY n.id
        LIMIT lim OFFSET off;
END;
$$ LANGUAGE plpgsql;