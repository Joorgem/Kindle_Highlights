import streamlit as st
import re
from io import StringIO
from collections import defaultdict

# Função para processar arquivo de texto
def process_file(content):
    notes = []
    for note in content.split('=========='):
        if note.strip():
            lines = note.strip().split('\n')
            if len(lines) >= 3:
                book_info = lines[0].strip()
                page_info = re.search(r'página (\d+)', lines[1])
                if page_info:
                    page = int(page_info.group(1))
                else:
                    page = None
                highlight = '\n'.join(lines[3:]).strip()
                notes.append({'text': highlight, 'book': book_info, 'page': page})
    return notes

# Função para agrupar notas com base na contenção de sequências de palavras
def group_notes_by_containment(notes, min_words=4, page_tolerance=2):
    grouped_notes = []
    used_indices = set()

    for i, note1 in enumerate(notes):
        if i in used_indices:
            continue

        group = [note1]

        for j, note2 in enumerate(notes):
            if i != j and j not in used_indices:
                # Verificar se as notas são do mesmo livro e têm informações de página válidas
                if (note1['book'] == note2['book'] and 
                    note1['page'] is not None and note2['page'] is not None and 
                    abs(note1['page'] - note2['page']) <= page_tolerance):

                    words1 = note1['text'].split()
                    words2 = note2['text'].split()

                    # Limitar a palavra referência como tendo no mínimo 4 palavras
                    if len(words1) >= min_words and len(words2) >= min_words:
                        if " ".join(words2[:min_words]) in note1['text'] or " ".join(words1[:min_words]) in note2['text']:
                            group.append(note2)
                            used_indices.add(j)

        grouped_notes.append(group)
        used_indices.add(i)

    # Remover grupos com apenas uma nota, se necessário
    grouped_notes = [group for group in grouped_notes if len(group) > 1]

    return grouped_notes

# Função para exibir grupos de notas no Streamlit
def display_groups(grouped_notes):
    for group_id, group in enumerate(grouped_notes, 1):
        st.markdown(f"### Grupo {group_id} - {len(group)} notas")
        for note in group:
            st.write(f"- [{note['book']} - Página {note['page']}] {note['text']}")
        st.markdown("---")

# Início do Streamlit App
st.title("Kindle Highlights Manager")

uploaded_file = st.file_uploader("Escolha um arquivo .txt", type="txt")

if uploaded_file is not None:
    content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    notes = process_file(content)
    
    if notes:
        st.write(f"{len(notes)} notas carregadas.")
        
        # Parâmetro para o número mínimo de palavras na sequência
        min_words = st.slider("Número mínimo de palavras na sequência de referência", 1, 10, 4, 1)
        
        # Agrupar as notas por contenção de sequência de palavras com verificação de páginas
        st.write("Agrupando as notas por conteúdo e verificando páginas...")
        grouped_notes = group_notes_by_containment(notes, min_words)
        
        # Exibir os grupos
        display_groups(grouped_notes)
        
        st.write(f"{len(grouped_notes)} grupos foram formados (grupos com 1 nota foram removidos).")
        
        # Opção para enviar para a API após a visualização (a implementar)
        if st.button("Enviar Grupos para a API"):
            st.write("Grupos enviados para a API (função a ser implementada).")
    else:
        st.error("Nenhuma nota encontrada no arquivo.")
else:
    st.info("Por favor, faça o upload de um arquivo .txt com as notas do Kindle.")
