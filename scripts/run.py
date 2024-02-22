import subprocess
from multiprocessing import Process

miner_coldkey = 'miner'
validator_coldkey = 'validator'
netuid = 78
network = 'test'

miners = [
    # Mock (static)
    {'hotkey':'default', 'port':9001, 'file':'neurons/miners/test/mock.py', 'type':'mock'},
    {'hotkey':'default', 'port':9002, 'file':'neurons/miners/test/mock.py', 'type':'mock'},
    # Echo
    {'hotkey':'default', 'port':9003, 'file':'neurons/miners/test/echo.py', 'type':'echo'},
    {'hotkey':'default', 'port':9004, 'file':'neurons/miners/test/echo.py', 'type':'echo'},
    {'hotkey':'default', 'port':9005, 'file':'neurons/miners/test/echo.py', 'type':'echo'},
    # Phrase
    {'hotkey':'default', 'port':9006, 'file':'neurons/miners/test/phrase.py', 'type':'phrase',   'config': '--neuron.phrase "That is an excellent question"'},
    {'hotkey':'default', 'port':9007, 'file':'neurons/miners/test/phrase.py', 'type':'phrase',   'config': '--neuron.phrase "Could you repeat that?"'},
    {'hotkey':'default', 'port':9008, 'file':'neurons/miners/test/phrase.py', 'type':'phrase',   'config': '--neuron.phrase "And so it goes..."'},
    {'hotkey':'default', 'port':9009,
     'file':'neurons/miners/test/phrase.py', 'type':'phrase',   'config': '--neuron.phrase "You and me baby ain\'t nothing but mammals"'},
    {'hotkey':'default', 'port':9010 , 'file':'neurons/miners/test/phrase.py', 'type':'phrase', 'config': '--neuron.phrase "I\'m sorry Dave, I\'m afraid I can\'t do that"'},
]

validators = [
    {'hotkey':'default', 'port':9000 , 'file':'neurons/validator.py', 'type':'real', 'config': '--neuron.log_full --neuron.sample_size 5 --neuron.device cuda'},        
    {'hotkey':'default', 'port':9011 , 'file':'neurons/validator.py', 'type':'mock', 'config': '--neuron.log_full --neuron.sample_size 5 --neuron.model_id mock'},
]

def start_neuron(neuron, coldkey):
    command = f"pm2 start {neuron['file']} --interpreter python3 --name {neuron['hotkey']}:{neuron['type']} --"\
            +f" --wallet.name {coldkey} --wallet.hotkey {neuron['hotkey']} --subtensor.network {network} --netuid {netuid}"\
            +f" --axon.port {neuron['port']} --logging.debug {neuron.get('config')}"
    print(command)
    subprocess.run(command, shell=True)

miners_process = []
validators_process = []

for neuron in miners:
    p = Process(target=start_neuron, args=(neuron, miner_coldkey))
    p.start()
    miners_process.append(p)

for neuron in validators:
    p = Process(target=start_neuron, args=(neuron, validator_coldkey))
    p.start()
    validators_process.append(p)

# Wait for all processes to finish
for p in miners_process:
    p.join()

for p in validators_process:
    p.join()
