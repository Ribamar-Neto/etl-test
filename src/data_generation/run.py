import datetime
import random
import httpx
import asyncio

API_URL = "http://localhost:8000/all"


def generate_random_data(num_days=10):
    start_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = start_time.replace(second=0, microsecond=0, minute=0)
    current_time = start_time

    records = []
    for _ in range(num_days * 24 * 60):
        record = {
            'timestamp': current_time.isoformat(),
            'ambient_temperature': round(random.uniform(15.0, 35.0), 2),
            'power': round(random.uniform(50.0, 100.0), 2),
            'wind_speed': round(random.uniform(0.0, 20.0), 2)
        }
        records.append(record)
        current_time += datetime.timedelta(minutes=1)
    start_date = records[0]['timestamp']
    end_date = records[-1]['timestamp']
    print(f"Data inicial: {start_date}")
    print(f"Data final: {end_date}")
    return records


async def send_data_to_api(records):
    async with httpx.AsyncClient() as client:
        for record in records:
            response = await client.post(API_URL, json=record)

            if response.status_code != 201:
                print(f"Failed to insert data: {response.status_code}, {response.text}")


async def generate_and_send_data(num_days=10):
    records = generate_random_data(num_days)
    await send_data_to_api(records)


asyncio.run(generate_and_send_data(10))