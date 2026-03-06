import streamlit as st
from pathlib import Path

def load_css():
    css_path = Path(__file__).resolve().parent.parent / "app/style.css"
    if not css_path.exists():
        css_path = Path(__file__).resolve().parent.parent / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css()

st.markdown("""
<style>
.pa-hero {
    text-align: center;
    padding: 40px 20px 30px 20px;
}
.pa-hero h1 {
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    letter-spacing: 3px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #ff2d78, #b24dff, #ff2d78);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
.pa-hero .pa-tagline {
    font-size: 1.05rem;
    color: #a89bb5 !important;
    font-style: italic;
    letter-spacing: 1px;
}
.pa-section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #febfda !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 30px 0 6px 0;
    text-shadow: 0 0 10px rgba(255, 45, 120, 0.25);
}
.pa-card {
    background: linear-gradient(145deg, rgba(13,13,24,0.95), rgba(20,10,30,0.9));
    border: 1px solid rgba(255, 45, 120, 0.15);
    border-radius: 12px;
    padding: 22px 26px;
    margin: 10px 0;
    transition: all 0.3s ease;
}
.pa-card:hover {
    border-color: rgba(255, 45, 120, 0.4);
    box-shadow: 0 0 20px rgba(255, 45, 120, 0.15);
}
.pa-card h3 {
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #febfda !important;
    margin: 0 0 10px 0;
}
.pa-card p, .pa-card li {
    font-size: 0.9rem;
    color: #c4b8d4 !important;
    line-height: 1.6;
}
.pa-card ul { padding-left: 20px; margin: 6px 0; }
.pa-card li { margin-bottom: 4px; }
.pa-stat-box {
    text-align: center;
    background: linear-gradient(145deg, rgba(13,13,24,0.95), rgba(20,10,30,0.9));
    border: 1px solid rgba(255, 45, 120, 0.2);
    border-radius: 12px;
    padding: 20px 14px;
    margin: 6px 0;
}
.pa-stat-number {
    font-size: 2rem;
    font-weight: 900;
    color: #ff2d78 !important;
    text-shadow: 0 0 15px rgba(255, 45, 120, 0.4);
}
.pa-stat-label {
    font-size: 0.8rem;
    color: #a89bb5 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}
.pa-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin: 14px 0;
}
.pa-step-num {
    flex-shrink: 0;
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #ff2d78, #b24dff);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.9rem;
    color: #fff !important;
}
.pa-step-content { flex: 1; }
.pa-step-content strong { color: #febfda !important; font-size: 0.95rem; }
.pa-step-content p {
    color: #a89bb5 !important;
    font-size: 0.85rem;
    margin: 3px 0 0 0;
    line-height: 1.5;
}
.pa-feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 10px 0;
}
.pa-feature-item {
    background: rgba(13, 13, 24, 0.8);
    border: 1px solid rgba(255, 45, 120, 0.12);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    transition: all 0.3s ease;
}
.pa-feature-item:hover {
    border-color: rgba(255, 45, 120, 0.35);
    transform: translateY(-2px);
}
.pa-feature-icon { font-size: 1.6rem; margin-bottom: 6px; }
.pa-feature-name { font-size: 0.85rem; font-weight: 700; color: #febfda !important; }
.pa-feature-desc { font-size: 0.75rem; color: #a89bb5 !important; margin-top: 3px; }
.pa-weight-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 8px 0;
}
.pa-weight-label { width: 140px; font-size: 0.82rem; color: #c4b8d4 !important; text-align: right; }
.pa-weight-track {
    flex: 1; height: 10px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 5px; overflow: hidden;
}
.pa-weight-fill {
    height: 100%; border-radius: 5px;
    background: linear-gradient(90deg, #ff2d78, #b24dff);
}
.pa-weight-val { width: 40px; font-size: 0.78rem; color: #ff2d78 !important; font-weight: 700; }
.pa-contact-box {
    background: linear-gradient(145deg, rgba(20, 10, 30, 0.95), rgba(13, 13, 24, 0.9));
    border: 1px solid rgba(255, 45, 120, 0.25);
    border-radius: 12px;
    padding: 28px;
    text-align: center;
    margin: 20px 0;
}
.pa-contact-box h3 { font-size: 1.1rem !important; color: #febfda !important; margin-bottom: 14px; }
.pa-contact-box p { font-size: 0.88rem; color: #a89bb5 !important; margin: 5px 0; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-section-title"> Profil</div>', unsafe_allow_html=True)
    username = st.session_state.get("username", "Invité")
    st.markdown(f"Bienvenue **{username}**")
    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)
    if st.button("Se déconnecter", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# =====================================================
# HERO
# =====================================================
st.markdown("""
<div class="pa-hero">
    <div class="pa-section-title">Data Intelligence au service du 7e Art</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr style="border:none; height:2px; background:linear-gradient(90deg, transparent, rgba(255,45,120,0.5), transparent); margin:0 0 30px 0;">', unsafe_allow_html=True)

# =====================================================
# CONTEXTE
# =====================================================
st.markdown('<div class="pa-section-title">Le contexte</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pa-card">
    <h3>Un cinéma en pleine transformation digitale</h3>
    <p>
        Un cinéma indépendant situé dans la Creuse, en perte de vitesse, a décidé de franchir
        le cap du numérique. L'objectif : créer une plateforme en ligne qui enrichit l'expérience
        de ses spectateurs en leur proposant un catalogue complet, des recommandations personnalisées
        et une sélection patrimoniale de films classiques.
    </p>
    <p style="margin-top:10px;">
        Le défi majeur : nous sommes en situation de <strong style="color:#ff2d78 !important;">cold start</strong>.
        Aucun utilisateur n'a encore renseigné ses préférences. Le système de recommandation doit donc
        fonctionner uniquement à partir des caractéristiques intrinsèques des films (contenu, genres, métadonnées)
        sans aucune donnée d'usage.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# ÉTUDE DE MARCHÉ
# =====================================================
st.markdown('<div class="pa-section-title">Étude de marché</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pa-card">
    <h3>Analyse du marché cinématographique dans la Creuse</h3>
    <p>
        Avant de construire le catalogue et le système de recommandation, nous avons réalisé une étude
        de marché approfondie sur la consommation de cinéma dans la région de la Creuse. Cette analyse
        préliminaire nous a permis de comprendre les attentes et préférences du public local, et d'orienter
        nos choix de filtrage des bases de données IMDb et TMDB.
    </p>
    <p style="margin-top:10px;">
        L'étude a porté sur les données du <strong style="color:#ff2d78 !important;">CNC</strong> (Centre National
        du Cinéma) et de l'<strong style="color:#ff2d78 !important;">INSEE</strong> pour caractériser le profil
        sociodémographique de la zone, la fréquentation des salles, les genres les plus populaires et les
        habitudes de consommation culturelle. Ces insights ont directement guidé la constitution d'un catalogue
        réduit et pertinent de <strong style="color:#ff2d78 !important;">10 307 films</strong>, adapté au public cible.
    </p>
    <p style="margin-top:10px;">
        Points clés de l'étude :
    </p>
    <ul>
        <li>Profil démographique de la Creuse et habitudes de fréquentation cinéma</li>
        <li>Analyse des tendances de consommation (genres, périodes, origines des films)</li>
        <li>Benchmark avec les cinémas indépendants en zone rurale</li>
        <li>Définition des critères de filtrage pour constituer un catalogue adapté : films avec titres français, de 1950 à 2025, durée entre 60min et 180min, note minimale 6.0, si durée > 120min note minimale 8.0, genres adaptés au grand public : exclusion de "sport", "horreur", "téléfilm", "actualités" seuils de vote en fonction de la zone de production. </li>
    </ul>
    <p style="margin-top:14px;">
        <a href="https://my.visme.co/view/33pggggx-analyse-de-marche" target="_blank"
           style="color:#ff2d78 !important; font-weight:700; text-decoration:underline;">
           Consulter l'étude de marché complète →
        </a>
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# NOTRE AGENCE
# =====================================================
st.markdown('<div class="pa-section-title">Notre agence</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pa-card">
    <h3>Popcorn Analytics — Data Analysts freelance</h3>
    <p>
        Popcorn Analytics est une agence de conseil en data analyse spécialisée dans l'industrie
        culturelle et le divertissement. Notre équipe est composé de Matthias Haeflinger, Patricia Fereira et Ziad Bejaoui. 
        Nous accompagnons les acteurs du cinéma, du streaming et de la distribution dans l'exploitation intelligente de 
        leurs données.
    </p>
    <p style="margin-top:10px;">Nos domaines d'expertise :</p>
    <ul>
        <li>Systèmes de recommandation (KNN, content-based filtering, approches hybrides)</li>
        <li>Analyse exploratoire et visualisation de données</li>
        <li>KPI et tableaux de bord décisionnels</li>
        <li>Industrialisation de pipelines data</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# =====================================================
# LE CATALOGUE
# =====================================================
st.markdown('<div class="pa-section-title">Le catalogue</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="pa-stat-box"><div class="pa-stat-number">10 307</div><div class="pa-stat-label">Films au catalogue</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="pa-stat-box"><div class="pa-stat-number">20</div><div class="pa-stat-label">Genres couverts</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="pa-stat-box"><div class="pa-stat-number">1950—2025</div><div class="pa-stat-label">Période couverte</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="pa-stat-box"><div class="pa-stat-number">4</div><div class="pa-stat-label">Zones de production</div></div>', unsafe_allow_html=True)

st.markdown("""
<div class="pa-card" style="margin-top:14px;">
    <h3>Sources de données</h3>
    <p>
        Le catalogue a été construit à partir de deux sources complémentaires :
        <strong style="color:#ff2d78 !important;">IMDb</strong> (Internet Movie Database) pour les métadonnées
        structurées (titres, casting, notes, genres) et
        <strong style="color:#ff2d78 !important;">TMDB</strong> (The Movie Database) pour les données enrichies
        (affiches, synopsis, budgets, zones de production). Les datasets bruts représentent plus de 7 millions
        d'entrées — un nettoyage et filtrage rigoureux a permis d'obtenir un catalogue de qualité adapté
        au public du cinéma. De plus nous avons créé une clé API keywords TMDB afin de récupérer une liste de mots-clés par film.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# CE QUE NOUS AVONS RÉALISÉ
# =====================================================
st.markdown('<div class="pa-section-title">Ce que nous avons réalisé</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pa-feature-grid">
    <div class="pa-feature-item">
        <div class="pa-feature-name">Catalogue interactif</div>
        <div class="pa-feature-desc">Filtres multi-critères, recherche, tri et pagination sur 10 000+ films</div>
    </div>
    <div class="pa-feature-item">
        <div class="pa-feature-name">Recommandations ML</div>
        <div class="pa-feature-desc">Moteur KNN content-based avec score hybride similarité + popularité</div>
    </div>
    <div class="pa-feature-item">
        <div class="pa-feature-name">Sélection patrimoniale</div>
        <div class="pa-feature-desc">Curation de films classiques pour valoriser le patrimoine cinématographique</div>
    </div>
    <div class="pa-feature-item">
        <div class="pa-feature-name">Dashboard & KPIs</div>
        <div class="pa-feature-desc">Statistiques du catalogue, tendances et indicateurs clés</div>
    </div>
    <div class="pa-feature-item">
        <div class="pa-feature-name">Gestion des favoris</div>
        <div class="pa-feature-desc">Système de favoris personnalisé pour les utilisateurs connectés</div>
    </div>
    <div class="pa-feature-item">
        <div class="pa-feature-name">API REST</div>
        <div class="pa-feature-desc">Backend FastAPI exposant les données et recommandations via endpoints</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# COMMENT FONCTIONNE LA RECOMMANDATION
# =====================================================
st.markdown('<div class="pa-section-title">Comment sont recommandés les films ?</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pa-card">
    <h3>Approche : Content-Based Filtering en situation de cold start</h3>
    <p>
        En l'absence de données utilisateur (pas d'historique de visionnage, pas de notes),
        nous utilisons une approche <strong style="color:#ff2d78 !important;">content-based</strong> :
        les films sont recommandés sur la base de leurs caractéristiques propres, sans aucune
        information sur les préférences des spectateurs.
    </p>
    <p style="margin-top:10px;">
        L'algorithme choisi est le <strong style="color:#ff2d78 !important;">K-Nearest Neighbors (KNN)</strong>
        avec une mesure de <strong style="color:#ff2d78 !important;">similarité cosinus</strong>.
        Chaque film est représenté par un vecteur multidimensionnel combinant plusieurs types de features,
        puis le modèle identifie les K films les plus proches dans cet espace vectoriel.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pa-card">
    <h3>Pipeline de recommandation</h3>
    <div class="pa-step">
        <div class="pa-step-num">1</div>
        <div class="pa-step-content">
            <strong>Extraction des features</strong>
            <p>Chaque film est décrit par 7 types de caractéristiques : synopsis, keywords, genres, décennie, langue, zone de production et popularité.</p>
        </div>
    </div>
    <div class="pa-step">
        <div class="pa-step-num">2</div>
        <div class="pa-step-content">
            <strong>Vectorisation & encodage</strong>
            <p>Le synopsis lemmatisé et les keywords sont transformés en vecteur TF-IDF (8 000 features max). Les genres passent par un MultiLabelBinarizer. Les variables catégorielles (décennie, langue, zone) sont one-hot encodées. Les votes sont log-transformés et normalisés.</p>
        </div>
    </div>
    <div class="pa-step">
        <div class="pa-step-num">3</div>
        <div class="pa-step-content">
            <strong>Concaténation pondérée</strong>
            <p>Tous les vecteurs sont combinés en une matrice creuse unique, avec des poids différents pour chaque feature selon son importance.</p>
        </div>
    </div>
    <div class="pa-step">
        <div class="pa-step-num">4</div>
        <div class="pa-step-content">
            <strong>KNN + similarité cosinus</strong>
            <p>Le modèle KNN (brute force, 50 voisins) calcule la distance cosinus entre le film sélectionné et l'ensemble du catalogue.</p>
        </div>
    </div>
    <div class="pa-step">
        <div class="pa-step-num">5</div>
        <div class="pa-step-content">
            <strong>Score hybride</strong>
            <p>Le classement final combine 75% de similarité cosinus et 25% de popularité (log des votes), pour équilibrer pertinence et accessibilité.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Poids des features
st.markdown("""
<div class="pa-card">
    <h3>Poids des features dans le modèle</h3>
    <div class="pa-weight-bar">
        <div class="pa-weight-label">Keywords (TF-IDF)</div>
        <div class="pa-weight-track"><div class="pa-weight-fill" style="width:100%;"></div></div>
        <div class="pa-weight-val">0.45</div>
    </div>
    <div class="pa-weight-bar">
        <div class="pa-weight-label">Synopsis (TF-IDF)</div>
        <div class="pa-weight-track"><div class="pa-weight-fill" style="width:67%;"></div></div>
        <div class="pa-weight-val">0.30</div>
    </div>
    <div class="pa-weight-bar">
        <div class="pa-weight-label">Genres</div>
        <div class="pa-weight-track"><div class="pa-weight-fill" style="width:20%;"></div></div>
        <div class="pa-weight-val">0.09</div>
    </div>
    <div class="pa-weight-bar">
        <div class="pa-weight-label">Décennie</div>
        <div class="pa-weight-track"><div class="pa-weight-fill" style="width:18%;"></div></div>
        <div class="pa-weight-val">0.08</div>
    </div>
    <div class="pa-weight-bar">
        <div class="pa-weight-label">Langue originale</div>
        <div class="pa-weight-track"><div class="pa-weight-fill" style="width:11%;"></div></div>
        <div class="pa-weight-val">0.05</div>
    </div>
    <div class="pa-weight-bar">
        <div class="pa-weight-label">Zone de production</div>
        <div class="pa-weight-track"><div class="pa-weight-fill" style="width:11%;"></div></div>
        <div class="pa-weight-val">0.05</div>
    </div>
    <div class="pa-weight-bar">
        <div class="pa-weight-label">Popularité (votes)</div>
        <div class="pa-weight-track"><div class="pa-weight-fill" style="width:7%;"></div></div>
        <div class="pa-weight-val">0.03</div>
    </div>
    <p style="margin-top:14px; font-size:0.82rem; color:#a89bb5 !important;">
        Les keywords TMDB dominent car ils capturent précisément les thèmes et concepts clés de chaque film
        (ex: "time travel", "dystopia", "heist"). Le synopsis complète avec le contexte narratif.
        Les métadonnées (genres, décennie, langue, zone) affinent le résultat.
        La popularité est volontairement faible pour éviter de toujours recommander les blockbusters.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# POURQUOI CES CHOIX
# =====================================================
st.markdown('<div class="pa-section-title">Pourquoi ces choix techniques ?</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="pa-card" style="min-height:220px;">
        <h3>KNN plutôt que deep learning ?</h3>
        <p>
            En cold start avec ~10 000 films, le KNN offre un excellent compromis entre
            performance et simplicité. Pas besoin d'entraîner un réseau de neurones : la similarité
            cosinus sur des features bien construites donne des résultats pertinents et interprétables.
            Le modèle est transparent — on sait pourquoi un film est recommandé.
        </p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="pa-card" style="min-height:220px;">
        <h3>TF-IDF plutôt que embeddings ?</h3>
        <p>
            Le TF-IDF est léger, rapide et fonctionne remarquablement sur des textes courts
            comme les synopsis. Les embeddings (Word2Vec, BERT) seraient pertinents pour un catalogue
            beaucoup plus large ou pour capturer des nuances sémantiques fines, mais ici le TF-IDF
            avec sous-pondération logarithmique suffit largement.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# PISTES D'AMÉLIORATION
# =====================================================
st.markdown('<div class="pa-section-title">Pistes d\'amélioration</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pa-card">
    <ul>
        <li><strong style="color:#ff2d78 !important;">Filtrage collaboratif</strong> — Dès que les utilisateurs
        noteront des films, intégrer leurs préférences pour passer à un modèle hybride (content + collaborative).</li>
        <li><strong style="color:#ff2d78 !important;">Embeddings sémantiques</strong> — Remplacer le TF-IDF par
        des embeddings de type Sentence-BERT pour mieux capturer le sens profond des synopsis.</li>
        <li><strong style="color:#ff2d78 !important;">A/B testing</strong> — Mesurer l'impact réel des
        recommandations sur l'engagement des utilisateurs.</li>
        <li><strong style="color:#ff2d78 !important;">Personnalisation par profil</strong> — Adapter les poids
        des features selon le profil utilisateur (cinéphile vs. grand public).</li>
        <li><strong style="color:#ff2d78 !important;">Notifications push</strong> — Envoyer des recommandations
        personnalisées par email ou notification lorsque de nouveaux films correspondent au profil.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# =====================================================
# CONTACT
# =====================================================
st.markdown('<hr style="border:none; height:2px; background:linear-gradient(90deg, transparent, rgba(255,45,120,0.5), transparent); margin:30px 0;">', unsafe_allow_html=True)

st.markdown("""
<div class="pa-contact-box">
    <h3>Contactez-nous</h3>
    <p><strong style="color:#ff2d78 !important;">Popcorn Analytics</strong></p>
    <p>6 rue d'Enghien, 69002 Lyon</p>
    <p>contact@popcorn-analytics.fr</p>
</div>
""", unsafe_allow_html=True)
