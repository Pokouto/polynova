# Script de configuration pour Render - Windows
Write-Host "🚀 Configuration pour le déploiement sur Render..." -ForegroundColor Green

# 1. Créer Procfile
Write-Host "📄 Création de Procfile..." -ForegroundColor Cyan
"web: gunicorn config.wsgi" | Out-File -FilePath "Procfile" -Encoding UTF8
Write-Host "✅ Procfile créé" -ForegroundColor Green

# 2. Créer runtime.txt
Write-Host "📄 Création de runtime.txt..." -ForegroundColor Cyan
"python-3.11.0" | Out-File -FilePath "runtime.txt" -Encoding UTF8
Write-Host "✅ runtime.txt créé" -ForegroundColor Green

# 3. Créer .gitignore
Write-Host "📄 Création de .gitignore..." -ForegroundColor Cyan
@"
# Django
*.log
*.pot
*.pyc
__pycache__/
db.sqlite3
media/
staticfiles/

# Environnements
.env
venv/
env/

# IDE
.vscode/
.idea/

# Système
.DS_Store
Thumbs.db
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "✅ .gitignore créé" -ForegroundColor Green

# 4. Installer les packages
Write-Host "📦 Installation des packages..." -ForegroundColor Cyan
pip install gunicorn whitenoise dj-database-url

# 5. Mettre à jour requirements.txt
Write-Host "📄 Mise à jour de requirements.txt..." -ForegroundColor Cyan
@"
# Packages pour Render
gunicorn==21.2.0
whitenoise==6.8.0
dj-database-url==2.1.0
"@ | Add-Content -Path "requirements.txt"

Write-Host ""
Write-Host "🎉 Configuration terminée !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes :" -ForegroundColor Yellow
Write-Host "1. Exécuter: python manage.py collectstatic"
Write-Host "2. Commit: git add . && git commit -m 'Prêt pour Render'"
Write-Host "3. Push: git push origin main"
Write-Host "4. Déployer sur: https://render.com"
