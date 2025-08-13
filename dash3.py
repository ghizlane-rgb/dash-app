import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import numpy as np
import warnings
import os

# Supprimer les warnings
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Voitures",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de l'API Lambda
LAMBDA_URL = "https://w7e62hoex6.execute-api.us-east-1.amazonaws.com/prod/getScrapingData"

@st.cache_data(ttl=300, show_spinner=False)  # Cache pendant 5 minutes
def load_data():
    """Charge les données depuis l'API Lambda"""
    try:
        response = requests.get(LAMBDA_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Convertir en DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            if 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
        else:
            return pd.DataFrame()

        # Nettoyage des colonnes numériques
        for col in ['Km', 'Prix', 'Mc']:
            if col in df.columns:
                cleaned = df[col].astype(str).str.replace(r'[^0-9]', '', regex=True)
                cleaned = cleaned.replace('', pd.NA)
                df[col] = pd.to_numeric(cleaned, errors='coerce')

        # Conversion de la date
        if 'DateScraping' in df.columns:
            df['DateScraping'] = pd.to_datetime(df['DateScraping'], errors='coerce')

        return df

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de la récupération des données: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement des données: {e}")
        return pd.DataFrame()

def apply_filters(df):
    """Applique les filtres sélectionnés par l'utilisateur"""
    filtered_df = df.copy()
    
    # Filtres dans la sidebar
    st.sidebar.header("🔍 Filtres")
    
    # Filtre par Source
    if 'Source' in df.columns:
        sources = ['Tous'] + sorted(df['Source'].dropna().unique().tolist())
        selected_source = st.sidebar.selectbox("📍 Source", sources)
        if selected_source != 'Tous':
            filtered_df = filtered_df[filtered_df['Source'] == selected_source]
    
    # Filtre par Transmission
    if 'Transmission' in df.columns:
        transmissions = ['Tous'] + sorted(df['Transmission'].dropna().unique().tolist())
        selected_transmission = st.sidebar.selectbox("⚙️ Transmission", transmissions)
        if selected_transmission != 'Tous':
            filtered_df = filtered_df[filtered_df['Transmission'] == selected_transmission]
    
    # Filtre par Carburant
    if 'Carburant' in df.columns:
        carburants = ['Tous'] + sorted(df['Carburant'].dropna().unique().tolist())
        selected_carburant = st.sidebar.selectbox("⛽ Carburant", carburants)
        if selected_carburant != 'Tous':
            filtered_df = filtered_df[filtered_df['Carburant'] == selected_carburant]
    
    # Filtre par Statut
    if 'Statut' in df.columns:
        statuts = ['Tous'] + sorted(df['Statut'].dropna().unique().tolist())
        selected_statut = st.sidebar.selectbox("📊 Statut", statuts)
        if selected_statut != 'Tous':
            filtered_df = filtered_df[filtered_df['Statut'] == selected_statut]
    
    # Filtre par Marque
    if 'Marque' in df.columns:
        marques = ['Tous'] + sorted(df['Marque'].dropna().unique().tolist())
        selected_marque = st.sidebar.selectbox("🏷️ Marque", marques)
        if selected_marque != 'Tous':
            filtered_df = filtered_df[filtered_df['Marque'] == selected_marque]
    
    # Filtre par État
    if 'Etat' in df.columns:
        etats = ['Tous'] + sorted(df['Etat'].dropna().unique().tolist())
        selected_etat = st.sidebar.selectbox("🔧 État", etats)
        if selected_etat != 'Tous':
            filtered_df = filtered_df[filtered_df['Etat'] == selected_etat]
    
    
    
    return filtered_df

def display_kpis(df):
    """Affiche les KPIs principaux"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚗 Total Voitures", len(df))
    
    with col2:
        if 'Prix' in df.columns and not df['Prix'].isna().all():
            prix_moyen = df['Prix'].mean()
            st.metric("💰 Prix Moyen", f"{prix_moyen:,.0f} MAD" if not pd.isna(prix_moyen) else "N/A")
    
    with col3:
        if 'Km' in df.columns and not df['Km'].isna().all():
            km_moyen = df['Km'].mean()
            st.metric("📊 KM Moyen", f"{km_moyen:,.0f}" if not pd.isna(km_moyen) else "N/A")
    
    with col4:
        if 'Source' in df.columns:
            nb_sources = df['Source'].nunique()
            st.metric("📍 Sources", nb_sources)

def display_charts(df):
    """Affiche tous les graphiques"""
    
    # Première ligne de graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Source' in df.columns and not df['Source'].isna().all():
            st.subheader("📍 Répartition par Source")
            source_counts = df['Source'].value_counts()
            fig = px.histogram(
                df,
                x='Source',
                title="Nombre de voitures par Source",
                color='Source'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Transmission' in df.columns and not df['Transmission'].isna().all():
            st.subheader("⚙️ Répartition par Transmission")
            fig = px.histogram(
                df, 
                x='Transmission', 
                title="Nombre de voitures par transmission",
                color='Transmission'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Deuxième ligne de graphiques
    col3, col4 = st.columns(2)
    
    with col3:
        if 'Carburant' in df.columns and not df['Carburant'].isna().all():
            st.subheader("⛽ Répartition par Carburant")
            fig = px.histogram(
                df, 
                x='Carburant', 
                title="Nombre de voitures par carburant",
                color='Carburant'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        if 'Etat' in df.columns and not df['Etat'].isna().all():
            st.subheader("🔧 Répartition par État")
            fig = px.histogram(
                df, 
                x='Etat', 
                title="Nombre de voitures par état",
                color='Etat'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Graphiques sur toute la largeur
    if 'Marque' in df.columns and not df['Marque'].isna().all():
        st.subheader("🏷️ Top 10 des Marques")
        top_marques = df['Marque'].value_counts().head(10)
        fig = px.bar(
            x=top_marques.index,
            y=top_marques.values,
            title="Top 10 des marques les plus représentées",
            labels={'x': 'Marque', 'y': 'Nombre de voitures'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    if 'DateScraping' in df.columns and not df['DateScraping'].isna().all():
        st.subheader("📅 Évolution temporelle")
        
        # Grouper par date
        date_counts = df.groupby(df['DateScraping'].dt.date).size().reset_index()
        date_counts.columns = ['Date', 'Nombre']
        
        fig = px.line(
            date_counts,
            x='Date',
            y='Nombre',
            title="Évolution du nombre de voitures scrapées par date",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    

def display_statistics(df):
    """Affiche les statistiques détaillées"""
    st.subheader("📊 Statistiques Détaillées")
    
    numerical_cols = ['Km', 'Prix', 'Mc']
    available_cols = [col for col in numerical_cols if col in df.columns and not df[col].isna().all()]
    
    if available_cols:
        stats_df = pd.DataFrame()
        
        for col in available_cols:
            stats_df[col] = [
                df[col].mean(),
                df[col].median(),
                df[col].std(),
                df[col].min(),
                df[col].max(),
                df[col].count()
            ]
        
        stats_df.index = ['Moyenne', 'Médiane', 'Écart-type', 'Minimum', 'Maximum', 'Nombre de valeurs']
        
        # Formatage des nombres
        stats_df = stats_df.round(2)
        
        st.dataframe(stats_df, use_container_width=True)
    else:
        st.info("Aucune donnée numérique disponible pour les statistiques.")

def main():
    # En-tête
    st.title("🚗 Dashboard Voitures")
    st.markdown("---")
    
    # Chargement des données avec spinner
    with st.spinner("🔄 Chargement des données en cours..."):
        df = load_data()
    
    if df.empty:
        st.error("❌ Aucune donnée disponible.")
        st.stop()
    
    # Affichage du nombre total d'enregistrements
    st.success(f"✅ {len(df)} voitures chargées avec succès")
    
    # Application des filtres
    filtered_df = apply_filters(df)
    
    # Information sur le filtrage
    if len(filtered_df) != len(df):
        st.info(f"🔍 {len(filtered_df)} voitures correspondent aux filtres sélectionnés (sur {len(df)} total)")
    
    # Affichage des KPIs
    display_kpis(filtered_df)
    st.markdown("---")
    
    # Onglets pour organiser le contenu
    tab1, tab2, tab3 = st.tabs(["📈 Graphiques", "📊 Statistiques", "🗂️ Données"])
    
    with tab1:
        display_charts(filtered_df)
    
    with tab2:
        display_statistics(filtered_df)
        
        # Analyse par catégorie
        st.subheader("🏷️ Analyse par Catégories")
        categorical_cols = ['Source', 'Etat', 'Transmission', 'Carburant', 'Statut', 'Marque']
        available_cat_cols = [col for col in categorical_cols if col in filtered_df.columns]
        
        for col in available_cat_cols:
            if not filtered_df[col].isna().all():
                st.write(f"**{col}:**")
                category_counts = filtered_df[col].value_counts()
                st.dataframe(category_counts.to_frame('Nombre'), use_container_width=True)
                st.markdown("---")
    
    with tab3:
        st.subheader("🗂️ Données Brutes")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Bouton de téléchargement
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger les données filtrées (CSV)",
            data=csv,
            file_name=f"voitures_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Sidebar avec informations supplémentaires
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Informations")
    st.sidebar.info(f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    if st.sidebar.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.subheader("created by ghizlane chtouki")
if __name__ == "__main__":
    main()