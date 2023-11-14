import urllib.request
import json
import tempfile
from os import path

class GuidelineService:

    def __init__(self):
        self.SERVER_URL = "https://backend.leitlinien.krebsgesellschaft.de/"

    def download_guideline_list(self, state="published"):
        url = self.SERVER_URL + "get_guidelines?version_id=%s" % state

        with urllib.request.urlopen(url) as url_request:
            json_data = json.loads(url_request.read().decode())

        return json_data

    def download_guideline(self, guideline_id, guideline_state="published", load_references=True, use_stage=False):
        if not use_stage:
            url = self.SERVER_URL + "get_guideline?id=%s&version_id=%s" % (guideline_id, guideline_state)
        else:
            url = "https://backend.llo.stage.interaktiv.de/get_guideline?id=%s&version_id=%s" % (guideline_id, guideline_state)

        print("Downloading %s" % url)
        guideline_str = ""
        with urllib.request.urlopen(url) as url_request:
            guideline_str = url_request.read().decode()

        file_path = path.join(tempfile.gettempdir(), "%s_%s.json" % (guideline_id, guideline_state))
        with open(file_path, "w", encoding="utf-8") as guideline_file:
            guideline_file.write(guideline_str)

        json_data = json.loads(guideline_str)
        if load_references:
            json_data['literature_list'] = self.download_literature(json_data['uid'])
            json_data['literature_index'] = None
            json_data['literature'] = None
        return json_data

    def download_literature(self, guideline_uid):
        url = self.SERVER_URL + "get_literature?uid=%s" % guideline_uid
        literature_str = ""
        with urllib.request.urlopen(url) as url_request:
            literature_str = url_request.read().decode()

        json_data = json.loads(literature_str)
        return json_data

    def load_guideline(self, guideline_id, guideline_state="published", load_references=False):
        from os import path
        file_path = path.join(tempfile.gettempdir(), "%s_%s.json" % (guideline_id, guideline_state))
        if path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as guideline_file:
                json_data = json.load(guideline_file)
                if load_references:
                    json_data['literature_list'] = self.download_literature(json_data['uid'])
                    json_data['literature_index'] = None
                    json_data['literature'] = None

                return json_data
        else:
            print("Die Datei %s existiert nicht. Bitte starten sie das Programm erneut ohne die Option 'local'." % file_path)
            exit(-1)

    def load_recommendations(self, guideline_id, guideline_state):
        from os import path
        file_path = path.join(tempfile.gettempdir(), "%s_%s_recommendations.json" % (guideline_id, guideline_state))
        if path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as guideline_file:
                return json.load(guideline_file)
        else:
            print("Die Datei %s existiert nicht. Bitte starten sie das Programm erneut ohne die Option 'local'." % file_path)
            exit(-1)

    def download_evidence_tables(self, guideline_id, guideline_state="private"):
        url = self.SERVER_URL + "get_guideline_portaltype?guideline_id=%s&portal_type=EvidenceTableCT&version_id=%s" % (guideline_id, guideline_state)
        print("Downloading %s" % url)

        with urllib.request.urlopen(url) as url_request:
            json_data = json.loads(url_request.read().decode())

        return json_data

    def download_recommendations(self, guideline_id, guideline_state):
        url = self.SERVER_URL + "get_guideline_portaltype?guideline_id=%s&portal_type=RecommendationCT&version_id=%s" % (guideline_id, guideline_state)
        print("Downloading %s" % url)

        with urllib.request.urlopen(url) as url_request:
            json_data = json.loads(url_request.read().decode())

        return json_data

    def download_quality_indicators(self, guideline_id, guideline_state):
        url = self.SERVER_URL + "get_guideline_portaltype?guideline_id=%s&portal_type=QualityIndicatorCT&version_id=%s" % (guideline_id, guideline_state)
        print("Downloading %s" % url)

        with urllib.request.urlopen(url) as url_request:
            request_string = url_request.read().decode()
            '''
            if "data-litref_json=" in request_string:
                print("Literature references found!")
            else:
                print("NO literature references found.")
            '''
            json_data = json.loads(request_string)

        return json_data