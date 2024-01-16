
import deepl

API_KEY = "ea75bedb-ef52-b4dc-dceb-e6aa9e2e7127"

translator = deepl.Translator(API_KEY)

result = translator.translate_text("Die AWMF, die Deutsche Krebsgesellschaft e.V. und die Deutsche Krebshilfe haben sich mit dem im Februar 2008 gestarteten Leitlinienprogramm Onkologie das Ziel gesetzt, gemeinsam die Entwicklung und Fortschreibung und den Einsatz wissenschaftlich begründeter und praktikabler Leitlinien in der Onkologie zu fördern und zu unterstützen.", target_lang="ES")
print(result.text)