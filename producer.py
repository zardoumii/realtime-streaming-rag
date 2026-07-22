import json
import requests
import time
from sseclient import SSEClient
from confluent_kafka import Producer

# Connect to our local Redpanda broker
producer = Producer({'bootstrap.servers': 'redpanda:29092'})

def delivery_report(err, msg):
    if err is not None:
        pass # Silently ignore delivery errors for now to keep terminal clean
    else:
        data = json.loads(msg.value().decode('utf-8'))
        print(f"Pushed to stream: {data['title']}")

print("Connecting to Wikipedia... Press Ctrl+C to stop.")

url = 'https://stream.wikimedia.org/v2/stream/recentchange'

# The nametag so Wikipedia doesn't block us
headers = {
    'User-Agent': 'RealTimeRAG-Project/1.0 (learning-data-engineering) python-requests'
}

# Wrap in a loop so it reconnects if the internet blips
while True:
    try:
        response = requests.get(url, stream=True, headers=headers, timeout=60)
        client = SSEClient(response)

        for event in client.events():
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                    
                    if change.get('server_name') == 'en.wikipedia.org':
                        data = {
                            'title': change.get('title'),
                            'user': change.get('user'),
                            'url': change.get('meta', {}).get('uri'),
                            'timestamp': change.get('meta', {}).get('dt'),
                            'comment': change.get('comment', '') 
                        }
                        
                        producer.produce(
                            topic='wiki-changes', 
                            value=json.dumps(data).encode('utf-8'),
                            callback=delivery_report
                        )
                        producer.poll(0)
                        
                except ValueError:
                    continue
                    
    except Exception as e:
        print(f"Connection lost ({e}). Reconnecting in 3 seconds...")
        time.sleep(3)