from GuidelineService import GuidelineService

service = GuidelineService()

guideline_list = service.download_guideline_list()

qi_count = 0
qi_with_refs_count = 0
au_in_qi = 0
au_list = []

for guideline in [x for x in guideline_list if x['state'] == "published" and x['guideline_language']['id'] == "de"]:
    qi_list = service.download_quality_indicators(guideline['id'], guideline_state=guideline['state'])['content_by_type']
    qi_count += len(qi_list)
    ref_count = 0
    for qi in qi_list:
        for reco in qi['reference_recommendations']:
            if reco['literature_references'] is not None and len(reco['literature_references']) > 0:
                qi_with_refs_count += 1
                for litref in reco['literature_references']:
                    ref_count += 1
                    if litref['au'] is not None:
                        for au in litref['au']:
                            if au not in au_list:
                                au_list.append(au)
    print("#QI: %s, #QI with refs: %s, #AU in QI: %s, #LitRefs in guideline: %s" % (qi_count, qi_with_refs_count, len(au_list), ref_count))
    pass