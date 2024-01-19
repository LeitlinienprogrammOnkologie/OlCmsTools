import psycopg2
import random
from psycopg2 import sql
from configparser import ConfigParser

config = ConfigParser()
config.read("db.ini")

N_RECO = 100

pg_host = config.get("PGSQL", "host")
pg_db = config.get("PGSQL", "database")
pg_user = config.get("PGSQL", "user")
pg_pwd = config.get("PGSQL", "password")

topic_dict = {
    "Diagnose": [ "Untersuchung",
        "Diagnostizieren",
        "Feststellen",
        "Diagnostische Verfahren",
        "Labor",
        "Pathologie",
        "Gewebeprobe",
        "Bildgebend",
        "Biopsie",
        "Histologie",
        "Zytologie",
        "Screening",
        "Früherkennung",
        "Stadium",
    ]
}

conn = psycopg2.connect(
    host=pg_host,
    database=pg_db,
    user=pg_user,
    password=pg_pwd)

cur = conn.cursor()
cur.execute("SELECT uid, short_title FROM ll_data WHERE state = 'published'")
rows = cur.fetchall()
cur.close()

recos = {}

result = []
def get_recos(guideline_data):
    cur = conn.cursor()

    cur.execute(sql.SQL("SELECT * FROM {table} WHERE {key} = '%s'" % guideline_data[0]).format(
        table=sql.Identifier("ll_recommendations"),
        key = sql.Identifier("ll_uid")))

    reco_rows = cur.fetchall()
    cur.close()
    return reco_rows

for i in range(N_RECO):
    guideline_index = i % len(rows)
    guideline_topic_list = list(topic_dict.keys())
    guideline_topic_index = i % len(guideline_topic_list)
    guideline_topic = guideline_topic_list[guideline_topic_index]
    if rows[guideline_index][0] not in recos:
        recos[rows[guideline_index][0]] = get_recos(rows[guideline_index])

    rnd_reco = recos[rows[guideline_index][0]][random.randint(0, len( recos[rows[guideline_index][0]])) - 1]
    while rnd_reco in result:
        rnd_reco = recos[rows[guideline_index][0]][random.randint(0, len(recos[rows[guideline_index][0]])) - 1]

    for k, v in topic_dict.items():
        if any([x in rnd_reco[6] for x in v]):
            pass
    buffer = list(rnd_reco)
    buffer.insert(0, rows[guideline_index][1])
    rnd_reco = tuple(buffer)
    result.append(rnd_reco)

pass



