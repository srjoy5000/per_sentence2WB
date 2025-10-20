# text = "chien (chien: noun)"
# new_candidate = "chien"
# pos = "noun"

# print(new_candidate in text and pos in text)
import spacy
data_structure = {
    "new_words": {},
}

data = {}

list_a = ["a", "b", "c"]


for i, item in enumerate(list_a):
    entry = data_structure.copy()
    entry["new_words"] = item
    data[i] = entry

print(data)


text = "みんなを元気づけたり、簡単に交流したり、競争したり、一緒に笑ったりするためのオプションがあります。"
text = "これらの 10 の理想的なパーティー ゲームを使えば、軽い入り口からパーティーの最高潮まで、友人の集まりを盛り上げる完璧な「ツールボックス」が手に入ります。"

nlp = spacy.load("ja_core_news_md")

doc = nlp(text)
for token in doc:
    print(f"{token.text}: {token.lemma_}: {token.pos_}: {token.tag_}")


data = {"0": {"new_words": {"en": ["dog (dog: noun), barks (bark: verb)"], "fr": ["chien"], "ja": ["犬"], "pt": ["cachorro"]}, "sent_translations": {"en": "The dog barks.", "fr": "Le chien aboie.", "ja": "その犬は吠える", "pt": "O cachorro late."}, "source_sentence": {"fr": "Le chien aboie."}, "created_at": "2025-10-16T14:35:22", "notes": ""}, "1": {
    "new_words": {"en": ["dog"], "fr": ["chien"], "ja": ["犬"], "pt": ["cachorro"]}, "sent_translations": {"en": "The dog barks.", "fr": "Le chien aboie.", "ja": "その犬は吠える", "pt": "O cachorro late."}, "source_sentence": {"fr": "Le chien aboie."}, "created_at": "2025-10-16T14:35:22", "notes": ""}, }
sent = "Le chien aboie."

if any([v["source_sentence"] for v in data.values() if v["source_sentence"]["fr"] == sent]):
    print(f"'{sent}' already exists. Registration skipped.")
