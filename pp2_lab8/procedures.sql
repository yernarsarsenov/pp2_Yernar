CREATE TABLE IF NOT EXISTS invalid_contacts (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255),
    last_name  VARCHAR(255),
    phone      VARCHAR(50)
);

CREATE OR REPLACE PROCEDURE upsert_contact(
    p_first VARCHAR, p_last VARCHAR, p_phone VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phone_nums WHERE first_name = p_first) THEN
        UPDATE phone_nums SET phone = p_phone WHERE first_name = p_first;
    ELSE
        INSERT INTO phone_nums(first_name, last_name, phone)
        VALUES(p_first, p_last, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_firsts TEXT[], p_lasts TEXT[], p_phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i     INT;
    phone TEXT;
BEGIN
    DELETE FROM invalid_contacts;
    FOR i IN 1..array_length(p_firsts, 1) LOOP
        phone := p_phones[i];
        IF (
            (phone LIKE '+7%' AND length(phone) = 12 AND substring(phone, 2) ~ '^[0-9]+$')
            OR
            (phone LIKE '8%'  AND length(phone) = 11 AND phone ~ '^[0-9]+$')
        ) THEN
            INSERT INTO phone_nums(first_name, last_name, phone)
            VALUES(p_firsts[i], p_lasts[i], phone);
        ELSE
            INSERT INTO invalid_contacts(first_name, last_name, phone)
            VALUES(p_firsts[i], p_lasts[i], phone);
        END IF;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_value LIKE '+%' OR p_value ~ '^[0-9]+$' THEN
        DELETE FROM phone_nums WHERE phone = p_value;
    ELSE
        DELETE FROM phone_nums WHERE first_name = p_value;
    END IF;
END;
$$;