import streamlit as st
import requests
from bs4 import BeautifulSoup
import spacy
from collections import Counter
import pandas as pd

# Cargar modelo spaCy (idioma inglés, si querés español cambia a es_core_news_sm)
@st.cache_resource
def load_model():
    return spacy.load("en_core_web_sm")

def extract_text_from_url(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Extraer texto visible - evitar scripts, estilos, etc.
        texts = soup.findAll(text=True)
        blacklist = ['style', 'script', 'head', 'title', 'meta', '[document]']
        visible_texts = filter(lambda t: t.parent.name not in blacklist, texts)
        visible_text = " ".join(t.strip() for t in visible_texts if t.strip())
        return visible_text
    except Exception as e:
        st.error(f"Error al obtener texto de la URL: {e}")
        return ""

def analyze_entities(text, nlp):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

st.title("Análisis básico de Entidades de una Página Web")

url = st.text_input("Ingrese URL para analizar (solo páginas en inglés por ahora):")

if url:
    nlp = load_model()
    with st.spinner("Extrayendo texto..."):
        text = extract_text_from_url(url)
    if text:
        st.success("Texto extraído correctamente. Analizando entidades...")
        entities = analyze_entities(text, nlp)
        if entities:
            # Contar frecuencia por entidad y tipo
            counter = Counter(entities)
            data = []
            for (entity, label), freq in counter.items():
                data.append({"Entidad": entity, "Tipo": label, "Frecuencia": freq})
            df = pd.DataFrame(data).sort_values(by="Frecuencia", ascending=False)
            st.dataframe(df)

            # Gráfico barras de entidades más frecuentes
            top_df = df.head(10)
            st.bar_chart(top_df.set_index("Entidad")["Frecuencia"])
        else:
            st.warning("No se detectaron entidades en el texto.")
    else:
        st.error("No se pudo extraer texto para analizar.")

else:
    st.info("Ingresa una URL para empezar el análisis.")
