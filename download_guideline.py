from GuidelineService import GuidelineService
from os import path
from datetime import datetime
import shutil

import tempfile
import pandas as pd


service = GuidelineService()

guideline_id = "s3-leitlinie-diagnostik-therapie-und-nachsorge-des-nierenzellkarzinoms"
guideline_id = "supportive-therapie-bei-onkologischen-patientinnen"
guideline_id = "diagnostik-und-therapie-des-hepatozellulaeren-karzinoms"
guideline_state = "archived"

current_date = datetime.now()
guideline_live = service.download_guideline(guideline_id, guideline_state=guideline_state, load_references=True, use_stage=False)
download_sec = (datetime.now() - current_date).seconds
print("Download took %s seconds" % download_sec)

local_path = path.join(tempfile.gettempdir(), "%s_%s.json" % (guideline_id, guideline_state))
shutil.copyfile(local_path, "./Guidelines/%s_%s_live_%s.json" % (guideline_id, guideline_state, download_sec))

current_date = datetime.now()
guideline_stage = service.download_guideline(guideline_id, guideline_state=guideline_state, load_references=True, use_stage=True)
download_sec = (datetime.now() - current_date).seconds
print("Download took %s seconds" % download_sec)

local_path = path.join(tempfile.gettempdir(), "%s_%s.json" % (guideline_id, guideline_state))
shutil.copyfile(local_path, "./Guidelines/%s_%s_stage_%s.json" % (guideline_id, guideline_state, download_sec))

def json_diff(json1, json2, path=""):
    diff = []
    for k in json1.keys():
        if k not in json2:
            diff.append((f"{path}/{k}", json1[k], None))
        elif isinstance(json1[k], dict):
            diff.extend(json_diff(json1[k], json2[k], path=f"{path}/{k}"))
        elif isinstance(json1[k], list):
            if len(json1[k]) != len(json2[k]):
                diff.append((f"{path}/{k}", json1[k], json2[k]))
            else:
                for i in range(len(json1[k])):
                    if isinstance(json1[k][i], (dict, list)):
                        diff.extend(json_diff(json1[k][i], json2[k][i], path=f"{path}/{k}/{i}"))
                    elif json1[k][i] != json2[k][i]:
                        diff.append((f"{path}/{k}/{i}", json1[k][i], json2[k][i]))
        elif json1[k] != json2[k]:
            diff.append((f"{path}/{k}", json1[k], json2[k]))

    for k in json2.keys():
        if k not in json1:
            diff.append((f"{path}/{k}", None, json2[k]))
    return diff


def compare_jsons(output):
    diff = json_diff(guideline_live, guideline_stage)
    df = pd.DataFrame(diff, columns=['Key', 'Value1', 'Value2'])
    df.to_csv(output, index=False)


# use it like this:
compare_jsons("./Guidelines/%s_%s_diff.csv" % (guideline_live['short_title'], guideline_state))
