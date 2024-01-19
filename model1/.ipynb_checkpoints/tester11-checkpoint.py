import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from torch.utils.data import Dataset, DataLoader

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModelForSequenceClassification.from_pretrained("microsoft/codebert-base", num_labels=2)

model.load_state_dict(torch.load('tester1.pth'))

def predict_code_quality(model, tokenizer, code_snippet):
    # Tokenize the code snippet
    inputs = tokenizer(code_snippet, return_tensors="pt", truncation=True, padding=True)

    # Run the model
    with torch.no_grad():
        outputs = model(**inputs)
        print(outputs)
        bad, good = outputs.logits[0]
    
    # Interpret the output (0 for bad quality, 1 for good quality)
    quality = "Good Quality" if good > bad else "Bad Quality"
    return quality

# Titre et informations
st.title('Projet NLP : Détection qualité du code en JavaScript')
#st.write('Réalisé par: Ahmed Lazhar, Meriam Belhiba, Basri Gouider, Atef Labiadh')

# Zone de texte pour récupérer le code JavaScript
code_js = st.text_area('Entrez votre code JavaScript ici')

# Boutons pour évaluer le code et effacer les données
col1, col2 = st.columns([1, 1])
if col1.button('Évaluer le code'):
    # predictions
    quality = predict_code_quality(model, tokenizer, code_js)
    # Affichez le résultat de la prédiction
    st.write(f"{code_js} is {quality}")

if col2.button('Effacer'):
    code_js = ''

    

    

