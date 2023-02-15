from GuidelineService import GuidelineService
from html2text import HTML2Text
from datetime import datetime
import regex

html2text = HTML2Text()
service = GuidelineService()

guideline_list = service.download_guideline_list()
litref_reco_id_list = []
litref_hgt_id_list = []
author_total_list = []

def ParseTextLitref(text):
    result = []
    match_list = text.split("\"id\": ")
    if match_list is not None and len(match_list) > 1:
        for match in match_list[1:]:
            sub_arr = match.split("\",")
            id = sub_arr[0]
            id = id.split("}")[0].replace("\"", "")
            if int(id) not in result:
                result.append(int(id))

    return result

def GetRecommendationLiterature(content):
    for content_element in content['subsections']:
        reco_result = None
        hgt_result = None
        if content_element['type'] == "RecommendationCT":
            reco_result = [x['id'] for x in content_element['literature_references']]
        elif content_element['type'] == "TextCT" and "data-litref_json" in content_element['text']:
            hgt_result = ParseTextLitref(content_element['text'])

        if reco_result is not None and len(reco_result) > 0:
            litref_reco_id_list.extend(reco_result)

        if hgt_result is not None and len(hgt_result) > 0:
            litref_hgt_id_list.extend(hgt_result)

        GetRecommendationLiterature(content_element)

def ParseAuthor(author):
    return ["%s %s" % (author['lastname'], author['firstname']), author['lastname'], author['firstname']]

def GetProfSocAuthorList(prof_soc):
    result = []
    for author in prof_soc['author']:
        result.append(ParseAuthor(author))

    return result

def GetAuthorList(guideline):
    result = []
    for prof_soc in guideline['coordination_editiorial']:
        author = ParseAuthor(prof_soc['author'])
        if author not in result:
            result.append(author)

    for workgroup in guideline['workgroups']:
        for au in workgroup['author_members']:
            author = ParseAuthor(au)
            if author not in result:
                result.append(author)
        for au in workgroup['author_managers']:
            author = ParseAuthor(au)
            if author not in result:
                result.append(author)

    for prof_soc in guideline['involved_professionalsocieties']:
        for au in prof_soc['authors']:
            author = ParseAuthor(au)
            if author not in result:
                result.append(author)
    return result

out_str = "Leitlinie|Version|Jahr|Author|Inhaltstyp|Position|Referenz|Link|Referenzen (gesamt)\n"
out_list = []

author_total_str = "Leitlinie|Version|Jahr|Author\n"

def ParseLitref(litref):
    litref_author_str = ", ".join([x.replace(",", "") for x in litref['au'][0:min(len(litref['au']), 6)]])
    if len(litref['au']) > 6:
        litref_author_str += ", et al."

    result = "%s. %s. %s. %s;%s:%s" % (litref_author_str, litref['title'], litref['periodical_name'], litref['publication_year'], litref['volume_number'], litref['start_page_number'])
    result = result.replace("..", ".")
    return result

for guideline in guideline_list:
    if guideline['guideline_language']['id'] == "de" and guideline['state'] == "published":
        guideline_full = service.download_guideline(guideline['id'], guideline_state="published", load_references=True)
        guideline_date = datetime.fromisoformat(guideline_full["date"].replace("T", " ").replace("Z", ""))

        GetRecommendationLiterature(guideline_full)
        author_list = GetAuthorList(guideline_full)
        author_list.sort(key=lambda x: x[1])

        author_item = ["%s|%s|%s|%s" % (guideline_full['short_title'], "\"%s\"" % guideline_full['published_version'], guideline_date.year, "%s, %s" % (x[1], x[2])) for x in author_list]
        author_total_str += "\n".join(author_item)

        for lit_ref in guideline_full['literature_list']:
            if lit_ref['au'] is None:
                continue

            tag_text = html2text.handle(lit_ref['tag'])

            for guideline_author in author_list:
                author_str = "%s, %s" % (guideline_author[1], guideline_author[2][0])
                if author_str in tag_text:
                    index = -1
                    try:
                        index = lit_ref['au'].index(author_str)
                    except:
                        for i in range(len(lit_ref['au'])):
                            if author_str in lit_ref['au'][i]:
                                index = i
                                break

                    if index == 0:
                        position = "Erstautor"
                    elif index == len(lit_ref['au'])-1:
                        position = "Letztautor"
                    else:
                        position = "Standard"

                    tag = ParseLitref(lit_ref)
                    if lit_ref['user_definable_url'] is not None:
                        url = lit_ref['user_definable_url'].replace("\n", "").replace("\r", "")
                    else:
                        url = ""

                    if lit_ref['id'] in litref_reco_id_list:
                        out_item = "%s|%s|%s|%s|Empfehlung|%s|%s|%s|%s" % (guideline_full['short_title'], "\"%s\"" % guideline_full['published_version'], guideline_date.year, "%s, %s" % (guideline_author[1], guideline_author[2]), position, tag, url, len(guideline_full['literature_list']))
                        if out_item not in out_list:
                            out_list.append(out_item)
                    if lit_ref['id'] in litref_hgt_id_list:
                        out_item = "%s|%s|%s|%s|Hintergrund|%s|%s|%s|%s" % (guideline_full['short_title'], "\"%s\"" % guideline_full['published_version'], guideline_date.year, "%s, %s" % (guideline_author[1], guideline_author[2]), position, tag, url, len(guideline_full['literature_list']))
                        if out_item not in out_list:
                            out_list.append(out_item)

    if "olorektal" in guideline_full['short_title']:
        pass

out_str += "\n".join(out_list)

with open("results.csv", "w", encoding="utf-8") as f:
    f.write(out_str)

with open("authors.csv", "w", encoding="utf-8") as f:
    f.write(author_total_str)