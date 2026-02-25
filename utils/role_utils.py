"""
Utilitaires pour la gestion des rôles (admin/employe)
"""
from typing import Optional


def normalize_role(role: Optional[str]) -> str:
    """
    Normalise les variantes de rôle vers: super_admin | admin | employe.
    """
    value = str(role or "").strip().lower()
    aliases = {
        "super_admin": "super_admin",
        "super-admin": "super_admin",
        "superadmin": "super_admin",
        "admin": "admin",
        "administrator": "admin",
        "employe": "employe",
        "employee": "employe",
        "user": "employe",
    }
    return aliases.get(value, value or "employe")


def est_admin(couturier_data: Optional[dict]) -> bool:
    """
    Vérifie si l'utilisateur connecté est un administrateur
    
    Args:
        couturier_data: Données du couturier depuis st.session_state.couturier_data
        
    Returns:
        True si admin, False sinon
    """
    if not couturier_data:
        return False
    
    role = normalize_role(couturier_data.get('role', 'employe'))
    return role == 'admin'


def est_employe(couturier_data: Optional[dict]) -> bool:
    """
    Vérifie si l'utilisateur connecté est un employé
    
    Args:
        couturier_data: Données du couturier depuis st.session_state.couturier_data
        
    Returns:
        True si employé, False sinon
    """
    if not couturier_data:
        return False
    
    role = normalize_role(couturier_data.get('role', 'employe'))
    return role == 'employe'


def obtenir_couturier_id(couturier_data: Optional[dict]) -> Optional[int]:
    """
    Récupère l'ID du couturier connecté
    
    Args:
        couturier_data: Données du couturier depuis st.session_state.couturier_data
        
    Returns:
        ID du couturier ou None
    """
    if not couturier_data:
        return None
    
    return couturier_data.get('id')


def obtenir_salon_id(couturier_data: Optional[dict]) -> Optional[str]:
    """
    Récupère l'ID du salon auquel appartient l'utilisateur connecté (multi-tenant)
    
    Args:
        couturier_data: Données du couturier depuis st.session_state.couturier_data
        
    Returns:
        ID du salon (VARCHAR) ou None
    """
    if not couturier_data:
        return None
    
    salon_id = couturier_data.get('salon_id')
    
    # Si l'admin n'a pas de salon_id, utiliser son propre id comme salon_id
    if not salon_id and normalize_role(couturier_data.get('role')) == 'admin':
        salon_id = couturier_data.get('id')
    
    return salon_id

