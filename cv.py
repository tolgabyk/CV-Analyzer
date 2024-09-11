import pdfplumber
import re
import pandas as pd
import spacy
import streamlit as st

nlp = spacy.load('en_core_web_sm')

# Özgeçmişten metin çıkarma fonksiyonu
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() if page.extract_text() else ""
    return text

# Dil tespit fonksiyonu
def detect_language(text):
    if re.search(r'(experience|education|skills|projects)', text, re.I):
        return 'english'
    elif re.search(r'(deneyim|eğitim|beceriler|projeler)', text, re.I):
        return 'turkish'
    else:
        return 'unknown'

# CV bölümlerini analiz etme fonksiyonu
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

# Otomatik geri bildirim üretme fonksiyonu
def generate_feedback(sections, language):
    feedback = []
    
    if language == 'english':
        # Experience Section Feedback
        if not sections.get('experience', False):
            feedback.append("Your resume does not contain a 'Work Experience' section. Consider adding this section to highlight your professional background.")
        else:
            feedback.append("The 'Work Experience' section is present. Ensure it is in reverse chronological order, detailing roles and responsibilities for each position.")

        # Education Section Feedback
        if not sections.get('education', False):
            feedback.append("Your resume is missing an 'Education' section. Include this section to list your degrees and institutions.")
        else:
            feedback.append("The 'Education' section is present. Make sure to list your most recent education first, followed by earlier degrees.")

        # Skills Section Feedback
        if not sections.get('skills', False):
            feedback.append("Your resume lacks a 'Skills' section. Consider adding a list of technical and soft skills.")
        else:
            feedback.append("The 'Skills' section is well-organized. Consider separating technical and personal skills for better readability.")

        # Projects Section Feedback
        if not sections.get('projects', False):
            feedback.append("Your resume does not mention any 'Projects' or 'Accomplishments'. Including relevant projects and their outcomes could add value.")
        else:
            feedback.append("The 'Projects' section is present, but ensure to highlight the results and impact of each project.")
    
    elif language == 'turkish':
        # Deneyim Bölümü Önerileri
        if not sections.get('experience', False):
            feedback.append("CV'nizde 'İş Deneyimi' bölümü bulunmuyor. Bu bölümü ekleyerek profesyonel geçmişinizi vurgulayabilirsiniz.")
        else:
            feedback.append("İş Deneyimi bölümü mevcut. Kronolojik bir sırada olduğundan emin olun ve her pozisyon için görev ve sorumluluklarınızı net bir şekilde belirtin.")
        
        # Eğitim Bölümü Önerileri
        if not sections.get('education', False):
            feedback.append("Eğitim geçmişiniz belirtilmemiş. 'Eğitim' bölümünü ekleyerek mezun olduğunuz okulları ve aldığınız dereceleri listeleyebilirsiniz.")
        else:
            feedback.append("Eğitim geçmişiniz mevcut. En son eğitim aldığınız yerden başlayarak geriye doğru kronolojik olarak düzenleyin.")
        
        # Beceri Bölümü Önerileri
        if not sections.get('skills', False):
            feedback.append("CV'nizde 'Beceriler' bölümü eksik. Teknik ve yumuşak becerilerinizi listeleyerek bu bölümü ekleyin.")
        else:
            feedback.append("Beceriler bölümü iyi bir şekilde düzenlenmiş. Teknik ve kişisel becerileri ayrı başlıklar altında belirtmek okunabilirliği artırabilir.")
        
        # Projeler veya Başarılar Bölümü Önerileri
        if not sections.get('projects', False):
            feedback.append("Projeler veya başarılarınız hakkında bilgi verilmemiş. Önemli projelerinizi ve bunların sonuçlarını ekleyebilirsiniz.")
        else:
            feedback.append("Projeler bölümü mevcut, ancak her projenin sonucu ve etkisini vurgulamayı unutmayın.")
    
    else:
        feedback.append("CV'nin dili belirlenemedi. Lütfen CV'nin İngilizce veya Türkçe olduğundan emin olun.")

    return feedback

# Kullanıcı arayüzü ve CV analizi
def create_dashboard():
    st.title("Gelişmiş CV Analiz ve Geri Bildirim Aracı")
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
            # Kullanıcının seçtiği dili kullan
            chosen_language = 'turkish' if language_choice == "Türkçe" else 'english'
            sections = analyze_resume_structure(text, detected_language)
            feedback = generate_feedback(sections, chosen_language)

        # Analiz sonuçlarını ve önerilerini göster
        st.header("Analiz Sonuçları ve Formatlama Önerileri")
        for suggestion in feedback:
            st.write(f"- {suggestion}")

        # Metnin tamamını göster (isteğe bağlı)
        st.subheader("Çıkarılan Metin")
        st.text(text)

# Uygulama ana fonksiyonu
if __name__ == "__main__":
    create_dashboard()
