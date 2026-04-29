import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import io
from datetime import datetime, date

# ══════════════════════════════════════════════
#  CONFIGURATION DE LA PAGE
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="AgroData 237 — Plateforme Agricole",
    page_icon="🌿",
    layout="wide"
)

# Style Cyber-Agro 2026
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    :root {
        --bg-deep: #050A0E;
        --glass: rgba(15, 23, 42, 0.65);
        --glass-border: rgba(255, 255, 255, 0.08);
        --accent-primary: #00F2FF; /* Cyber Cyan */
        --accent-secondary: #7000FF; /* Electric Purple */
        --accent-success: #00FF85; /* Neon Green */
        --accent-warning: #FFB800; /* Gold */
        --text-main: #F1F5F9;
        --text-dim: #94A3B8;
    }

    .stApp {
        background: radial-gradient(circle at 0% 0%, #0c1a26 0%, #050A0E 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-main);
    }

    /* Sidebar Cyber */
    [data-testid="stSidebar"] {
        background: rgba(5, 10, 14, 0.95) !important;
        border-right: 1px solid var(--glass-border) !important;
        backdrop-filter: blur(20px);
    }
    [data-testid="stSidebar"] h1 {
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* Glass Cards */
    [data-testid="metric-container"], .stPlotlyChart, [data-testid="stForm"] {
        background: var(--glass) !important;
        border: 1px solid var(--glass-border) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    [data-testid="metric-container"]:hover {
        border-color: var(--accent-primary) !important;
        transform: translateY(-5px);
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.2) !important;
    }

    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        color: var(--accent-primary) !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-dim) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.7rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: var(--glass) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        color: var(--text-dim) !important;
        padding: 8px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        border-color: var(--accent-primary) !important;
        color: var(--accent-primary) !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        color: white !important;
        box-shadow: 0 10px 20px -5px rgba(112, 0, 255, 0.4) !important;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 30px -5px rgba(112, 0, 255, 0.6) !important;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stNumberInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-deep); }
    ::-webkit-scrollbar-thumb { background: var(--glass-border); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-primary); }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  LOGIQUE DE DONNÉES
# ══════════════════════════════════════════════
PALETTE = ["#00F2FF", "#7000FF", "#00FF85", "#FFB800", "#FF005C", "#0075FF"]
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94A3B8", size=11),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zeroline=False, title_font=dict(size=12)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zeroline=False, title_font=dict(size=12)),
    margin=dict(l=40, r=20, t=40, b=40)
)

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

def load_demo_data():
    np.random.seed(42)
    n = 200
    regions = ["Centre", "Littoral", "Ouest", "Nord", "Sud", "Est", "Adamaoua"]
    cultures = ["Cacao", "Café", "Maïs", "Manioc", "Plantain", "Tomate"]
    
    df = pd.DataFrame({
        "ID": [f"PAR-{i+1000}" for i in range(n)],
        "Région": np.random.choice(regions, n),
        "Culture": np.random.choice(cultures, n),
        "Surface (ha)": np.random.uniform(0.5, 15.0, n).round(2),
        "Rendement (t/ha)": np.random.normal(4.5, 1.2, n).round(2),
        "pH Sol": np.random.normal(6.2, 0.5, n).round(1),
        "Pluviométrie (mm)": np.random.normal(1500, 300, n).round(0),
        "Revenu (FCFA)": np.random.normal(500000, 150000, n).astype(int),
        "Date": [date(2024, np.random.randint(1,13), np.random.randint(1,28)) for _ in range(n)]
    })
    st.session_state.data = df
    st.success("✅ 200 parcelles de démonstration chargées !")

# ══════════════════════════════════════════════
#  BARRE LATÉRALE (NAVIGATION)
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div style="text-align: center; padding-bottom: 20px;"><span style="font-size: 50px;">🌿</span></div>', unsafe_allow_html=True)
    st.title("AgroData 237")
    st.markdown("*Analyse de données agricoles*")
    
    menu = st.radio("Navigation principale", [
        "🏠  Accueil & Tableau de bord", 
        "📝  Saisie des parcelles", 
        "🔢  Analyses statistiques", 
        "📊  Exploration graphique", 
        "📥  Exportation des données"
    ])
    
    st.divider()
    if st.button("📥 Charger les données de test"):
        load_demo_data()
    
    if st.button("🗑️ Réinitialiser l'application"):
        st.session_state.data = pd.DataFrame()
        st.rerun()

    st.markdown("---")
    st.caption("✍️ Réalisé par : NGAH FRANC")
    st.caption("🎓 Université de Yaoundé I")

# ══════════════════════════════════════════════
#  CONTENU PRINCIPAL
# ══════════════════════════════════════════════
df = st.session_state.data

if "Accueil" in menu:
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 3rem; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 2rem;">
            <h1 style="background: linear-gradient(90deg, #00F2FF, #7000FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; font-size: 3rem;">AgroData 237 <span style="font-size: 1rem; -webkit-text-fill-color: #94A3B8;">Analyse Expert</span></h1>
            <p style="color: #94A3B8; margin: 1rem 0 0; font-size: 1.1rem; letter-spacing: 1px;">PLATEFORME DE GESTION ET D'ANALYSE DES CULTURES AU CAMEROUN</p>
        </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.warning("Aucune donnée disponible. Utilisez le menu à gauche pour charger la démo ou saisir des parcelles.")
    else:
        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Parcelles", len(df))
        c2.metric("Rendement Moyen", f"{df['Rendement (t/ha)'].mean():.2f} t/ha")
        c3.metric("Surface Totale", f"{df['Surface (ha)'].sum():.1f} ha")
        c4.metric("Revenu Moyen", f"{df['Revenu (FCFA)'].mean():,.0f} FCFA")
        
        st.divider()
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("### 💠 Répartition par Type de Culture")
            fig = px.pie(df, names="Culture", hole=0.6, color_discrete_sequence=PALETTE)
            fig.update_layout(CHART_THEME)
            st.plotly_chart(fig, use_container_width=True, key="dash_pie")
            
        with col_right:
            st.markdown("### 📊 Performance par Région (t/ha)")
            fig = px.bar(df.groupby("Région")["Rendement (t/ha)"].mean().reset_index().sort_values("Rendement (t/ha)"), 
                         x="Rendement (t/ha)", y="Région", orientation="h", color="Rendement (t/ha)", 
                         color_continuous_scale="Viridis")
            fig.update_layout(CHART_THEME, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True, key="dash_bar_reg")

        # Analyses intelligentes
        st.markdown("### 🔍 Analyses clés du système")
        insights = []
        if not df.empty:
            insights.append(f"Rendement moyen optimisé : {df['Rendement (t/ha)'].mean():.2f} t/ha")
            insights.append(f"Culture dominante détectée : {df['Culture'].value_counts().idxmax()}")
            insights.append(f"Potentiel de revenu global : {df['Revenu (FCFA)'].sum():,.0f} FCFA")
        
        c_ins1, c_ins2 = st.columns(2)
        for i, ins in enumerate(insights):
            with (c_ins1 if i % 2 == 0 else c_ins2):
                st.markdown(f"""
                    <div style="background: var(--glass); border-left: 4px solid var(--accent-primary); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
                        <span style="color: var(--accent-primary); font-size: 1.2rem; margin-right: 10px;">⚡</span>
                        <span style="color: var(--text-main); font-size: 0.95rem;">{ins}</span>
                    </div>
                """, unsafe_allow_html=True)

elif "Saisie" in menu:
    st.header("📋 Formulaire de Collecte")
    
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        with c1:
            f_id = st.text_input("Identifiant Parcelle", value=f"PAR-{len(df)+1001}")
            f_region = st.selectbox("Région", ["Centre", "Littoral", "Ouest", "Nord", "Sud", "Est", "Adamaoua"])
            f_culture = st.selectbox("Culture", ["Cacao", "Café", "Maïs", "Manioc", "Plantain", "Tomate"])
            f_surface = st.number_input("Surface (ha)", 0.1, 100.0, 1.0)
        with c2:
            f_rend = st.number_input("Rendement (t/ha)", 0.0, 50.0, 3.5)
            f_ph = st.slider("pH du sol", 3.0, 9.0, 6.0)
            f_pluvio = st.number_input("Pluviométrie (mm)", 0, 5000, 1200)
            f_revenu = st.number_input("Revenu estimé (FCFA)", 0, 10000000, 250000)
        
        submitted = st.form_submit_button("Enregistrer la fiche")
        if submitted:
            new_row = {
                "ID": f_id, "Région": f_region, "Culture": f_culture,
                "Surface (ha)": f_surface, "Rendement (t/ha)": f_rend,
                "pH Sol": f_ph, "Pluviométrie (mm)": f_pluvio,
                "Revenu (FCFA)": f_revenu, "Date": date.today()
            }
            st.session_state.data = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Donnée enregistrée !")
            st.rerun()

elif "Analyses" in menu:
    st.header("📉 Statistiques Avancées")
    
    if df.empty:
        st.error("Veuillez d'abord charger des données.")
    else:
        # Stats descriptives globales
        st.subheader("Indicateurs de tendance centrale et de dispersion")
        numeric_df = df.select_dtypes(include=[np.number])
        stats_table = numeric_df.describe().T
        
        # Ajout Skewness et Kurtosis
        stats_table['Skewness'] = numeric_df.skew()
        stats_table['Kurtosis'] = numeric_df.kurt()
        
        st.dataframe(stats_table.style.format("{:.2f}"), use_container_width=True)
        
        st.divider()
        
        # Test de Normalité
        st.subheader("Test de Normalité (Shapiro-Wilk)")
        var_to_test = st.selectbox("Choisir une variable", numeric_df.columns)
        shapiro_test = stats.shapiro(df[var_to_test].dropna())
        
        c1, c2 = st.columns(2)
        c1.metric("Statistique W", f"{shapiro_test.statistic:.4f}")
        c2.metric("P-Value", f"{shapiro_test.pvalue:.4f}")
        
        if shapiro_test.pvalue > 0.05:
            st.success(f"La distribution de '{var_to_test}' semble suivre une loi normale (p > 0.05).")
        else:
            st.warning(f"La distribution de '{var_to_test}' ne semble pas suivre une loi normale.")

elif "graphique" in menu:
    st.header("📈 Visualisation interactive")
    
    if df.empty:
        st.error("Aucune donnée disponible. Veuillez d'abord charger ou saisir des données.")
    else:
        tab1, tab2, tab3 = st.tabs(["📊 Distributions", "🔗 Corrélations", "🌡️ Matrice thermique"])
        
        with tab1:
            st.markdown("#### Étude de la dispersion des variables")
            var = st.selectbox("Choisir la mesure à analyser", ["Rendement (t/ha)", "Surface (ha)", "pH Sol", "Pluviométrie (mm)"], key="v1")
            fig = px.histogram(df, x=var, nbins=30, marginal="box", color_discrete_sequence=[PALETTE[2]], opacity=0.8)
            fig.update_layout(CHART_THEME)
            st.plotly_chart(fig, use_container_width=True, key="graph_hist")
            
        with tab2:
            st.markdown("#### Analyse de la relation entre variables")
            c_g1, c_g2 = st.columns(2)
            x_ax = c_g1.selectbox("Variable en abscisse (X)", ["Surface (ha)", "Pluviométrie (mm)", "pH Sol"], key="x1")
            y_ax = c_g2.selectbox("Variable en ordonnée (Y)", ["Rendement (t/ha)", "Revenu (FCFA)"], key="y1")
            try:
                fig = px.scatter(df, x=x_ax, y=y_ax, color="Culture", trendline="ols", color_discrete_sequence=PALETTE, 
                                 title=f"Relation entre {x_ax} et {y_ax}")
                fig.update_layout(CHART_THEME)
                st.plotly_chart(fig, use_container_width=True, key="graph_scatter")
            except:
                fig = px.scatter(df, x=x_ax, y=y_ax, color="Culture", color_discrete_sequence=PALETTE)
                fig.update_layout(CHART_THEME)
                st.plotly_chart(fig, use_container_width=True, key="graph_scatter_fail")

        with tab3:
            st.markdown("#### Matrice de corrélation de Pearson")
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            corr_matrix = df[numeric_cols].corr().round(2)
            fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu_r", aspect="auto")
            fig.update_layout(CHART_THEME)
            st.plotly_chart(fig, use_container_width=True, key="graph_heatmap")

elif "Exportation" in menu:
    st.header("💾 Exporter les Résultats")
    
    if df.empty:
        st.error("Aucune donnée à exporter.")
    else:
        st.write("Aperçu des données finales :")
        st.dataframe(df.head(10), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        # CSV Export
        csv = df.to_csv(index=False).encode('utf-8')
        col1.download_button("📥 Télécharger CSV", data=csv, file_name="agrodata_export.csv", mime="text/csv")
        
        # Excel Export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Donnees')
        col2.download_button("📥 Télécharger Excel", data=output.getvalue(), file_name="agrodata_export.xlsx")

st.divider()
st.caption("AgroData 237 • Développé pour le TP INF 232 - 2026 • © 2024")
