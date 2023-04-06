import openai
from io import StringIO
from textwrap import wrap
import PyPDF4
import nltk

openai.api_key = "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"
model_engine = "text-davinci-003"
model_engine = "gpt-3.5-turbo"
output_string = ""


pdf_filepath = "//dkg-dc-01/Daten/Daten/Arbeitsverzeichnisse/OL/HTA Dokumente/Publikationen nach Entität/HCC/AbouAlfa et al. 2020 - ClarIDHy.pdf"
fp = open(pdf_filepath, "rb")
pdfreader = PyPDF4.PdfFileReader(fp)
page_count = pdfreader.numPages

for i in range(page_count):
    page_obj = pdfreader.getPage(i)
    output_string += page_obj.extractText()

study_text_list = wrap(output_string, int(1024))

def send_message(message):
    chat = openai.ChatCompletion.create(
        model=model_engine,
        messages=[ {"role": "user", "content": message} ]
    )

    return chat

send_message("Please consider this study publication, do not respond until study entry is finished, indicated by 'entry finished.")
for message in study_text_list:
    send_message(message)

reply = send_message("Entry finished. Assess the quality of the study and for each endpoint using the GRADE methodology. Provide evidence table and summary of findings table. Justify each quality rating using footnotes")

response = reply.choices[0]
print(response.message)