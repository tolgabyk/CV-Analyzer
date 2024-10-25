import pdfplumber
import re
import spacy
import streamlit as st
import google.generativeai as genai

nlp = spacy.load('en_core_web_sm')

# Özgeçmişten metin çıkarma 
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() if page.extract_text() else ""
    return text

# Dil tespit 
def detect_language(text):
    if re.search(r'(experience|education|skills|projects)', text, re.I):
        return 'english'
    elif re.search(r'(deneyim|eğitim|beceriler|projeler)', text, re.I):
        return 'turkish'
    else:
        return 'unknown'

# CV bölümlerini analiz et
def analyze_resume_structure(text, language):
    if language == 'english':
        sections = {
            'experience': bool(re.search(r'(experience|work history|employment)', text, re.I)),
            'education': bool(re.search(r'(education|academic)', text, re.I)),
            'skills': bool(re.search(r'(skills|expertise|proficiencies)', text, re.I)),
            'projects': bool(re.search(r'(projects|accomplishments)', text, re.I))
        }
    elif language == 'turkish':
        sections = {
            'experience': bool(re.search(r'(deneyim|iş geçmişi|çalışma geçmişi)', text, re.I)),
            'education': bool(re.search(r'(eğitim|akademik)', text, re.I)),
            'skills': bool(re.search(r'(beceriler|uzmanlık|yetenekler)', text, re.I)),
            'projects': bool(re.search(r'(projeler|başarılar)', text, re.I))
        }
    else:
        sections = {}
    
    return sections

# Google Generative AI ile geri bildirim önerisi 
def generate_feedback_with_genai(text, sections, language, api_key):
    genai.configure(api_key=api_key)  
    feedback = []
    
    prompt = f"""Aşağıdaki CV içeriğini analiz ederek eksik olan bölümler hakkında öneriler sun:
    
    CV İçeriği:
    {text}
    
    Algılanan Bölümler:
    {sections}
    
    Dil: {language}
    
    Lütfen eksik olan bölümler hakkında geliştirme önerileri sağlayın."""
    
    try:
        # Google Generative AI'dan yanıt al
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat()
        response = chat.send_message(prompt)
        feedback_text = response.text  
        feedback = feedback_text.split("\n")  # Yanıtı satır bazında böl
    except Exception as e:
        feedback.append(f"Google Generative AI API'ye erişimde sorun yaşandı: {str(e)}")
    
    return feedback

# Kullanıcı arayüzü ve CV analizi
def create_dashboard(api_key):
    st.title("CV Analiz Aracı")
    st.write("Bir CV yükleyin ve analiz sonuçlarını ve geri bildirim önerilerini görün.")

    # Kullanıcının dil seçimi
    language_choice = st.selectbox("Lütfen geri bildirim dilini seçin:", ("Türkçe", "İngilizce"))

    # Kullanıcının CV yüklemesi
    uploaded_file = st.file_uploader("CV Yükle (PDF formatında)", type=["pdf"])

    if uploaded_file is not None:
        # CV'yi analiz et
        with st.spinner('Analiz ediliyor... Lütfen bekleyin...'):
            text = extract_text_from_pdf(uploaded_file)
            detected_language = detect_language(text)
            
            chosen_language = 'turkish' if language_choice == "Türkçe" else 'english'
            sections = analyze_resume_structure(text, detected_language)
            
            # Google Generative AI üzerinden geri bildirim önerileri al
            feedback = generate_feedback_with_genai(text, sections, chosen_language, api_key)

        # Analiz sonuçlarını ve önerilerini göster
        st.header("Analiz Sonuçları ve Formatlama Önerileri")
        for suggestion in feedback:
            st.write(f"- {suggestion}")

        
        st.subheader("Çıkarılan Metin")
        st.text(text)

# Uygulama ana fonksiyonu
if __name__ == "__main__":
    api_key = "" # Api Key
    create_dashboard(api_key)
