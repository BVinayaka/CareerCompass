import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjk0NzQyNTctOWY4Yy00Y2I0LWE5Y2UtMjNhM2Q5ZDM4ZTRhIiwidHlwZSI6ImFwaV90b2tlbiJ9.Hc9nYSzzt5thtOWuWq5Kr14wD0nixZdO7ODBheS3lLE"
}
url = "https://api.edenai.run/v2/text/question_answer"

def chat(question):
    text1 = "I need information related to resume building"
    text2 = "Please give me information related to resume builder  only"

    payload = {
        "providers": "openai",
        "texts": [text1, text2],
        "question": question,
        "examples_context": "In 2017, U.S. life expectancy was 78.6 years.",
        "examples": [["What is human life expectancy in the United States?", "78 years."]],
        "fallback_providers": "gpt-3.5-turbo"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        answer = result['openai']['answers'][0]
    else:
        answer = "Sorry, something went wrong."

    return answer

if __name__ == '__main__':
    question = input("Please enter your question: ")
    answer = chat(question)
    print("Answer:", answer)
