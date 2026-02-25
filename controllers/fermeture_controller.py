"""
Controleur metier pour le workflow de fermeture/livraison des commandes.
"""

from typing import Dict, List, Optional

from models.database import CommandeModel


class FermetureController:
    """Orchestre les operations metier de fermeture sans UI Streamlit."""

    def __init__(self, db_connection):
        self.commande_model = CommandeModel(db_connection)

    def lister_commandes_avec_reste(
        self,
        couturier_id: int,
        salon_id: str,
        date_debut=None,
        date_fin=None,
    ) -> List[Dict]:
        return self.commande_model.lister_commandes_avec_reste_a_payer(
            couturier_id=couturier_id,
            salon_id=salon_id,
            date_debut=date_debut,
            date_fin=date_fin,
        )

    def enregistrer_modification_paiement(
        self,
        commande_id: int,
        prix_total: float,
        avance: float,
        reste: float,
    ) -> bool:
        ok = self.commande_model.modifier_prix_commande(
            commande_id=commande_id,
            prix_total=prix_total,
            avance=avance,
            reste=reste,
        )
        if ok and reste <= 0:
            self.commande_model.marquer_commande_terminee(commande_id)
        return ok

    def lister_commandes_terminees(
        self,
        salon_id: str,
        couturier_id: Optional[int] = None,
        date_debut=None,
        date_fin=None,
        statut: str = "Terminé",
    ) -> List[Dict]:
        return self.commande_model.lister_commandes_terminees(
            salon_id=salon_id,
            couturier_id=couturier_id,
            date_debut=date_debut,
            date_fin=date_fin,
            statut=statut,
        )

    def demandes_en_attente_map(self) -> Dict[int, Dict]:
        demandes = self.commande_model.lister_demandes_validation()
        return {
            d.get("commande_id"): d
            for d in demandes
            if d.get("type_action") == "fermeture_demande"
        }

    def demandes_stats_par_commandes(self, couturier_id: int, commande_ids: List[int]) -> Dict[int, Dict]:
        return self.commande_model.compter_demandes_fermeture_par_commandes(couturier_id, commande_ids)

    def demande_resume_commande(self, commande_id: int, couturier_id: int) -> Dict:
        return self.commande_model.compter_demandes_fermeture_commande(commande_id, couturier_id)

    def valider_livraison(self, commande_id: int) -> bool:
        return self.commande_model.marquer_commande_livree_payee(commande_id)
