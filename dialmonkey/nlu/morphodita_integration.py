import requests

def lemmatize_string(input_string: str) -> str:
    r = requests.get(f"http://lindat.mff.cuni.cz/services/morphodita/api/tag?data={input_string}&convert_tagset=pdt_to_conll2009&output=json")
    response = r.json()["result"]
    lemmas = []
    for sentence in response:
        for word in sentence:
            lemmas.append(word["lemma"])
    return ' '.join(lemmas)