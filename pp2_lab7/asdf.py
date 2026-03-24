import psycopg2

conn = psycopg2.connect(dbname = "name", user = "yerlan", password = "2008yernar", host = "127.0.0.1", port = "5432")
print("Connection established")
conn.close()