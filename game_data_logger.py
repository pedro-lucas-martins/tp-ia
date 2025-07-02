import matplotlib.pyplot as plt

class GameDataLogger:
    def save_csv(self, filename="game_stats.csv"):
        import csv
        if not self.stats_history:
            print("Nenhum dado para salvar.")
            return
        keys = list(self.stats_history[0].keys())
        with open(filename, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.stats_history)
        print(f"Dados salvos em {filename}")
    def __init__(self):
        self.stats_history = []

    def log(self, stats, game_time):
        # stats: dict com métricas do jogo
        entry = stats.copy()
        entry['time'] = game_time
        self.stats_history.append(entry)

    def plot_results(self):
        if not self.stats_history:
            print("Nenhum dado para plotar.")
            return
        times = [s['time'] for s in self.stats_history]
        eliminated = [s['eliminated_attackers'] for s in self.stats_history]
        successful = [s['successful_attackers'] for s in self.stats_history]
        score = [s['score'] for s in self.stats_history]
        towers = [s['towers'] for s in self.stats_history]
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 2, 1)
        plt.plot(times, eliminated, label="Eliminados")
        plt.plot(times, successful, label="Bem-sucedidos")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Atacantes")
        plt.legend()
        plt.title("Atacantes Eliminados vs Bem-sucedidos")
        plt.subplot(2, 2, 2)
        plt.plot(times, score, color='purple')
        plt.xlabel("Tempo (s)")
        plt.ylabel("Pontuação")
        plt.title("Pontuação ao Longo do Tempo")
        plt.subplot(2, 2, 3)
        plt.plot(times, towers, color='orange')
        plt.xlabel("Tempo (s)")
        plt.ylabel("Torres")
        plt.title("Torres Colocadas")
        plt.tight_layout()
        plt.show()
