import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.title("Análisis de presencia de términos y estrategia de contenido")

st.markdown("""
Subí tus URLs y tus términos clave. La herramienta verificará si cada término aparece en el H1, la meta descripción y el contenido visible de cada página. Luego podés agregar tus notas estratégicas.
""")

# --- Input ---
urls_input = st.text_area("URLs del sitio (una por línea)")
terms_input = st.text_area("Términos clave (una por línea)")

urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
terms = [t.strip() for t in terms_input.split("\n") if t.strip()]

if urls and terms:

    # --- Función de análisis ---
    def check_term_in_page(url, term):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return {"H1": "Error", "Meta": "Error", "Contenido": "Error"}
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            h1 = " ".join([h.get_text() for h in soup.find_all("h1")])
            meta = soup.find("meta", attrs={"name": "description"})
            meta_desc = meta["content"] if meta else ""
            body = soup.get_text()
            
            return {
                "H1": "✅" if term.lower() in h1.lower() else "❌",
                "Meta": "✅" if term.lower() in meta_desc.lower() else "❌",
                "Contenido": "✅" if term.lower() in body.lower() else "❌"
            }
        except Exception as e:
            return {"H1": "Error", "Meta": "Error", "Contenido": "Error"}

    # --- Construir tabla de resultados ---
    rows = []
    for url in urls:
        for term in terms:
            estado = check_term_in_page(url, term)
            rows.append({
                "URL": url,
                "Término": term,
                "H1": estado["H1"],
                "Meta descripción": estado["Meta"],
                "Contenido": estado["Contenido"],
                "Notas estratégicas": ""  # campo editable
            })

    df = pd.DataFrame(rows)

    # --- Mostrar tabla editable ---
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        column_config={
            "Notas estratégicas": st.column_config.TextColumn(
                "Notas estratégicas",
                help="Agregá aquí ideas de optimización o estrategia de contenido"
            )
        }
    )

    st.markdown("### Exportar tabla con notas")
    st.download_button(
        label="Descargar CSV",
        data=edited_df.to_csv(index=False).encode("utf-8"),
        file_name="analisis_terminos.csv",
        mime="text/csv"
    )
