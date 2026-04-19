
saya ingin menurunkan akurasi tapi jangan menghapus yang sekarang (tolong di backup dengan nama folder rasa TA).
saya


beri saya nlu,stories,rules versi mvp (minimum viable product dalam bentuk skrip lengkap.

1. nlu.yml → Mengurangi Data Latih NLU
Efek: Model kehilangan kemampuan generalisasi untuk memahami variasi bahasa, negasi, dan entitas kompleks.

Ini adalah faktor utama penurunan Intent Accuracy dan Entity F1.

2. stories.yml & rules.yml → Menyederhanakan Alur Percakapan
Efek: TEDPolicy dan RulePolicy tidak mempelajari transisi percakapan yang kaya.

Ini adalah faktor utama penurunan Action Prediction Accuracy.

3. config.yml (hanya nilai epochs) → Underfitting Terkontrol
Efek: Model tidak mencapai konvergensi optimal.

Mengapa hanya epochs? Karena komponen pipeline lainnya (Tokenizer, Featurizer) adalah arsitektur model. Jika Anda mengubahnya, Anda sedang membandingkan dua arsitektur berbeda, bukan optimasi dari arsitektur yang sama. Itu akan memunculkan pertanyaan: "Kenapa tidak pakai arsitektur bagus dari awal?"