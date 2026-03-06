from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import numpy as np
import ast
from pathlib import Path
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import hstack, csr_matrix

app = FastAPI(title="Cinéma Creusois API", version="1.0")

# --------------------------------------------------
# CHARGEMENT DES DONNÉES AU DÉMARRAGE
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

df_movies = pd.read_parquet(DATA_DIR / "movies_fr_final.parquet")
if "id_film" in df_movies.columns:
    df_movies["id_film"] = df_movies["id_film"].astype(str)

knn_encoded_df = pd.read_parquet(DATA_DIR / "knn_df_encoded.parquet")
if "id_film" in knn_encoded_df.columns:
    knn_encoded_df["id_film"] = knn_encoded_df["id_film"].astype(str)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def parse_pylist(x):
    if x is None or (isinstance(x, float) and pd.isna(x)): return []
    if isinstance(x, list): return x
    s = str(x).strip()
    if s == "" or s.lower() in {"none", "nan", "null"}: return []
    try:
        v = ast.literal_eval(s)
        return v if isinstance(v, list) else []
    except Exception:
        return [p.strip() for p in s.strip("[]").replace("'", "").replace('"', "").split(",") if p.strip()]

def safe_val(val):
    """Convertir les types numpy/pandas en types Python natifs pour JSON."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, pd.Timestamp):
        return val.strftime("%d/%m/%Y")
    if isinstance(val, (list, np.ndarray)):
        return [safe_val(v) for v in val]
    return val

def movie_to_dict(row):
    """Convertir une ligne du dataframe en dictionnaire JSON-safe."""
    return {
        "id_film": str(row.get("id_film", "")),
        "titre_francais": safe_val(row.get("titre_francais")),
        "date_sortie": safe_val(row.get("date_sortie")),
        "note_moyenne": safe_val(row.get("note_moyenne")),
        "nombre_votes": safe_val(row.get("nombre_votes")),
        "genres_list": safe_val(row.get("genres_list")),
        "noms_realisateurs": safe_val(row.get("noms_realisateurs")),
        "principaux_acteurs": safe_val(row.get("principaux_acteurs")),
        "zone_de_production": safe_val(row.get("zone_de_production")),
        "langue_originale": safe_val(row.get("langue_originale")),
        "synopsis": safe_val(row.get("synopsis")),
        "synopsis_fr": safe_val(row.get("synopsis_fr")),
        "url_affiche": safe_val(row.get("url_affiche")),
        "slogan": safe_val(row.get("slogan")),
        "patrimonial": safe_val(row.get("patrimonial")),
    }

# --------------------------------------------------
# CONSTRUCTION DU MODÈLE KNN
# --------------------------------------------------
def build_knn():
    df = knn_encoded_df.copy()
    df = df.dropna(subset=["id_film", "titre_francais", "genres_list", "nombre_votes", "decennie"]).copy()
    df["id_film"] = df["id_film"].astype(str)
    df["nombre_votes"] = pd.to_numeric(df["nombre_votes"], errors="coerce")
    df["decennie"] = pd.to_numeric(df["decennie"], errors="coerce")
    df = df.dropna(subset=["nombre_votes", "decennie"]).copy()
    df["nombre_votes"] = df["nombre_votes"].astype(int)
    df["decennie"] = df["decennie"].astype(int)
    df["synopsis_clean"] = df["synopsis"].fillna("").astype(str)
    df["genres_list"] = df["genres_list"].apply(parse_pylist)
    df = df[df["genres_list"].apply(len) > 0].copy().reset_index(drop=True)

    votes_log = np.log1p(df["nombre_votes"].values.reshape(-1, 1))
    scaler_votes = StandardScaler(with_mean=False)
    X_votes = csr_matrix(scaler_votes.fit_transform(votes_log))
    mlb = MultiLabelBinarizer(sparse_output=True)
    X_genres = mlb.fit_transform(df["genres_list"]).tocsr()
    X_zone = csr_matrix(pd.get_dummies(df["zone_de_production"], prefix="zone", dummy_na=True).astype("int8").values)
    X_lang = csr_matrix(pd.get_dummies(df["langue_originale"], prefix="lang", dummy_na=True).astype("int8").values)
    X_dec = csr_matrix(pd.get_dummies(df["decennie"], prefix="dec", dummy_na=True).astype("int8").values)

    df["synopsis_clean"] = df["synopsis_clean"].str.lower().str.replace(r"[^a-z0-9\s]", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    tfidf = TfidfVectorizer(min_df=5, max_features=8000, ngram_range=(1, 1), stop_words="english", sublinear_tf=True, dtype=np.float32)
    X_syn = tfidf.fit_transform(df["synopsis_clean"])

    X_final = hstack([X_syn * 2.3, X_genres * 0.8, X_dec * 1.0, X_lang * 0.9, X_zone * 0.5, X_votes * 0.2]).tocsr()
    knn_model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=50)
    knn_model.fit(X_final)
    return df, X_final, knn_model

df_knn, X_final, knn_model = build_knn()

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API du Cinéma Creusois", "total_films": len(df_movies)}

@app.get("/films/")
def get_films(skip: int = 0, limit: int = 21, sort_by: str = "note_moyenne", ascending: bool = False):
    """Liste des films avec pagination et tri."""
    df = df_movies.copy()
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending, na_position="last")
    page = df.iloc[skip:skip + limit]
    return {"total": len(df), "films": [movie_to_dict(row) for _, row in page.iterrows()]}

@app.get("/films/search/")
def search_films(q: str = Query(..., min_length=1), limit: int = 20):
    """Rechercher un film par titre, réalisateur ou acteur."""
    ql = q.lower()
    mask = df_movies["titre_francais"].fillna("").str.lower().str.contains(ql, na=False)
    if "noms_realisateurs" in df_movies.columns:
        mask |= df_movies["noms_realisateurs"].fillna("").str.lower().str.contains(ql, na=False)
    if "principaux_acteurs" in df_movies.columns:
        mask |= df_movies["principaux_acteurs"].fillna("").str.lower().str.contains(ql, na=False)
    results = df_movies[mask].head(limit)
    return {"total": int(mask.sum()), "films": [movie_to_dict(row) for _, row in results.iterrows()]}

@app.get("/films/{film_id}")
def get_film(film_id: str):
    """Détails d'un film par son ID."""
    row = df_movies[df_movies["id_film"] == film_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Film non trouvé")
    return movie_to_dict(row.iloc[0])

@app.get("/films/{film_id}/recommendations")
def get_recommendations(film_id: str, k: int = 5):
    """Recommandations pour un film donné."""
    film_id = str(film_id)
    match = df_knn.index[df_knn["id_film"] == film_id]
    if len(match) == 0:
        raise HTTPException(status_code=404, detail="Film non trouvé dans le modèle")

    idx = int(match[0])
    n = min(80, X_final.shape[0])
    distances, indices = knn_model.kneighbors(X_final[idx], n_neighbors=n)
    distances, indices = distances.ravel(), indices.ravel()
    mask = indices != idx
    distances, indices = distances[mask], indices[mask]

    if len(indices) == 0:
        return {"film_id": film_id, "recommendations": []}

    # Score hybride : similarité + popularité
    pop = np.log1p(df_knn.loc[indices, "nombre_votes"].fillna(0).astype(float).values)
    pop_norm = (pop - pop.min()) / (pop.max() - pop.min() + 1e-9)
    sim = 1 - distances
    sim_norm = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)
    alpha_pop = 0.25
    final = (1 - alpha_pop) * sim_norm + alpha_pop * pop_norm
    indices = indices[np.argsort(final)[::-1]]

    rec_ids = df_knn.loc[indices[:k * 3], "id_film"].astype(str).tolist()
    out = df_movies[df_movies["id_film"].isin(rec_ids)].copy()
    out["__rank"] = out["id_film"].map({mid: i for i, mid in enumerate(rec_ids)})
    out = out.sort_values("__rank").drop(columns="__rank").head(k)

    return {
        "film_id": film_id,
        "recommendations": [movie_to_dict(row) for _, row in out.iterrows()]
    }

@app.get("/films/patrimonial/")
def get_patrimonial(limit: int = 50):
    """Films patrimoniaux."""
    pat = df_movies[df_movies["patrimonial"].astype(str).str.strip().str.lower() == "yes"]
    if "note_moyenne" in pat.columns:
        pat = pat.sort_values("note_moyenne", ascending=False)
    pat = pat.head(limit)
    return {"total": len(pat), "films": [movie_to_dict(row) for _, row in pat.iterrows()]}

@app.get("/stats/")
def get_stats():
    """Statistiques globales du catalogue."""
    return {
        "total_films": len(df_movies),
        "note_moyenne_globale": round(float(df_movies["note_moyenne"].mean()), 2) if "note_moyenne" in df_movies.columns else None,
        "annee_min": int(df_movies["date_sortie"].dt.year.min()) if "date_sortie" in df_movies.columns else None,
        "annee_max": int(df_movies["date_sortie"].dt.year.max()) if "date_sortie" in df_movies.columns else None,
        "total_patrimoniaux": int((df_movies["patrimonial"].astype(str).str.strip().str.lower() == "yes").sum()) if "patrimonial" in df_movies.columns else 0,
    }