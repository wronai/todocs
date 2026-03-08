#!/usr/bin/env bash
clear
pip install glon --upgrade
pip install goal --upgrade
pip install code2llm --upgrade
pip install code2docs --upgrade
code2docs ./todocs --output ../docs/
#code2llm ./ -f toon,evolution,code2logic,project-yaml -o ./project --no-chunk
code2llm ./ -f all -o ./project --no-chunk
#code2llm report --format all       # → all views
rm project/analysis.json
rm project/analysis.yaml


#code2docs ./code2docs --readme-only     # Tylko README
#code2docs ./code2docs --dry-run         # Podgląd bez zapisu
#code2docs sync ./code2docs              # Tylko zmienione pliki
#code2docs check ./code2docs             # Sprawdź kompletność docs