import requests
from pathlib import Path
import time
import hashlib
import json
from datetime import datetime


def download_csv(
    url: str = "https://www.datosabiertos.gob.pe/sites/default/files/DATASET_Denuncias_Policiales_Enero%202018%20a%20Octubre%202025.csv",
    output_filename: str = "DATASET_Denuncias_Policiales_Enero_2018_a_Octubre_2025.csv",
    max_retries: int = 3,
    backoff_factor: float = 1.0,
):
    """Descarga el CSV y guarda un archivo metadata.json con metadatos (sha256, size, fecha).

    Usa reintentos simples con backoff exponencial.
    """
    # Ruta a la carpeta data
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    output_file = data_dir / output_filename
    metadata_file = data_dir / "metadata.json"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Descargando CSV desde: {url} (intento {attempt})")
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()

            content = resp.content
            with open(output_file, "wb") as f:
                f.write(content)

            # Calcular hash y crear metadata
            sha256 = hashlib.sha256(content).hexdigest()
            size = len(content)
            meta = {
                "filename": output_file.name,
                "url": url,
                "downloaded_at": datetime.utcnow().isoformat() + "Z",
                "sha256": sha256,
                "size_bytes": size,
            }
            with open(metadata_file, "w", encoding="utf-8") as mf:
                json.dump(meta, mf, ensure_ascii=False, indent=2)

            print(f"✓ Descarga completada: {output_file}")
            print(f"✓ Tamaño: {size / (1024*1024):.2f} MB")
            return output_file

        except Exception as e:
            last_exc = e
            wait = backoff_factor * (2 ** (attempt - 1))
            print(f"Error descarga (intento {attempt}): {e}. Reintentando en {wait}s...")
            time.sleep(wait)

    # Si llegamos aquí, todos los intentos fallaron
    raise last_exc


if __name__ == "__main__":
    download_csv()