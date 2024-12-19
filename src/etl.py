import httpx
import pandas as pd
from datetime import datetime

API_URL = "http://localhost:8000/data"

def extract_data_for_date(date: str):
    """
    Extrai dados da API para um único dia.
    
    Args:
        date (str): Data no formato 'YYYY-MM-DD'.
    
    Returns:
        list: Dados extraídos no formato JSON.
    """
    try:
        start_date = f"{date}T00:00:00+00:00"
        end_date = f"{date}T23:59:59+00:00"
        
        params = {
            "start": start_date,
            "end": end_date,
            "fields": ["timestamp", "wind_speed", "power", "ambient_temperature"]
        }
        response = httpx.get(API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Dados extraídos para {date}: {len(data)} registros encontrados.")
        
        filtered_data = [
            record for record in data
            if datetime.fromisoformat(record['timestamp']).date() == datetime.fromisoformat(start_date).date()
        ]
        print(f"Dados filtrados para {date}: {len(filtered_data)} registros.")
        return filtered_data
    except httpx.RequestError as e:
        print(f"Erro na requisição: {e}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"Erro de status HTTP: {e.response.status_code}")
        return []

def aggregate_data(data: list):
    """
    Agrega os dados em intervalos de 10 minutos.
    
    Args:
        data (list): Dados no formato JSON.
    
    Returns:
        pd.DataFrame: Dados agregados.
    """
    if not data:
        print("Nenhum dado para agregar.")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df.set_index('timestamp', inplace=True)
    
    aggregated_df = df.resample('10T').agg({
        'wind_speed': ['mean', 'min', 'max', 'std'],
        'power': ['mean', 'min', 'max', 'std']
    })
    aggregated_df.reset_index(inplace=True)

    print(f"Dados agregados em intervalos de 10 minutos:\n{aggregated_df}")
    return aggregated_df


if __name__ == "__main__":
    input_date = input("Insira a data (formato YYYY-MM-DD): ")
    try:
        datetime.strptime(input_date, "%Y-%m-%d")
        extracted_data = extract_data_for_date(input_date)
        aggregated_data = aggregate_data(extracted_data)
        print(f"Dados finais:\n{aggregated_data}")
    except ValueError:
        print("Data inválida. Use o formato YYYY-MM-DD.")
