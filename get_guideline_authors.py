from GuidelineService import GuidelineService

service = GuidelineService()

guideline_id = "kopie-interdisziplina-re-leitlinie-der-qualita-t"
state = "private"

guideline = service.download_guideline(guideline_id, guideline_state=state, load_references=False)

def get_json_attrib(parent, element_name):
    if element_name in parent and parent[element_name] is not None:
        return parent[element_name]
    else:
        return None

out_txt = "Mandatsträger:\n"
for prof_soc in guideline['involved_professionalsocieties']:
    if get_json_attrib(prof_soc, "authors") is not None:
        for author in get_json_attrib(prof_soc, "authors"):
            au_name = "%s %s (%s) für: %s\n" % (author['firstname'], author['lastname'], author['author_email'], prof_soc['professionalsociety']['title'])
            out_txt += au_name

out_txt += "\nArbeitsgruppen:\n"

for workgroup in guideline['workgroups']:
    out_txt +="- %s:\n" % workgroup['title']
    if get_json_attrib(workgroup, 'author_managers') is not None:
        for author in get_json_attrib(workgroup, 'author_managers'):
            au_name = "-- Leitung: %s %s (%s)\n" % (author['firstname'], author['lastname'], author['author_email'])
            out_txt += au_name
    if get_json_attrib(workgroup, 'author_members') is not None:
        for author in get_json_attrib(workgroup, 'author_members'):
            au_name = "-- Mitglied: %s %s (%s)\n" % (author['firstname'], author['lastname'], author['author_email'])
            out_txt += au_name

pass


