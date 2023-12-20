from GuidelineService import GuidelineService
from urllib import request
import os

service = GuidelineService()

guideline_list = service.download_guideline_list(state="private")

for guideline in guideline_list:
    try:
        guideline = service.download_guideline(guideline['id'], guideline_state="private", load_references=False)
    except:
        pass
    print(guideline['short_title'])
    if 'lead_assosication' not in guideline or guideline['lead_assosication'] is None:
        continue

    for lead_profsoc in guideline['lead_assosication']:
        logo = lead_profsoc['logo']
        logo_filename = logo['filename']
        logo_url = logo['url']
        local_path = os.path.join("logos", logo_filename)
        if not os.path.exists(local_path):
            print("%s -> %s" % (logo_url, local_path))
            request.urlretrieve(logo_url, local_path)

print("DONE")