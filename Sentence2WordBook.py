"""
Author: srjoy5000
Using googletrans==3.1.0a0 instead of 4.0.0-rc1 to avoid errors
"""


import spacy
import json
import os
import pandas as pd
import copy
import re
from googletrans import Translator
from datetime import datetime

JSON_PATH = "data.json"
EXCEL_PATH = "wordbook.xlsx"
print_output = True
target_languages = {
    'en': 'ENGLISH',
    'fr': 'FRENCH',
    'pt': 'PORTUGUESE',
    'ja': 'JAPANESE',
}
target_POS = {
    "NOUN": "nouns",
    "VERB": "verbs",
    "ADJ": "adjectives",
    "ADV": "adverbs",
    # "AUX": "auxiliary" # not recommended
}

# MODELS = {
#     'en': 'en_core_web_sm',
#     'fr': 'fr_core_news_sm',
#     'pt': 'pt_core_news_sm',
#     'ja': 'ja_core_news_sm',
# }
MODELS = {
    'en': 'en_core_web_md',
    'fr': 'fr_core_news_md',
    'pt': 'pt_core_news_md',
    'ja': 'ja_core_news_md',
}

data_structure = {
    "new_words": {},
    "sent_translations": {},
    "source_sentence": {},
    "created_at": "",
    "notes": ""
}


translator = Translator()  # Create an instance of the Translator

# input_string = "Bonjour, comment ça va?"
# input_string = "J’ai vu un chien courir dans le parc."
# input_string = "Sucessor espiritual de Ghost of Tsushima está com grande desconto ao usar Cupom exclusivo"
# input_string = "Os preços e ofertas mencionados são válidos no momento da publicação e podem mudar sem aviso prévio."
# input_string = "This is the first sentence. Here is another one!"
# input_string = "This is the first movie. There will be another one!"
# input_string = "Ela está cansada e quer dormir."
# input_string = "Com esses 10 jogos ideais para festas, você tem em mãos uma “caixa de ferramentas” perfeita para animar qualquer encontro de amigos, desde aquela entrada mais leve até o auge da festa. Há opções para levantar todo mundo, para trocas rápidas, para competir e para rir juntos!"
input_string = """Dans moins d'une heure, Donald Trump reçoit Volodymyr Zelensky dans son bureau de la Maison Blanche,à Washington. Les missiles Tomahawk,l'utilisationde cette arme de longue portée sera au centre des discussions entre le président américain et le président ukrainien.

Dans cette édition,aussi, une nouvelle page de l'histoire de Madagascar s'est ouverte après la fuite à l'étranger d'Andry Rajoelina.Lecolonel Randrianirinaestle nouveau président malgache.

Nous sommes,aussi,au Proche-Orient,pour parler d'un sujet sensible. Après l'accord entre Israël et le Hamas, comment rendre le reste des corps sans vie ?Ce qu'on appelle une dépouille. Nous serons à Ramallah."""
input_string = """Every week it seems US financial markets are hit by another bout of fear.
The latest worries spread this week from the banking sector in the US, after two regional lenders warned they would be hit by losses from alleged fraud.
But before that, markets swooned over signs of rekindled US-China tensions, as the two superpowers face off over tariffs, advanced technology and access to rare earths.
The bankruptcies of car parts supplier First Brands and subprime car lender Tricolor acted as a trigger for nervous chatter in September.
Over the last month, US shares, which had been climbing since their tariff-induced rout in April, have flattened.
But in many ways the market swings so far - down roughly 3% at the steepest - are not unusual.
Zooming out, the major indexes have still posted gains since the start of the year, with the S&P 500 up roughly 13%. That's smaller than 2024 but still solid.
"The market has done surprisingly well so far this year ... driven by an improvement in corporate profits and the enthusiasm surrounding AI," says Sam Stovall, chief investment strategist at CFRA Research."""


def load_data(file_path=JSON_PATH):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}


def save_data(file_path=JSON_PATH, data=None):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# take the JSON and export it to an Excel file
def export_table(file_path=JSON_PATH, pos_list=target_POS.values()):
    data = load_data(file_path)  # get the saved data from JSON
    data_list = [v | {"index": k} for k, v in data.items()]
    with pd.ExcelWriter(EXCEL_PATH, engine='xlsxwriter') as writer:
        df = pd.json_normalize(data_list, sep="_")
        for col in df.columns:
            df[col] = df[col].apply(lambda x: ", ".join(
                x) if isinstance(x, list) else x)
        df = df[[
            "index",
            "new_words_en",
            "new_words_fr",
            "new_words_ja",
            "new_words_pt",
            "sent_translations_en",
            "sent_translations_fr",
            "sent_translations_ja",
            "sent_translations_pt",
            "source_sentence_en",
            "source_sentence_fr",
            "source_sentence_ja",
            "source_sentence_pt",
            "created_at",
            "notes"
        ]]
        df.to_excel(writer, index=False)
        if print_output:
            print(
                f"{"="*150}\n{df}\n{"="*150}")


def search_same_word(word, lemma, pos_name):
    m = re.search(r"\(([^:()]+):\s*([^()]+)\)", word)
    if m:
        l, p = m.group(1).strip(), m.group(2).strip()
        if l == lemma and p == pos_name:
            return True
    return False


def get_word_list(doc, lang, data) -> list:
    new_words = []
    for token in doc:
        if token.pos_ in target_POS.keys():  # choose only noun, verb, adj, adv
            lemma = token.lemma_.lower()
            pos_name = target_POS[token.pos_]
            # Check duplication: add word if there are any duplicates
            if not any([True for id in data for word in data[id]
                        ["new_words"][lang] if search_same_word(word, lemma, pos_name)]):
                new_words.append(f"{token.text} ({lemma}: {pos_name})")
    return new_words


"""
まず、detected_langでモデル読み込み、文に分ける。そしてそれぞれの文に対して他の言語で訳を作る。
それぞれの言語での訳文に対しnlpでtokenizeする。
文ごとのエントリーにそれぞれの言語でのnew_wordsのリストと、訳文を登録する。

あと、もし新しいワードリストがすべての言語で空だったら、その文はどうする？No new words for sentence とする
入力したうち、データと同じ文があれば、それは登録しない。
"""


def process_text(input_text, target_langs=target_languages.keys()):
    input_text = input_text.replace("\n", " ")
    print(f"{"="*150}\n⏳ Processing your input text!")
    # detect the used language
    detected_lang = translator.detect(input_text).lang
    print(
        f"🔍 Detected language: {target_languages[detected_lang]}")
    nlp_dl = spacy.load(MODELS[detected_lang])
    if not nlp_dl:
        print(
            f"No spaCy model for language: {detected_lang}\nFailed to process your text")
        return

    data = load_data()
    id_start = len(data) or 0
    print("⏳ Generating translations and new word lists")
    doc_dl = nlp_dl(input_text)
    for id, sent in enumerate(doc_dl.sents, id_start):
        # if the entire sentence in the data, skip the registration
        if any([True for v in data.values() if sent.text in v["source_sentence"][detected_lang]]):
            print(f"🟡 '{sent}' already exists. Registration skipped.")
            continue
        print(f"🟢 Registering '{sent.text}'")
        new_entry = copy.deepcopy(data_structure)
        for lang in target_langs:
            if detected_lang == lang:
                new_entry["new_words"][lang] = get_word_list(
                    sent, lang, data)
                new_entry["sent_translations"][lang] = sent.text
                new_entry["source_sentence"][lang] = sent.text
            else:
                translated_text = translator.translate(
                    sent.text, src=detected_lang, dest=lang).text
                nlp = spacy.load(MODELS[lang])
                doc = nlp(translated_text)
                new_entry["new_words"][lang] = get_word_list(
                    doc, lang, data)
                new_entry["sent_translations"][lang] = translated_text
                new_entry["source_sentence"][lang] = ""
        new_entry["created_at"] = datetime.now(
        ).isoformat(timespec='seconds')
        data[id] = new_entry

    if len(data) > id_start:  # if there are new items, save
        print(f"⏳ Saving data to [{JSON_PATH}]")
        save_data(data=data)  # save JSON data
        print(f"⏳ Exporting data to [{EXCEL_PATH}]")
        export_table()  # export JSON to excel file
        print("✅ Registration completed!")
    else:  # if there are no new items, skip saving
        print("☑️  No new sentence was found. Registration skipped.")
    print(f"{"="*150}")


process_text(input_string)
