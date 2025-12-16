import streamlit as st
import random
from fpdf import FPDF
import base64
from datetime import datetime
import urllib.parse

# Configuration de la page
st.set_page_config(page_title="Beit Midrash Quizz", page_icon="✡️", layout="wide")

# --- CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Resultats du Test de Connaissances Rabbiniques', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(user_results, score, total, level):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Infos générales
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=1)
    pdf.cell(0, 10, f"Niveau evalue: {level}", ln=1)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Score Final: {score}/{total} ({(score/total)*100:.1f}%)", ln=1)
    pdf.ln(10)
    
    # Détail
    pdf.set_font("Arial", size=10)
    for cat, items in user_results.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"Categorie: {cat}", ln=1)
        pdf.set_font("Arial", size=10)
        
        for item in items:
            status = "CORRECT" if item['correct'] else "ERREUR"
            pdf.multi_cell(0, 8, f"[{status}] Q: {item['question']}")
            pdf.multi_cell(0, 8, f"   Reponse: {item['user_answer']} | Correction: {item['correct_answer']}")
            pdf.ln(2)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

# --- BANQUE DE DONNÉES (Structure: Niveau -> Categorie -> Liste de questions) ---
# Pour avoir des "nouvelles questions" au reset, ajoutez simplement plus de 3 questions par liste.
# Le programme en piochera 3 au hasard.

questions_db = {
    "Niveau 2 : Talmid Haham (Intermédiaire)": {
        "Shabbat": [
            {"q": "Quel est le statut de 'Davar Sheiino Mitkaven' selon Rabbi Shimon ?", "opt": ["Permis", "Interdit Deoraita", "Interdit Derabanan", "Permis seulement pour un besoin vital"], "ans": "Permis", "exp": "Rabbi Shimon permet une action non intentionnelle (sauf si c'est Psik Reisha). La Halacha suit R' Shimon."},
            {"q": "Peut-on demander à un non-juif d'allumer la lumière pour un repas de Shabbat ?", "opt": ["Oui, c'est un besoin de Mitzva", "Non, c'est un interdit de Amira Leakum", "Oui, s'il le fait de lui-même", "Seulement s'il fait sombre"], "ans": "Non, c'est un interdit de Amira Leakum", "exp": "On ne peut pas demander directement, même pour une Mitzva, sauf cas très spécifiques (malade, etc.)."},
            {"q": "Quelle est la quantité minimale pour être coupable de 'Hotzaa' (porter) ?", "opt": ["Un Kezayit", "La taille d'une figue sèche (Grogueret)", "Tout ce qui a une utilité", "Un Reviit"], "ans": "La taille d'une figue sèche (Grogueret)", "exp": "Pour la nourriture, c'est Kagrogueret. Pour d'autres objets, cela dépend de leur utilité."}
        ],
        "Kashrut": [
            {"q": "Quel est le statut du verre (verre à boire) pour la viande et le lait (Sépharades) ?", "opt": ["Il n'absorbe pas, il suffit de le rincer", "Il faut le cachériser", "Il faut attendre 24h", "Interdit d'utiliser pour les deux"], "ans": "Il n'absorbe pas, il suffit de le rincer", "exp": "Selon le Shoulchan Arouch, le verre n'est pas poreux et n'absorbe pas les goûts."},
            {"q": "Qu'est-ce que 'Bishul Akum' concerne principalement ?", "opt": ["Tout aliment", "Aliment qui monte sur la table des rois et ne se mange pas cru", "Seulement la viande", "Le pain seulement"], "ans": "Aliment qui monte sur la table des rois et ne se mange pas cru", "exp": "Si l'aliment se mange cru ou n'est pas 'noble', le décret de Bishul Akum ne s'applique pas."},
            {"q": "Un mélange 'Min be Mino' (espèce dans son espèce) s'annule à :", "opt": ["1/60", "La majorité (Rov)", "1/100", "Ne s'annule jamais"], "ans": "La majorité (Rov)", "exp": "Min Be Mino s'annule à la majorité selon la Torah (Batel Berov), mais les Sages ont exigé 60 par précaution (sauf cas spécifiques). La réponse stricte Halachique de base est Rov pour la Torah."}
        ],
        "Berakhot": [
            {"q": "Quelle est la Bracha sur le riz (Orez) ?", "opt": ["Hamotzi", "Mezonot", "Shehakol", "Haadama"], "ans": "Mezonot", "exp": "Le riz est l'exception : il est Mezonot mais sa Bracha finale est Borei Nefachot."},
            {"q": "Quand doit-on faire la Bracha A'hrona au plus tard ?", "opt": ["72 minutes", "Tant qu'on est rassasié", "30 minutes", "Jusqu'au repas suivant"], "ans": "Tant qu'on est rassasié", "exp": "Le temps de digestion (Iukul) définit la limite, généralement jusqu'à ce qu'on ait à nouveau faim (approx 72 min)."},
            {"q": "Doit-on réciter 'Shehecheyanu' sur un fruit nouveau qu'on voit mais ne mange pas ?", "opt": ["Oui", "Non", "Seulement si on l'achète", "Seulement en Eretz Israel"], "ans": "Oui", "exp": "Selon le Shoulchan Arouch, la vue suffit si cela procure une joie, mais l'usage est d'attendre de le manger."}
        ],
        "Niddah (Pureté familiale)": [
            {"q": "Combien de vérifications (Bedikot) sont obligatoires durant les 7 jours de propreté (selon la Torah) ?", "opt": ["Une le 1er jour et une le 7ème", "Deux par jour", "Une seule suffit", "Aucune, le temps suffit"], "ans": "Une seule suffit", "exp": "Min Hatorah, une seule vérification suffit. Les Sages en demandent deux par jour (Mitzva Lechat'hila)."},
            {"q": "Quelle couleur n'est JAMAIS impure ?", "opt": ["Rouge", "Noir", "Vert", "Rose foncé"], "ans": "Vert", "exp": "Le vert, le blanc, le bleu et le jaune (pur) ne rendent pas Niddah. Le rouge et le noir (rouge séché) oui."},
            {"q": "Qu'est-ce que la 'Hargasha' ?", "opt": ["Sensation d'écoulement utérin", "Douleur au ventre", "Voir du sang", "L'odeur"], "ans": "Sensation d'écoulement utérin", "exp": "Pour être Niddah de la Torah, la femme doit sentir l'ouverture de l'utérus ou l'écoulement (Hargasha)."}
        ],
        "Tefila (Prière)": [
            {"q": "Jusqu'à quand peut-on prier Shacharit (Zman Tephila) ?", "opt": ["Hatzot", "4 heures proportionnelles (Zmanit)", "Midi pile", "Au lever du soleil"], "ans": "4 heures proportionnelles (Zmanit)", "exp": "Le temps idéal est jusqu'à 4 heures. Après, on peut rattraper jusqu'à Hatzot mais sans récompense de 'Prière en son temps'."},
            {"q": "Si on a oublié 'Yaalé Veyavo' dans la Amidah de Shaharit de Rosh Hodesh :", "opt": ["On continue", "On recommence la Amidah", "On le dit à la fin", "On le dit à Mincha"], "ans": "On recommence la Amidah", "exp": "Rosh Hodesh est obligatoire. Si on oublie et qu'on a fini la bénédiction 'Hamahazir', on recommence au début."},
            {"q": "Combien d'hommes faut-il pour la répétition de la Amidah (Hazarat Hashatz) ?", "opt": ["10", "6 qui prient + 4 présents", "9 qui répondent", "3"], "ans": "9 qui répondent", "exp": "Idéalement il faut 9 personnes qui écoutent et répondent Amen pour que la bénédiction ne soit pas en vain."}
        ],
        "Tanakh & Histoire": [
            {"q": "Qui a détruit le Premier Temple ?", "opt": ["Titus", "Nabuchodonosor (Nevou'hadnetzar)", "Antiochus", "Hérode"], "ans": "Nabuchodonosor (Nevou'hadnetzar)", "exp": "Roi de Babylone, en -586 (ou -422 selon Seder Olam)."},
            {"q": "Combien de livres contient le Tanakh ?", "opt": ["5", "24", "36", "12"], "ans": "24", "exp": "Le canon juif compte 24 livres (les 12 petits prophètes comptent pour 1)."},
            {"q": "Quel roi de Yehuda a fait Téchouva à la fin de sa vie ?", "opt": ["Ménaché", "Ahab", "David", "Salomon"], "ans": "Ménaché", "exp": "Malgré ses fautes graves, Ménaché a fait Téchouva dans les fers à Babylone et D.ieu l'a écouté."}
        ]
    },
    # Vous pouvez copier-coller la structure ci-dessus pour remplir Niveau 1 et 3
    "Niveau 1 : Fondamentaux (Baal Kore)": {"Général": [{"q": "Exemple question niveau 1...", "opt": ["A", "B"], "ans": "A", "exp": "..."}]},
    "Niveau 3 : Décisionnaire (Dayan)": {"Général": [{"q": "Exemple question niveau 3...", "opt": ["A", "B"], "ans": "A", "exp": "..."}]}
}

# --- FONCTIONS UTILITAIRES ---

def get_quiz_data(level):
    """Récupère 3 questions aléatoires par catégorie pour le niveau donné"""
    if level not in questions_db:
        return {}
    
    full_data = questions_db[level]
    selected_quiz = {}
    
    for category, questions in full_data.items():
        # Si on a plus de 3 questions, on en prend 3 au hasard
        # Sinon on prend tout ce qu'il y a
        nb_to_take = min(3, len(questions))
        selected_quiz[category] = random.sample(questions, nb_to_take)
        
    return selected_quiz

def reset_quiz():
    st.session_state.answers = {}
    st.session_state.quiz_generated = False
    st.session_state.current_quiz_data = {}
    st.session_state.finished = False

# --- DÉBUT DE L'INTERFACE ---

st.title("📚 Beit Midrash - Évaluation Rabbinique")
st.markdown("Ce test couvre 6 domaines de la Halacha et du savoir juif. **3 questions par domaine (Total 18).**")

# Initialisation du State
if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'finished' not in st.session_state:
    st.session_state.finished = False

# 1. SÉLECTION DU NIVEAU
if not st.session_state.quiz_generated:
    st.sidebar.header("Configuration")
    selected_level = st.sidebar.selectbox("Choisir le niveau :", list(questions_db.keys()))
    
    if st.sidebar.button("Commencer le Quizz / Mélanger les questions"):
        st.session_state.current_level = selected_level
        st.session_state.current_quiz_data = get_quiz_data(selected_level)
        st.session_state.quiz_generated = True
        st.rerun()

# 2. AFFICHAGE DU QUIZZ
if st.session_state.quiz_generated and not st.session_state.finished:
    st.header(f"Test : {st.session_state.current_level}")
    
    with st.form("exam_form"):
        question_counter = 1
        data = st.session_state.current_quiz_data
        
        # Parcourir les catégories
        for category, questions in data.items():
            st.markdown(f"### 📖 {category}")
            for q_data in questions:
                st.markdown(f"**{question_counter}. {q_data['q']}**")
                
                # Widget unique par question
                key_name = f"q_{category}_{question_counter}"
                st.session_state.answers[key_name] = st.radio(
                    "Réponse :", 
                    q_data['opt'], 
                    key=key_name, 
                    index=None,
                    label_visibility="collapsed"
                )
                st.markdown("---")
                question_counter += 1
        
        if st.form_submit_button("Valider l'examen"):
            st.session_state.finished = True
            st.rerun()

# 3. RÉSULTATS ET EXPORT
if st.session_state.finished:
    st.header("📈 Résultats de l'examen")
    
    score = 0
    total_questions = 0
    results_detail = {} # Pour le PDF
    
    data = st.session_state.current_quiz_data
    q_counter = 1
    
    # Calcul du score et affichage
    for category, questions in data.items():
        st.subheader(f"Catégorie : {category}")
        results_detail[category] = []
        
        for q_data in questions:
            total_questions += 1
            user_key = f"q_{category}_{q_counter}"
            user_res = st.session_state.answers.get(user_key)
            correct = q_data['ans']
            is_correct = (user_res == correct)
            
            # Stockage pour PDF
            results_detail[category].append({
                "question": q_data['q'],
                "user_answer": str(user_res),
                "correct_answer": correct,
                "correct": is_correct
            })
            
            # Affichage écran
            with st.expander(f"Q{q_counter}: {q_data['q']}", expanded=False):
                if is_correct:
                    st.success(f"✅ Correct ! ({user_res})")
                    score += 1
                else:
                    st.error(f"❌ Erreur. Votre réponse : {user_res}")
                    st.info(f"La bonne réponse était : **{correct}**")
                st.markdown(f"💡 *Explication : {q_data['exp']}*")
            
            q_counter += 1

    # Score Final
    final_percentage = (score / total_questions) * 100
    col1, col2, col3 = st.columns(3)
    col2.metric("Note Finale", f"{score}/{total_questions}", f"{final_percentage:.1f}%")

    if final_percentage > 80:
        st.balloons()
        st.success("Mazal Tov ! Excellent niveau.")
    elif final_percentage > 50:
        st.warning("Bon travail, mais des révisions sont nécessaires.")
    else:
        st.error("Niveau insuffisant. Il faut reprendre les bases.")

    st.markdown("---")
    
    # --- ZONE D'EXPORT ---
    st.subheader("📤 Sauvegarder mes résultats")
    
    c1, c2, c3 = st.columns(3)
    
    # 1. Générer PDF
    pdf_bytes = create_pdf(results_detail, score, total_questions, st.session_state.current_level)
    b64_pdf = base64.b64encode(pdf_bytes).decode('latin-1')
    href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="resultat_torah_quizz.pdf" style="text-decoration:none; color:white; background-color:#FF4B4B; padding:10px; border-radius:5px;">📄 Télécharger le PDF</a>'
    c1.markdown(href_pdf, unsafe_allow_html=True)
    
    # 2. Envoyer par Email (Mailto)
    subject = f"Résultat Quizz: {st.session_state.current_level}"
    body = f"Shalom,\n\nVoici mon résultat au test.\nScore: {score}/{total_questions} ({final_percentage:.1f}%).\n\nBien cordialement."
    # Encodage pour URL
    safe_subject = urllib.parse.quote(subject)
    safe_body = urllib.parse.quote(body)
    mailto_link = f"mailto:?subject={safe_subject}&body={safe_body}"
    
    c2.markdown(f'<a href="{mailto_link}" target="_blank" style="text-decoration:none; color:white; background-color:#4CAF50; padding:10px; border-radius:5px;">📧 Envoyer par Email</a>', unsafe_allow_html=True)
    
    # 3. Recommencer
    if c3.button("🔄 Recommencer le test"):
        reset_quiz()
        st.rerun()
