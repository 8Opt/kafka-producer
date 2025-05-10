import time
import httpx

from kafka import KafkaProducer


TOPIC = "TEST_KAFKA"
BOOTSTRAP_SERVERS = '0.0.0.0:9092'
SAMPLES_URL = "https://catfact.ninja/fact"

producer = KafkaProducer(bootstrap_servers=[BOOTSTRAP_SERVERS])

while True:

    cat_rsp = httpx.get(SAMPLES_URL)
    if cat_rsp.status_code != 200: 
        print(f"Fetch data from {SAMPLES_URL} failed!!!")
        
    value = cat_rsp.json()  # ex: {"fact":"A female cat can be referred to as a molly or a queen, and a male cat is often labeled as a tom.","length":96}
    msg = value.get("fact")
    print(f"[Producer] Kafka send: {msg}")
    value = bytes(value.get("fact"), encoding="utf-8")
    producer.send(topic=TOPIC, 
                  value=value)
    

    time.sleep(10)