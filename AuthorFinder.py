from GuidelineService import GuidelineService
from html2text import HTML2Text
from datetime import datetime
import regex

html2text = HTML2Text()
service = GuidelineService()

guideline_list = service.download_guideline_list()
litref_reco_id_dict = {}
litref_hgt_id_list = []
author_total_list = []
litref_qi_reco_id_list = []

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

def get_reco_type(reco):
    if 'type_of_recommendation' in reco and reco['type_of_recommendation'] is not None and 'name' in reco['type_of_recommendation'] and reco['type_of_recommendation']['name'] is not None:
        return reco['type_of_recommendation']['name']
    else:
        return ""
def get_GOR(reco):
    result = ""
    if len(reco['recommendation_grade']) > 0:
        if 'tite' in reco['recommendation_grade'] and reco['recommendation_grade']['title'] is not None:
            result = reco['recommendation_grade']['title']

    if result == "":
        if "sollte" in reco['text']:
            return "B"
        elif "soll" in reco['text']:
            return "A"
        elif "kann" in reco['text'] or "können" in reco['text']:
            return "0"
        else:
            if "statement" not in reco['type_of_recommendation']['id']:
                pass
            return ""
    else:
        return result

def GetRecommendationLiterature(content):
    for content_element in content['subsections']:
        reco_result = None
        hgt_result = None
        if content_element['type'] == "RecommendationCT":
            reco_result = [x['id'] for x in content_element['literature_references']]
            for litref_id in reco_result:
                if litref_id not in litref_reco_id_dict:
                    litref_reco_id_dict[litref_id] = []
                if content_element not in litref_reco_id_dict[litref_id]:
                    litref_reco_id_dict[litref_id].append(content_element)
        elif content_element['type'] == "TextCT" and "data-litref_json" in content_element['text']:
            hgt_result = ParseTextLitref(content_element['text'])
        elif content_element['type'].lower() == "qualityindicatorct":
            if content_element['reference_recommendations'] is not None:
                for j in range(0, len(content_element['reference_recommendations'])):
                    reco = content_element['reference_recommendations'][j]
                    litref_qi_reco_id_list.append(reco['uid'])

        #if reco_result is not None and len(reco_result) > 0:
        #    litref_reco_id_dict.extend(reco_result)

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

out_str = "Leitlinie|Version|Jahr|Author|Inhaltstyp|Bester GoR|in QI|Position|Referenz|Link|Referenzen (gesamt)\n"
out_list = []

author_total_str = "Leitlinie|Version|Jahr|Author\n"

def ParseLitref(litref):
    litref_author_str = ", ".join([x.replace(",", "") for x in litref['au'][0:min(len(litref['au']), 6)]])
    if len(litref['au']) > 6:
        litref_author_str += ", et al."

    result = "%s. %s. %s. %s;%s:%s" % (litref_author_str, litref['title'], litref['periodical_name'], litref['publication_year'], litref['volume_number'], litref['start_page_number'])
    result = result.replace("..", ".")
    return result

def get_best_reco(reco_list):
    best_reco = reco_list[0]
    best_reco_gor = get_GOR(reco_list[0])
    if len(reco_list) > 1:
        for k in range(1, len(reco_list)):
            reco = reco_list[k]
            gor = get_GOR(reco)
            if len(gor) > 0:
                if "A" in gor and ("B" in best_reco_gor or "0" in best_reco_gor):
                    best_reco = reco
                    best_reco_gor = gor
                elif "B" in gor and "0" in best_reco_gor:
                    best_reco = reco
                    best_reco_gor = gor
                elif "0" in gor and best_reco_gor != "A" and best_reco_gor != "B":
                    best_reco = reco
                    best_reco_gor = gor

    return [best_reco, best_reco_gor]

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

                    if lit_ref['id'] in litref_reco_id_dict:
                        [reco, gor] = get_best_reco(litref_reco_id_dict[lit_ref['id']])
                        reco_type = get_reco_type(reco)
                        in_qi = reco['uid'] in litref_qi_reco_id_list
                        out_item = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (guideline_full['short_title'], "\"%s\"" % guideline_full['published_version'], guideline_date.year, "%s, %s" % (guideline_author[1], guideline_author[2]), reco_type, gor, in_qi, position, tag, url, len(guideline_full['literature_list']))
                        if out_item not in out_list:
                            out_list.append(out_item)

                    if lit_ref['id'] in litref_hgt_id_list:
                        out_item = "%s|%s|%s|%s|Hintergrund|||%s|%s|%s|%s" % (guideline_full['short_title'], "\"%s\"" % guideline_full['published_version'], guideline_date.year, "%s, %s" % (guideline_author[1], guideline_author[2]), position, tag, url, len(guideline_full['literature_list']))
                        if out_item not in out_list:
                            out_list.append(out_item)

    if "olorektal" in guideline_full['short_title']:
        pass

out_str += "\n".join(out_list)

with open("results.csv", "w", encoding="utf-8") as f:
    f.write(out_str)

with open("authors.csv", "w", encoding="utf-8") as f:
    f.write(author_total_str)