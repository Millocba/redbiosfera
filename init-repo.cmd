@echo off
REM Inicializa el repositorio Git de este proyecto.
REM Hace falta ejecutarlo una sola vez: doble clic o "init-repo.cmd" en la consola.
chcp 65001 > nul
cd /d "%~dp0"

where git >nul 2>&1 || (echo No se encontro git en el PATH. Instalalo desde https://git-scm.com/download/win & pause & exit /b 1)

if exist ".git" (echo El repositorio ya estaba inicializado. & git log --oneline -n 5 & pause & exit /b 0)

git init -b main
git add -A
git commit -m "Sitio Red Biosfera Urbana a partir del mockup v4" -m "Convierte el diseno base standalone en un sitio estatico desplegable en hosting compartido de Hostinger (Apache + PHP, sin build en el servidor): 6 paginas HTML mas 404, sistema de diseno Organic extraido a CSS con fuentes locales, formularios funcionales contra enviar.php, .htaccess con HTTPS y URLs limpias, build.py para regenerar public/, README y DEPLOY."

echo.
echo Repositorio creado.
git log --oneline
echo.
echo Para publicarlo en GitHub:
echo    git remote add origin https://github.com/USUARIO/red-biosfera-urbana.git
echo    git push -u origin main
echo.
pause
