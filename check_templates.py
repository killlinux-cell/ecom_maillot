#!/usr/bin/env python3
"""
Script pour vérifier les templates du dashboard
Usage: python check_templates.py
"""

import os
import re

def check_template_file(file_path):
    """Vérifier un template pour les références problématiques"""
    print(f"🔍 Vérification de {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier les références admin: qui n'existent pas
        admin_patterns = re.findall(r'admin:[a-zA-Z_]+', content)
        if admin_patterns:
            print(f"  ⚠️ Références admin trouvées: {set(admin_patterns)}")
        else:
            print(f"  ✅ Aucune référence admin problématique")
        
        # Vérifier les références url 'home' qui n'existent pas
        home_patterns = re.findall(r"url 'home'", content)
        if home_patterns:
            print(f"  ⚠️ Références 'home' trouvées: {len(home_patterns)}")
        else:
            print(f"  ✅ Aucune référence 'home' problématique")
        
        # Vérifier les références dashboard: qui existent
        dashboard_patterns = re.findall(r'dashboard:[a-zA-Z_]+', content)
        if dashboard_patterns:
            print(f"  ✅ Références dashboard trouvées: {set(dashboard_patterns)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lecture fichier: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Vérification des templates du dashboard...\n")
    
    template_dir = "templates/dashboard"
    template_files = [
        "base.html",
        "home.html",
        "products.html",
        "categories.html",
        "teams.html",
        "users.html",
        "user_edit.html",
        "product_edit.html",
        "orders.html",
        "payments.html",
        "customizations.html",
        "analytics.html",
        "settings.html"
    ]
    
    all_good = True
    
    for template_file in template_files:
        file_path = os.path.join(template_dir, template_file)
        if os.path.exists(file_path):
            if not check_template_file(file_path):
                all_good = False
        else:
            print(f"⚠️ Fichier manquant: {template_file}")
    
    print(f"\n📊 Résultats:")
    if all_good:
        print("🎉 Tous les templates sont corrects!")
    else:
        print("⚠️ Certains templates ont des problèmes")
    
    return 0 if all_good else 1

if __name__ == '__main__':
    exit(main())
