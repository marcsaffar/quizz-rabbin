import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Quizz Élèves Rabbins", page_icon="✡️", layout="centered")

# --- BANQUE DE QUESTIONS ---
questions_db = {
    "Niveau 1 : Fondamentaux (Baal Kore)": [
        {
            "q": "Quelle est la bénédiction (Berakha) appropriée pour une pizza si l'on en mange moins d'un Kezayit ?",
            "options": ["Hamotzi", "Mezonot", "Shehakol", "Borei Nefachot"],
            "answer": "Mezonot",
            "explanation": "Si la pâte est pétrie avec du jus de fruit ou du lait (majoritaire) et qu'on n'en fait pas un repas fixe (Keviat Seouda), c'est Mezonot. Sinon, c'est Hamotzi."
        },
        {
            "q": "Qui est l'auteur du Shoulchan Arouch ?",
            "options": ["Le Rambam", "Rabbi Yossef Karo", "Le Rema", "Rachi"],
            "answer": "Rabbi Yossef Karo",
            "explanation": "Rabbi Yossef Karo a rédigé le Shoulchan Arouch au 16ème siècle à Safed."
        },
        {
            "q": "Quel prophète a oint le Roi David ?",
            "options": ["Nathan", "Élie (Eliyahou)", "Samuel (Shmouel)", "Gad"],
            "answer": "Samuel (Shmouel)",
            "explanation": "C'est Shmouel Hanavi qui a oint David à Bethléem (1 Samuel 16)."
        }
    ],
    "Niveau 2 : Approfondissement (Talmid Haham)": [
        {
            "q": "Dans les lois du Shabbat, quelle condition n'est PAS requise pour l'interdit de Borer (Trier) ?",
            "options": ["Ochel Mitoch Psolet (Le bon du mauvais)", "Beyad (À la main)", "Miyad (Pour une consommation immédiate)", "Kli Sheni (Dans un second ustensile)"],
            "answer": "Kli Sheni (Dans un second ustensile)",
            "explanation": "Les conditions pour permettre le tri sont : Bon du mauvais, à la main, pour tout de suite. Kli Sheni concerne la cuisson (Bishul), pas le tri."
        },
        {
            "q": "Combien de temps faut-il attendre entre la viande et le lait selon l'opinion stricte du Rema (Ashkénaze) ?",
            "options": ["6 heures", "3 heures", "1 heure", "Juste se rincer la bouche"],
            "answer": "6 heures",
            "explanation": "Bien que certaines coutumes allemandes soient de 3h, le Rema conclut qu'il est correct d'attendre 6h comme pour le Rambam."
        },
         {
            "q": "Que signifie le principe 'Kim Li' dans le droit civil hébraïque (Chochen Michpat) ?",
            "options": ["J'ai établi", "Je tiens pour moi (comme cet avis)", "C'est facile pour moi", "Comme il est écrit"],
            "answer": "Je tiens pour moi (comme cet avis)",
            "explanation": "Le défendeur peut dire 'Kim Li' (je tiens comme cette opinion minoritaire) pour ne pas payer, car la charge de la preuve incombe au demandeur."
        }
    ],
    "Niveau 3 : Décisionnaire (Dayan)": [
        {
            "q": "Concernant 'Bishul Akum' (cuisson par un non-juif), quelle est la différence majeure entre le Shoulchan Arouch et le Rema ?",
            "options": ["L'allumage du feu suffit pour le Rema", "Le Rema interdit tout", "Le Shoulchan Arouch permet si le Juif remue", "Il n'y a pas de différence"],
            "answer": "L'allumage du feu suffit pour le Rema",
            "explanation": "Pour les Sépharades (S.A), le Juif doit participer physiquement à la cuisson (ex: poser la marmite). Pour les Ashkénazes (Rema), si le Juif allume seulement le feu, c'est permis."
        },
        {
            "q": "Dans un cas de 'Safek Sfeika' (double doute) dans la Torah, quelle est la règle ?",
            "options": ["On va à la rigueur (Lehoumra)", "On va à la permission (Lekoula)", "On demande au Sanhédrin", "On suit la majorité"],
            "answer": "On va à la permission (Lekoula)",
            "explanation": "Un double doute permet d'autoriser même un interdit de la Torah (Deoraita)."
        }
    ]
}

# --- INTERFACE ---
st.title("📚 Quizz : Formation Rabbinique")
st.markdown("Testez vos connaissances en Halacha, Gemara et Tanakh.")
st.markdown("---")

# Sélection du niveau
niveau = st.selectbox("Choisissez votre niveau de difficulté :", list(questions_db.keys()))

# Initialisation du score
if 'score' not in st.session_state:
    st.session_state.score = 0

# Affichage du formulaire
with st.form("quiz_form"):
    questions = questions_db[niveau]
    reponses_utilisateur = {}
    
    for i, item in enumerate(questions):
        st.subheader(f"Question {i+1}")
        st.write(item["q"])
        # On utilise une clé unique pour chaque widget
        reponses_utilisateur[i] = st.radio(
            "Votre réponse :", 
            item["options"], 
            key=f"q_{niveau}_{i}",
            index=None
        )
        st.write("") # Espace
    
    submitted = st.form_submit_button("Valider mes réponses")

# --- RÉSULTATS ---
if submitted:
    st.markdown("---")
    st.header("📈 Résultats")
    
    score = 0
    total = len(questions)
    
    for i, item in enumerate(questions):
        user_resp = reponses_utilisateur[i]
        correct_resp = item["answer"]
        
        with st.expander(f"Question {i+1} : {item['q']}", expanded=True):
            if user_resp == correct_resp:
                st.success(f"✅ Correct ! ({user_resp})")
                score += 1
            else:
                st.error(f"❌ Incorrect. Vous avez répondu : {user_resp}")
                st.markdown(f"**La bonne réponse était :** {correct_resp}")
            
            st.info(f"💡 **Explication :** {item['explanation']}")

    # Score final
    final_score = (score / total) * 100
    st.metric(label="Score Final", value=f"{score}/{total}", delta=f"{final_score:.0f}%")
    
    if final_score == 100:
        st.balloons()
        st.success("Hazak Barouch ! Maîtrise parfaite.")
    elif final_score >= 70:
        st.warning("Tov Méod. Quelques révisions nécessaires.")
    else:
        st.error("Nécessite une réétude du Siman (chapitre).")
