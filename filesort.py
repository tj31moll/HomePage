import requests
import json
from requests.structures import CaseInsensitiveDict
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize
import string
from gensim import corpora
from gensim.models.ldamodel import LdaModel

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# OneNote API functions
def create_page(access_token, section_id, content):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {access_token}"

    data = {
        "title": "Sorted notes",
        "content": f"<html><head><title>Sorted notes</title></head><body>{content}</body></html>",
    }

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages",
        headers=headers,
        data=json.dumps(data),
    )

    if response.status_code == 201:
        print("Page created successfully")
    else:
        print("Error creating page:", response.text)

def get_sections(access_token):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {access_token}"

    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/onenote/sections",
        headers=headers,
    )

    if response.status_code == 200:
        sections = response.json()["value"]
        return sections
    else:
        print("Error fetching sections:", response.text)
        return None

# Text preprocessing function
def preprocess(text):
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation)
    lemma = WordNetLemmatizer()

    def clean(doc):
        stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        punc_free = "".join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
        return normalized

    return clean(text)

# Text sorting function using LDA
def sort_text(text, num_topics=3):
    preprocessed_text = preprocess(text)

    # Tokenize the preprocessed text
    tokens = [word_tokenize(doc) for doc in preprocessed_text]

    # Create a dictionary and corpus for LDA
    dictionary = corpora.Dictionary(tokens)
    corpus = [dictionary.doc2bow(token) for token in tokens]

    # Train the LDA model
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=50)

    # Sort the text into topics
    sorted_data = {f"Topic {i}": [] for i in range(1, num_topics + 1)}
    for i, topic in enumerate(lda_model.show_topics(formatted=False, num_words=5)):
        sorted_data[f"Topic {i + 1}"] = [word[0] for word in topic[1]]

    # Create a formatted string to represent the sorted data as bullet points
    formatted_data = ""
    for topic, items in sorted_data.items():
        formatted_data += f"<h3>{topic}</h3><ul>"
        for item in items:
            formatted_data += f"<li>{item}</li>"
        formatted_data += "</ul>"

    return formatted_data

# Main function to read the text, sort it, and upload it to OneNote
def main():
    access_token = "YOUR_ACCESS_TOKEN"  # Replace with your access token
    section_id = "YOUR_SECTION_ID"  # Replace with your target section ID

    # Read the text from the file or UI
    with open("input.txt", "r") as file:
        text = file.read()

    # Sort the text into categories using LDA
    sorted_data = sort_text(text, num_topics=3)

    # Create a new page in OneNote with the sorted data
    create_page(access_token, section_id, sorted_data)

if __name__ == "__main__":
    main()
