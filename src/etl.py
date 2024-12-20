import httpx
import pandas as pd
from datetime import datetime
from db_config.alvo.database import Base, engine_for_target_db, SessionLocal
from db_config.alvo.models import Signal, Data

API_URL = "http://localhost:8000/data"

SIGNALS = ["wind_speed", "power", "ambient_temperature"]

Base.metadata.create_all(bind=engine_for_target_db)


def ensure_signals_exist(session):
    """
    Garante que os sinais padrão existam na tabela `signal`.
    
    Args:
        session (Session): Sessão do SQLAlchemy.
    """
    for signal_name in SIGNALS:
        signal = session.query(Signal).filter(Signal.name == signal_name).first()
        if not signal:
            new_signal = Signal(name=signal_name)
            session.add(new_signal)
    session.commit()
    print("Sinais garantidos na tabela 'signal'.")


def save_aggregated_data(session, aggregated_df):
    """
    Salva os dados agregados na tabela `data`.
    
    Args:
        session (Session): Sessão do SQLAlchemy.
        aggregated_df (pd.DataFrame): Dados agregados.
    """
    for signal_name in SIGNALS:
        # Obter o sinal correspondente
        signal = session.query(Signal).filter(Signal.name == signal_name).first()
        if not signal:
            raise Exception(f"Sinal {signal_name} não encontrado.")
        
        # Filtrar as colunas relevantes para o sinal
        for agg_type in ['mean', 'min', 'max', 'std']:
            column_name = f"{signal_name}_{agg_type}"
            if column_name not in aggregated_df.columns:
                raise Exception(f"Coluna {column_name} não encontrada nos dados agregados.")

            # Iterar pelos dados e salvar no banco
            for _, row in aggregated_df.iterrows():
                data_entry = Data(
                    timestamp=row['timestamp'],
                    signal_id=signal.id,
                    value=row[column_name],
                    agg_type=agg_type,
                )
                session.add(data_entry)
    session.commit()
    print("Dados agregados salvos na tabela 'data'.")


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
    
    aggregation_rules = {signal: ["mean", "min", "max", "std"] for signal in SIGNALS}
    aggregated_df = df.resample("10T").agg(aggregation_rules)
    aggregated_df.columns = [
            f"{col[0]}_{col[1]}" for col in aggregated_df.columns
        ]
    aggregated_df.reset_index(inplace=True)

    print(f"Dados agregados em intervalos de 10 minutos:\n{aggregated_df}")
    return aggregated_df


if __name__ == "__main__":
    input_date = input("Insira a data (formato YYYY-MM-DD): ")
    try:
        datetime.strptime(input_date, "%Y-%m-%d")
        extracted_data = extract_data_for_date(input_date)
        aggregated_data = aggregate_data(extracted_data)
        with SessionLocal() as session:
            ensure_signals_exist(session)
            save_aggregated_data(session, aggregated_data)
    except ValueError:
        print("Data inválida. Use o formato YYYY-MM-DD.")
    finally:
        print('\033[30;42mTodos os dados salvos com sucesso! ;)\033[m')
