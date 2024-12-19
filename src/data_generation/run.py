import datetime
import random
import json


def generate_random_data(timestamp):
    ambient_temperature = round(random.uniform(-10, 40), 2)  # Temperatura aleatória entre -10 e 40 graus
    power = round(random.uniform(0, 100), 2)  # Potência aleatória entre 0 e 100
    wind_speed = round(random.uniform(0, 20), 2)  # Velocidade do vento aleatória entre 0 e 20 m/s

    return {
        "timestamp": timestamp,
        "ambient_temperature": ambient_temperature,
        "power": power,
        "wind_speed": wind_speed
    }


def generate_time(num_records=10):
    start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=random.randint(0, 1000))
    start_time = start_time.replace(second=0, microsecond=0)
    current_time = start_time - datetime.timedelta(minutes=start_time.minute % 10)

    for _ in range(num_records):
        data = generate_random_data(current_time.isoformat())
        print(f"Data inserted: {json.dumps(data)}") 
        current_time += datetime.timedelta(minutes=1)

generate_time(11)
