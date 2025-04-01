# 🧪 Contribuer à ce projet

Bienvenue ! Ce guide explique comment contribuer proprement au projet, que tu sois développeur principal ou contributeur externe.

---

## 🗂️ Structure des branches

| Branche     | Usage                          |
|-------------|--------------------------------|
| `main`      | Version stable en production   |
| `develop`   | Version en préproduction/UAT   |
| `feature/*` | Fonctions ou corrections en cours de dev |

---

## 🧱 Règles de contribution

### ✅ Branches

- **Ne jamais pousser directement** sur `main` ou `develop`
- Créer une branche à partir de `develop` :

  ```bash
  git checkout develop
  git pull origin develop
  git checkout -b feature/nom-fonctionnalite
Nom de branche recommandé : feature/xxx, bugfix/xxx, refactor/xxx

✅ Commits
Utilise des messages clairs et concis :

makefile
Copier
Modifier
feat: ajout du scraping par catégorie
fix: corrige bug d’authentification Firebase
chore: mise à jour des dépendances
Tu peux suivre la convention Conventional Commits

✅ Pull Requests
Type de PR	Base branch	Effet
Nouvelle fonctionnalité	develop	🚀 CI/CD staging (UAT)
Mise en production	main	✅ Déploiement en production
Règles :
Une PR vers develop déclenche un déploiement UAT

Une PR vers main déclenche un déploiement production

Toutes les PRs doivent être relues et validées

Les tests doivent passer (CI GitHub Actions)

🚀 Releases
Les releases sont créées à partir de main, via un script ou manuellement

Convention de versionnement : SemVer + préversions

Type	Exemple	Usage
Alpha	v0.1.0-alpha.1	Dév instable
Beta	v0.1.0-beta.1	Pré-release pour test
RC	v0.1.0-rc.1	Release candidate
Stable	v0.1.0	Version officielle en prod
Utiliser le script de release :
bash
Copier
Modifier
./release.sh alpha 0.1.0 "Première version instable"
./release.sh beta 0.1.0 "Tests en staging"
./release.sh rc 0.1.0 "Préparation production"
./release.sh prod 0.1.0 "🎉 Mise en production"
Le script crée un tag Git, une release GitHub et génère automatiquement le changelog si non fourni.

🔐 Règles de protection (GitHub)
Branche main :
✅ PR obligatoire

✅ CI/Tests doivent réussir

✅ 1 review minimum

✅ Historique linéaire

🚫 Push direct interdit

🚫 Suppression interdite

Branche develop :
✅ PR obligatoire

✅ CI doit réussir

✅ Historique linéaire

🚫 Push direct déconseillé

🔁 Cycle de vie recommandé
mermaid
Copier
Modifier
graph TD
  A[feature/nouvelle-fonction] --> B(develop)
  B --> C(main)
  C --> D[tag & release]
⚙️ CI/CD
Le projet utilise GitHub Actions :

✅ build-and-test-dev : déclenché à chaque commit sur une feature branch

✅ deploy-uat : déclenché par une PR vers develop

✅ deploy-prod : déclenché par une PR vers main ou un tag/release GitHub

💬 Support
Pour toute question :

Crée une issue GitHub

Ou contacte directement le mainteneur du dépôt