import streamlit as st
import pymongo
import requests
from pymongo import MongoClient

def main():
    API_KEY = st.secrets["api_keys"]["GRID_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    st.title("Recherche de matchs par équipe")

    # 1) Connexion MongoDB
    CONNECTION_STRING = st.secrets["connection_strings"]["CONNECTION_STRING"]
    client = MongoClient(CONNECTION_STRING)  
    db = client["GRID_Data"]  
    collection = db["Match_Data"]  

    # 2) Champ de texte pour rechercher une équipe
    team_name = st.text_input("Entrez le nom d'une équipe :")

    # 3) Lorsque l'utilisateur saisit un nom d'équipe
    if team_name:
        # On recherche les matchs dans lesquels l'équipe saisie apparaît 
        # soit en tant que blue_team, soit en tant que red_team.
        # "$options": "i" permet de faire une recherche insensible à la casse.
        query = {
            "$or": [
                {"blue_team": {"$regex": team_name, "$options": "i"}},
                {"red_team": {"$regex": team_name, "$options": "i"}}
            ]
        }
        matches = list(collection.find(query))

        if matches:
            st.subheader(f"Résultats pour l'équipe : {team_name}")
            # 4) Parcourir les matches et afficher les informations
            for match in matches:
                series_id       = match["series_id"]
                blue_team       = match["blue_team"]
                red_team        = match["red_team"]
                tournament_name = match["tournament_name"]

                # Affichage basique
                st.write(f"**{blue_team} vs {red_team}**")
                st.write(f"Tournament: {tournament_name}")

                # Construction de l’URL du replay
                replay_url = f"https://api.grid.gg/file-download/replay/riot/series/{series_id}/games/1"

                # Méthode 2 : st.download_button 
                # (prend en charge le téléchargement direct, mais attention à la taille du fichier)
                replay_data = requests.get(replay_url, headers=headers).content
                st.download_button(
                    label="Télécharger le replay",
                    data=replay_data,
                    file_name=f"{blue_team}_vs_{red_team}_game1.rofl"
                )

                st.write("---")
        else:
            st.write("Aucun match trouvé pour cette équipe.")
    else:
        st.write("Veuillez saisir le nom d'une équipe ci-dessus pour afficher les matchs correspondants.")

if __name__ == "__main__":
    main()
