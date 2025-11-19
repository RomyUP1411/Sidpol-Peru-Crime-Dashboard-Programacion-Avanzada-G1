import requests
from pathlib import Path
import time
import hashlib
import json
from datetime import datetime
import processing
import pandas as pd


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

            # Intentar validar/estandarizar columnas del CSV descargado
            try:
                # Leer con las mismas funciones de processing para garantizar nombres esperados
                try:
                    raw = processing.load_raw(output_file)
                except Exception:
                    raw = pd.read_csv(output_file, encoding="latin1")

                # Columnas esperadas en el raw antes de clean
                expected_raw = {"ANIO", "MES", "DPTO_HECHO_NEW", "PROV_HECHO", "DIST_HECHO", "P_MODALIDADES", "cantidad"}
                cols = set(raw.columns.str.upper())

                if not expected_raw.issubset(cols):
                    # Intentar mapear columnas por palabras clave
                    rename_map = {}
                    for c in raw.columns:
                        cu = c.upper()
                        if "ANIO" in cu or "AÑO" in cu:
                            rename_map[c] = "ANIO"
                        elif "MES" in cu:
                            rename_map[c] = "MES"
                        elif "DEPARTA" in cu or "DPTO" in cu or "DEPARTAMENTO" in cu:
                            rename_map[c] = "DPTO_HECHO_NEW"
                        elif "PROV" in cu:
                            rename_map[c] = "PROV_HECHO"
                        elif "DIST" in cu:
                            rename_map[c] = "DIST_HECHO"
                        elif "MODAL" in cu:
                            rename_map[c] = "P_MODALIDADES"
                        elif "CANT" in cu or "CANTIDAD" in cu:
                            rename_map[c] = "cantidad"

                    if rename_map:
                        raw = raw.rename(columns=rename_map)
                        # Guardar el CSV estandarizado (sobrescribir)
                        raw.to_csv(output_file, index=False, encoding="utf-8")
                        meta["columns_standardized"] = True
                        with open(metadata_file, "w", encoding="utf-8") as mf:
                            json.dump(meta, mf, ensure_ascii=False, indent=2)
            except Exception:
                # No crítico; continuar
                pass

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
