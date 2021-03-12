from confluent_kafka import Consumer


c = Consumer({'bootstrap.servers': 'localhost', 'group.id': 'mygroup'})

c.subscribe(['cryptocompare'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))

c.close()
