import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Estrategia de Contenido SEO", layout="wide")

st.title("Estrategia de Contenido a partir de términos de búsqueda")

# 1️⃣ Cargar términos
st.subheader("1. Carga de términos clave")
terminos_file = st.file_uploader("Sube CSV con términos (columna: termino)", type=["csv"])
if terminos_file:
    df_terminos = pd.read_csv(terminos_file)
    terminos = df_terminos['termino'].dropna().tolist()
    st.write("Términos cargados:", terminos)

# 2️⃣ Cargar URLs del sitio
st.subheader("2. Carga de URLs del sitio")
urls_file = st.file_uploader("Sube CSV con URLs (columna: url)", type=["csv"])
if urls_file:
    df_urls = pd.read_csv(urls_file)
    urls = df_urls['url'].dropna().tolist()
    st.write("URLs cargadas:", len(urls))

# 3️⃣ Función heurística de búsqueda
def check_term_in_page(url, term):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return "Error"
        soup = BeautifulSoup(r.text, "html.parser")
        h1 = " ".join([h.get_text() for h in soup.find_all("h1")])
        meta = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta["content"] if meta else ""
        body = soup.get_text()
        
        estado = {
            "H1": "✅" if term.lower() in h1.lower() else "❌",
            "Meta": "✅" if term.lower() in meta_desc.lower() else "❌",
            "Contenido": "✅" if term.lower() in body.lower() else "❌"
        }
        return estado
    except Exception as e:
        return {"H1": "Error", "Meta": "Error", "Contenido": "Error"}

# 4️⃣ Analizar presencia de términos
if terminos_file and urls_file:
    st.subheader("3. Análisis de presencia de términos en el sitio")
    resultados = []
    for url in urls:
        for term in terminos:
            estado = check_term_in_page(url, term)
            resultados.append({
                "URL": url,
                "Termino": term,
                "H1": estado["H1"],
                "Meta descripción": estado["Meta"],
                "Contenido": estado["Contenido"]
            })
    df_result = pd.DataFrame(resultados)
    
    # Colorear estado
    def color_estado(val):
        if val == "✅":
            color = "lightgreen"
        elif val == "❌":
            color = "salmon"
        else:
            color = "lightgray"
        return f"background-color: {color}"
    
    st.dataframe(df_result.style.applymap(color_estado, subset=["H1","Meta descripción","Contenido"]))

    # 5️⃣ Notas estratégicas
    st.subheader("4. Notas estratégicas")
    for url in urls:
        st.markdown(f"**URL: {url}**")
        nota = st.text_area(f"Propuesta de optimización para {url}", key=url)
