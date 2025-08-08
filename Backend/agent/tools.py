import numpy as np
from langchain_core.tools import tool
from scipy import stats
from utils.data_format import beauty_output


class Tools:
    @staticmethod
    @tool
    def get_data():
        """Gunakan ini jika kamu ingin mengambil data dari user"""
        try:
            data = beauty_output("../data/pengeluaran.csv")
        except Exception as e:
            print(f"Terjadi kesalahan ketika agent memakai tool: {e}")
            return "Terjadi kesalahan saat mengambil data."
        return data

    @staticmethod
    @tool
    def analize_data(data: list[int]):
        """
        Gunakan ini jika kamu ingin menganalisis data user.
        params:
            - data -> kumpulan data numeric.
        """
        data = np.array(data)
        mean = np.mean(data).item()
        median = np.median(data).item()
        nilai_unik, hitungan = np.unique(data, return_counts=True)
        indeks_modus = np.argmax(hitungan)
        modus = nilai_unik[indeks_modus]
        std = np.std(data).item()
        varian = np.var(data).item()
        max = np.max(data).item()
        min = np.min(data).item()

        statistic, p_value = stats.shapiro(data)
        hasil = ""
        alpha = 0.05
        if p_value > alpha:
            hasil = "Data terdistribusi normal (Gagal menolak H0)."
        else:
            hasil = "Data tidak terdistribusi normal (Menolak H0)."
        return {
            "mean": mean,
            "median": median,
            "modus": modus.item(),
            "standar deviasi": std,
            "varian": varian,
            "max": max,
            "min": min,
            "jangkauan": max - min,
            "distribusi_data": hasil,
        }


if __name__ == "__main__":
    tool = Tools()
    print(tool.analize_data([10, 10, 10, 10, 20, 30, 20, 40, 40, 70]))
