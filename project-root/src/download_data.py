import requests
from pathlib import Path

def download_csv(
    url="https://www.datosabiertos.gob.pe/sites/default/files/DATASET_Denuncias_Policiales_Enero%202018%20a%20Octubre%202025.csv",
    output_filename="DATASET_Denuncias_Policiales_Enero_2018_a_Octubre_2025.csv"
):
    # Ruta a la carpeta data
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    output_file = data_dir / output_filename

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    print(f"Descargando CSV desde: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    with open(output_file, "wb") as f:
        f.write(response.content)

    print(f"✓ Descarga completada: {output_file}")
    print(f"✓ Tamaño: {len(response.content) / (1024*1024):.2f} MB")
    return output_file

if __name__ == "__main__":
    download_csv()