"""
Générateur de données test pour tester les fonctionnalités de visualisation.
Crée des datasets réalistes pour différents domaines métier.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random


class DataGenerator:
    """Générateur de données test pour l'application."""
    
    def __init__(self, seed: int = 42):
        """
        Initialise le générateur avec une graine pour la reproductibilité.
        
        Args:
            seed: Graine pour la génération aléatoire
        """
        np.random.seed(seed)
        random.seed(seed)
    
    def generate_sales_data(self, n_records: int = 1000) -> pd.DataFrame:
        """
        Génère des données de ventes fictives.
        
        Args:
            n_records: Nombre d'enregistrements à générer
            
        Returns:
            DataFrame avec les colonnes: date, region, produit, vendeur, quantite, prix_unitaire, chiffre_affaires
        """
        # Régions françaises
        regions = ["Île-de-France", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine", 
                  "Occitanie", "Hauts-de-France", "Grand Est", "Provence-Alpes-Côte d'Azur"]
        
        # Produits
        produits = ["Ordinateur Portable", "Smartphone", "Tablette", "Écouteurs", 
                   "Montre Connectée", "Appareil Photo", "Console de Jeux"]
        
        # Vendeurs
        vendeurs = ["Marie Dupont", "Jean Martin", "Sophie Bernard", "Pierre Durand", 
                   "Claire Moreau", "Luc Simon", "Emma Petit", "Thomas Robert"]
        
        # Génération des dates (12 derniers mois)
        start_date = datetime.now() - timedelta(days=365)
        dates = [start_date + timedelta(days=x) for x in range(365)]
        
        data = []
        for _ in range(n_records):
            region = random.choice(regions)
            produit = random.choice(produits)
            vendeur = random.choice(vendeurs)
            date = random.choice(dates)
            
            # Prix selon le produit
            prix_base = {
                "Ordinateur Portable": 800, "Smartphone": 600, "Tablette": 400,
                "Écouteurs": 150, "Montre Connectée": 300, "Appareil Photo": 1200,
                "Console de Jeux": 500
            }
            
            prix_unitaire = prix_base[produit] * random.uniform(0.8, 1.3)
            quantite = random.randint(1, 5)
            chiffre_affaires = prix_unitaire * quantite
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "region": region,
                "produit": produit,
                "vendeur": vendeur,
                "quantite": quantite,
                "prix_unitaire": round(prix_unitaire, 2),
                "chiffre_affaires": round(chiffre_affaires, 2)
            })
        
        return pd.DataFrame(data)
    
    def generate_customer_data(self, n_records: int = 500) -> pd.DataFrame:
        """
        Génère des données clients fictives.
        
        Args:
            n_records: Nombre de clients à générer
            
        Returns:
            DataFrame avec les données clients
        """
        prenoms_f = ["Marie", "Anne", "Sophie", "Claire", "Emma", "Julie", "Sarah"]
        prenoms_m = ["Jean", "Pierre", "Paul", "Michel", "Luc", "Thomas", "Nicolas"]
        noms = ["Martin", "Bernard", "Durand", "Petit", "Robert", "Richard", "Moreau"]
        villes = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg"]
        
        data = []
        for i in range(n_records):
            sexe = random.choice(["F", "M"])
            prenom = random.choice(prenoms_f if sexe == "F" else prenoms_m)
            nom = random.choice(noms)
            
            age = random.randint(18, 75)
            ville = random.choice(villes)
            salaire = random.randint(20000, 100000)
            score_satisfaction = random.uniform(1, 5)
            nb_commandes = random.randint(0, 50)
            
            data.append({
                "client_id": f"C{i+1:04d}",
                "nom_complet": f"{prenom} {nom}",
                "age": age,
                "sexe": sexe,
                "ville": ville,
                "salaire_annuel": salaire,
                "score_satisfaction": round(score_satisfaction, 1),
                "nb_commandes": nb_commandes,
                "valeur_client": round(salaire * 0.02 * score_satisfaction, 2)
            })
        
        return pd.DataFrame(data)
    
    def generate_financial_data(self, n_records: int = 200) -> pd.DataFrame:
        """
        Génère des données financières fictives.
        
        Returns:
            DataFrame avec des données financières mensuelles
        """
        start_date = datetime(2020, 1, 1)
        dates = [start_date + timedelta(days=30*i) for i in range(n_records)]
        
        # Simulation d'une tendance croissante avec du bruit
        base_revenue = 100000
        data = []
        
        for i, date in enumerate(dates):
            trend = base_revenue * (1 + 0.02 * i)  # Croissance de 2% par mois
            noise = np.random.normal(0, trend * 0.1)  # Bruit de 10%
            revenue = max(0, trend + noise)
            
            costs = revenue * random.uniform(0.6, 0.8)
            profit = revenue - costs
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "chiffre_affaires": round(revenue, 2),
                "couts": round(costs, 2),
                "benefice": round(profit, 2),
                "marge": round((profit / revenue) * 100, 1),
                "trimestre": f"Q{((date.month-1)//3)+1} {date.year}"
            })
        
        return pd.DataFrame(data)
    
    def generate_survey_data(self, n_records: int = 300) -> pd.DataFrame:
        """
        Génère des données d'enquête de satisfaction.
        
        Returns:
            DataFrame avec des réponses d'enquête
        """
        services = ["Service Client", "Livraison", "Qualité Produit", "Prix", "Site Web"]
        ages_groups = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
        
        data = []
        for i in range(n_records):
            service = random.choice(services)
            age_group = random.choice(ages_groups)
            
            # Corrélation entre âge et satisfaction
            base_satisfaction = {
                "18-25": 3.2, "26-35": 3.5, "36-45": 3.8,
                "46-55": 4.0, "56-65": 4.2, "65+": 4.1
            }
            
            satisfaction = max(1, min(5, 
                np.random.normal(base_satisfaction[age_group], 0.8)))
            
            data.append({
                "repondant_id": f"R{i+1:04d}",
                "service_evalue": service,
                "tranche_age": age_group,
                "note_satisfaction": round(satisfaction, 1),
                "recommandation": random.choice(["Oui", "Non", "Peut-être"]),
                "date_reponse": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")
            })
        
        return pd.DataFrame(data)
    
    def get_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Retourne tous les datasets disponibles.
        
        Returns:
            Dictionnaire avec nom -> DataFrame
        """
        return {
            "Données de Ventes": self.generate_sales_data(),
            "Données Clients": self.generate_customer_data(),
            "Données Financières": self.generate_financial_data(),
            "Enquête de Satisfaction": self.generate_survey_data()
        }
    
    def save_datasets_to_csv(self, output_dir: str = "./data"):
        """
        Sauvegarde tous les datasets en CSV.
        
        Args:
            output_dir: Répertoire de sortie
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        datasets = self.get_all_datasets()
        for name, df in datasets.items():
            filename = name.lower().replace(" ", "_").replace("é", "e") + ".csv"
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"Dataset '{name}' sauvegardé: {filepath}")


if __name__ == "__main__":
    # Test du générateur
    generator = DataGenerator()
    generator.save_datasets_to_csv()