from datetime import datetime

import httpx
import pandas as pd
from sqlalchemy.orm import Session

from src.db_config.alvo.database import (
    Base,
    SessionLocal,
    engine_for_target_db,
)
from src.db_config.alvo.models import Data, Signal

API_URL = "http://localhost:8000/data"

SIGNALS = ["wind_speed", "power", "ambient_temperature"]

Base.metadata.create_all(bind=engine_for_target_db)


def ensure_signals_exist(session: Session) -> None:
    """Garante que os sinais padrão existam na tabela `signal`.

    Args:
        session (Session): Sessão do SQLAlchemy.
    """
    for signal_name in SIGNALS:
        signal = (
            session.query(Signal).filter(Signal.name == signal_name).first()
        )
        if not signal:
            new_signal = Signal(name=signal_name)
            session.add(new_signal)
    session.commit()
    print("Sinais garantidos na tabela 'signal'.")


def save_aggregated_data(
    session: Session, aggregated_df: pd.DataFrame
) -> None:
    """Salva os dados agregados na tabela `data`.

    Args:
        session (Session): Sessão do SQLAlchemy.
        aggregated_df (pd.DataFrame): Dados agregados.
    """
    for _, row in aggregated_df.iterrows():
        for signal_name in SIGNALS:
            # Obter o sinal correspondente
            signal = (
                session.query(Signal)
                .filter(Signal.name == signal_name)
                .first()
            )
            if not signal:
                raise Exception(f"Sinal {signal_name} não encontrado.")

            # Criar uma entrada para cada agregação (mean, min, max, std)
            data_entry = Data(
                timestamp=row["timestamp"],
                signal_id=signal.id,
                mean=row[f"{signal_name}_mean"],
                min=row[f"{signal_name}_min"],
                max=row[f"{signal_name}_max"],
                std=row[f"{signal_name}_std"],
            )
            session.add(data_entry)
    session.commit()
    print("Dados agregados salvos na tabela 'data'.")


def extract_data_for_date(date: str) -> pd.DataFrame:
    """Extrai dados da API para um único dia.

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
            "fields": [
                "timestamp",
                "wind_speed",
                "power",
                "ambient_temperature",
            ],
        }
        response = httpx.get(API_URL, params=params)
        response.raise_for_status()

        data = response.json()

        filtered_data = [
            record
            for record in data
            if datetime.fromisoformat(record["timestamp"]).date()
            == datetime.fromisoformat(start_date).date()
        ]
        print(f"Dados filtrados para {date}: {len(filtered_data)} registros.")
    except httpx.RequestError as e:
        print(f"Erro na requisição: {e}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"Erro de status HTTP: {e.response.status_code}")
        return []
    else:
        return filtered_data


def aggregate_data(data: list) -> pd.DataFrame:
    """Agrega os dados em intervalos de 10 minutos.

    Args:
        data (list): Dados no formato JSON.

    Returns:
        pd.DataFrame: Dados agregados.
    """
    if not data:
        print("Nenhum dado para agregar.")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.set_index("timestamp")

    aggregated_data = {}

    for signal in SIGNALS:
        aggregated_data[f"{signal}_mean"] = df[signal].resample("10min").mean()
        aggregated_data[f"{signal}_min"] = df[signal].resample("10min").min()
        aggregated_data[f"{signal}_max"] = df[signal].resample("10min").max()
        aggregated_data[f"{signal}_std"] = df[signal].resample("10min").std()

    aggregated_df = pd.DataFrame(aggregated_data)

    # Resetando o índice para que o timestamp seja uma coluna normal
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
        print("\033[30;42mTodos os dados salvos com sucesso! ;)\033[m")
