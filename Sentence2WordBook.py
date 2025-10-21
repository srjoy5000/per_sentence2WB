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


class ProcessText:
    def __init__(self, text, settings):
        self.target_POS = {
            "NOUN": "nouns",
            "VERB": "verbs",
            "ADJ": "adjectives",
            "ADV": "adverbs",
            # "AUX": "auxiliary" # not recommended
        }
        self.available_languages = {
            'en': 'ENGLISH',
            'fr': 'FRENCH',
            'pt': 'PORTUGUESE',
            'ja': 'JAPANESE',
        }
        self.data_structure = {
            "new_words": {},
            "sent_translations": {},
            "source_sentence": {},
            "created_at": "",
            "notes": ""
        }
        self.MODELS = {
            'en': f'en_core_web_{settings['model_size'] or "sm"}',
            'fr': f'fr_core_news_{settings['model_size'] or "sm"}',
            'pt': f'pt_core_news_{settings['model_size'] or "sm"}',
            'ja': f'ja_core_news_{settings['model_size'] or "sm"}',
        }
        self.input_string = text
        self.target_languages = {
            k: v for k, v in self.available_languages.items() if k in settings['languages']}
        # print(self.target_languages)
        self.save = settings['save'] or True
        self.JSON_PATH = os.path.join(
            settings['save_dir'], "data.json") or "data.json"
        self.EXCEL_PATH = os.path.join(
            settings['save_dir'], "wordbook.xlsx") or "wordbook.xlsx"
        # print_output = True

        self.translator = Translator()  # Create an instance of the Translator

    def load_data(self):
        file_path = self.JSON_PATH
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}

    def save_data(self, data=None):
        file_path = self.JSON_PATH
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # take the JSON and export it to an Excel file

    def export_table(self):
        # file_path = self.JSON_PATH
        # pos_list = self.target_POS.values()
        data = self.load_data()  # get the saved data from JSON
        data_list = [v | {"id": k} for k, v in data.items()]
        with pd.ExcelWriter(self.EXCEL_PATH, engine='xlsxwriter') as writer:
            df = pd.json_normalize(data_list, sep="_")
            for col in df.columns:
                df[col] = df[col].apply(lambda x: ", ".join(
                    x) if isinstance(x, list) else x)
            columns = ["id", *[f"{name}_{lang}" for lang in self.target_languages.keys() for name in list(self.data_structure.keys())[:-2]], *
                       list(self.data_structure.keys())[-2:]]
            df = df[columns]
            df.to_excel(writer, index=False)
            # if print_output:
            #     print(
            #         f"{"="*100}\n{df}\n{"="*100}")
            return f"{"="*100}\n{df}\n{"="*100}"

    def search_same_word(self, word, lemma, pos_name):
        m = re.search(r"\(([^:()]+):\s*([^()]+)\)", word)
        if m:
            l, p = m.group(1).strip(), m.group(2).strip()
            if l == lemma and p == pos_name:
                return True
        return False

    def get_word_list(self, doc, lang, data) -> list:
        new_words = []
        for token in doc:
            if token.pos_ in self.target_POS.keys():  # choose only noun, verb, adj, adv
                lemma = token.lemma_.lower()
                pos_name = self.target_POS[token.pos_]
                # Check duplication: add word if there are any duplicates
                if not any([True for id in data for word in data[id]
                            ["new_words"][lang] if self.search_same_word(word, lemma, pos_name)]):
                    new_words.append(
                        f"{token.text.lower()} ({lemma}: {pos_name})")
        return new_words

    def process_text(self):
        input_text = self.input_string
        target_langs = self.target_languages.keys()
        input_text = input_text.replace("\n", " ")
        print(f"{"="*100}\n⏳ Processing your input text!")
        # detect the used language
        detected_lang = self.translator.detect(input_text).lang
        print(
            f"🔍 Detected language: {self.target_languages[detected_lang]}")
        nlp_dl = spacy.load(self.MODELS[detected_lang])
        if not nlp_dl:
            print(
                f"No spaCy model for language: {detected_lang}\nFailed to process your text")
            return

        data = self.load_data()
        id_start = len(data) or 0
        print("⏳ Generating translations and new word lists")
        doc_dl = nlp_dl(input_text)
        for id, sent in enumerate(doc_dl.sents, id_start):
            # if the entire sentence in the data, skip the registration
            if any([True for v in data.values() if sent.text in v["source_sentence"][detected_lang]]):
                print(f"🟡 '{sent}' already exists. Registration skipped.")
                continue
            print(f"🟢 Registering '{sent.text}'")
            new_entry = copy.deepcopy(self.data_structure)
            for lang in target_langs:
                if detected_lang == lang:
                    new_entry["new_words"][lang] = self.get_word_list(
                        sent, lang, data)
                    new_entry["sent_translations"][lang] = sent.text
                    new_entry["source_sentence"][lang] = sent.text
                else:
                    translated_text = self.translator.translate(
                        sent.text, src=detected_lang, dest=lang).text
                    nlp = spacy.load(self.MODELS[lang])
                    doc = nlp(translated_text)
                    new_entry["new_words"][lang] = self.get_word_list(
                        doc, lang, data)
                    new_entry["sent_translations"][lang] = translated_text
                    new_entry["source_sentence"][lang] = ""
            new_entry["created_at"] = datetime.now(
            ).isoformat(timespec='seconds')
            data[id] = new_entry

        if len(data) > id_start:  # if there are new items, save
            print(f"⏳ Saving data to [{self.JSON_PATH}]")
            self.save_data(data=data)  # save JSON data
            print(f"⏳ Exporting data to [{self.EXCEL_PATH}]")
            output_string = self.export_table()  # export JSON to excel file
            print("✅ Registration completed!")
            print(f"{"="*100}")
            return output_string
        else:  # if there are no new items, skip saving
            print("☑️  No new sentence was found. Registration skipped.")
            print(f"{"="*100}")
            return "No new sentence was found."


def get_output(input_string, settings):
    text_processor = ProcessText(input_string, settings)
    output = text_processor.process_text()
    return output
