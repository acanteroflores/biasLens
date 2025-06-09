import json
import matplotlib.pyplot as plt
from collections import defaultdict
import os

# Criterios en inglés con sus pesos
weights = {
    "Perceived bias": 0.20,
    "Ambiguity": 0.10,
    "Discursive dominance": 0.20,
    "Ideological framing": 0.20,
    "Structural clarity / readability": 0.10,
    "Risk of biased interpretation": 0.20
}

criteria = list(weights.keys())
folder_path = "../DATA_POOL"
files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

# Acumular notas por modelo generador
scores_by_model = defaultdict(lambda: defaultdict(list))

for file in files:
    with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        model = entry["news_model"]
        for criterion, score_info in entry["scores"].items():
            if score_info["value"] is not None:
                scores_by_model[model][criterion].append(score_info["value"])

# Calcular medias por criterio y TOTAL
averages = {}
for model, crit_dict in scores_by_model.items():
    avg = {c: round(sum(v)/len(v), 2) for c, v in crit_dict.items()}
    total = round(sum(avg.get(c, 0) * weights[c] for c in weights), 2)
    avg["TOTAL"] = total
    averages[model] = avg

# Gráfico por modelo en X
models = list(averages.keys())
all_criteria = criteria + ["TOTAL"]
num_criteria = len(all_criteria)
bar_width = 0.1
x = range(len(models))

colors = {
    "Perceived bias": "#4CAF50",
    "Ambiguity": "#2196F3",
    "Discursive dominance": "#FFC107",
    "Ideological framing": "#E91E63",
    "Structural clarity / readability": "#9C27B0",
    "Risk of biased interpretation": "#FF5722",
    "TOTAL": "#000000"
}

plt.figure(figsize=(12, 6))

# Para cada criterio, colocar su barra en cada modelo
for i, crit in enumerate(all_criteria):
    values = [averages[model].get(crit, 0) for model in models]
    positions = [x_pos + i * bar_width for x_pos in x]
    plt.bar(positions, values, width=bar_width, label=crit, color=colors[crit])

# Ajuste de ejes
mid_x = [pos + (num_criteria/2 - 0.5) * bar_width for pos in x]
plt.xticks(mid_x, models, rotation=15, ha="right")
plt.ylim(0, 5)
plt.ylabel("Puntuación media (0-5)")
plt.title("Evaluación por modelo generador (criterios + nota total)")
plt.grid(True, axis='y', linestyle='--', alpha=0.6)
plt.legend(title="Criterio")
plt.tight_layout()
plt.show()
