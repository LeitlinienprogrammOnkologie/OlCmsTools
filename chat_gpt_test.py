import openai

openai.api_key = "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"
model_engine = "text-davinci-003"

prompt = "How dows lightning work?"

completion = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=4096,
    n=1,
    stop=None,
    temperature=0.5,
)

response = completion.choices[0].text
print(response)