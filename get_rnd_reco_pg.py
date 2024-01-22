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

relevant_topic_list = [
    "Epidemiology / Risikofaktoren",
    "Diagnose",
    "Screening/Biopsie",
    "Behandlung",
    "Reha/FollowUp",
    "Psychoonkologie",
    "Palliativ"
]

topic_dict = {
    "Diagnose": [
        "Untersuchung",
        "Feststellen",
        "Labor",
        "Bildgebend",
        "Diagnos"
    ],
    "Screening/Biopsie": [
        "Screening",
        "Vorsorgeuntersuchung",
        "Gewebeprobe",
        "Vorsorge",
        "Pathologie",
        "Biopsie",
        "Histologie",
        "Zytologie",
        "Früherkennung",
        "Stadium",
        "Material"
    ],
    "Reha/FollowUp": [
        "Reha",
        "Follow",
        "Nachsorge",
        "Nachbehandlung",
        "Langzeitbetreuung",
        "Therapiebegleitung",
        "Erholung",
        "Gesundheitsmanagement",
        "Reintegrationsprogramm",
        "Langzeitüberwachung",
        "Nachtherapie",
    ],
    "Behandlung" : [
        "Therapie",
        "Metastasiert",
        "Behandlung",
    ],
    "Palliativ" : [
        "Palliativ",
        "Symptomlinderung",
        "Lebensqualität",
        "Schmerzmanagement",
        "Hospiz",
        "End-of-Life",
        "end of life"
        "Komfortpflege",
        "Lebensbegleitung",
        "Sterbebegleitung"
    ],
    "Psychoonkologie": [
        "Psycho",
        "Emotional",
        "Stress",
        "Psychisch",
        "Angst",
        "Depression",
        "Bewältigung",
        "Kommunikation",
        "Patientenbetreuung",
        "Seelisch",
    ],
    "Epidemiology / Risikofaktoren": [
        "Epidemiolog",
        "Risikofaktoren",
        "Krebshäufigkeit",
        "Krebsrisiko",
        "Prävalenz",
        "Inzidenz",
        "Risikofaktor",
        "Statistik",
        "Erkrankungswahrscheinlichkeit",
        "Prädisposition",
        "Risikogruppe",
        "Lebensstilfaktoren",
        "Genetische Faktoren",
        "Umweltfaktoren",
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

reco_result = []
def get_recos(guideline_data):
    cur = conn.cursor()

    cur.execute(sql.SQL("SELECT * FROM {table} WHERE {key} = '%s'" % guideline_data[0]).format(
        table=sql.Identifier("ll_recommendations"),
        key = sql.Identifier("ll_uid")))

    reco_rows = cur.fetchall()
    cur.close()
    return reco_rows

def get_next_reco(topic, recos):
    attempt = 0
    topic_keyword_list = topic_dict[topic]
    while attempt < len(recos):
        rnd_reco = recos[random.randint(0, len(recos) - 1)]
        reco_text = rnd_reco[6]
        if any([x.lower() in reco_text.lower() for x in topic_keyword_list]):
            return rnd_reco
        attempt += 1

    return None

for row in rows:
    recos[row[0]] = get_recos(row)

guideline_index = -1
topic_index = 0
while len(reco_result) < N_RECO:
    guideline_index += 1
    if guideline_index >= len(rows):
        guideline_index = 0
        topic_index += 1
        if topic_index >= len(topic_dict):
            topic_index = 0

    guideline_topic_list = list(topic_dict.keys())
    guideline_topic = guideline_topic_list[topic_index]

    next_reco = get_next_reco(guideline_topic, recos[rows[guideline_index][0]])

    if next_reco is not None:
        buffer = list(next_reco)
        buffer.insert(0, rows[guideline_index][1])
        buffer.insert(1, guideline_topic)
        next_reco = tuple(buffer)
        reco_result.append(next_reco)
    else:
        print("No more recommendations in guideline %s with topic %s" % (rows[guideline_index][1], guideline_topic))

pass



