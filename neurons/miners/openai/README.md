# OpenAI Bittensor Miner
This repository contains a Bittensor Miner that uses langchain and OpenAI's model as its synapse. The miner connects to the Bittensor network, registers its wallet, and serves the GPT model to the network.

## Prerequisites

- Python 3.8+
- OpenAI Python API (https://github.com/openai/openai)

## Installation

1. Clone the repository 
```bash
git clone https://github.com/ait-protocol/einstein-ait-prod.git
cd einstein-ait-prod
bash install.sh
pip uninstall uvloop -y
```

For ease of use, you can run the scripts as well with PM2. Installation of PM2 is: On Linux:
```bash
sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update
```

2. Ensure that you have a `.env` file with your `OPENAI_API` key
```.env
echo OPENAI_API_KEY=YOUR-KEY > .env
```

For more configuration options related to the wallet, axon, subtensor, logging, and metagraph, please refer to the Bittensor documentation.

## Example Usage

To run the OpenAI Bittensor Miner with default settings, use the following command:

```bash
python3 neurons/miners/openai/miner.py \
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test> \
--wallet.name <<your-wallet-name>> \
--wallet.hotkey <<your-hotkey>> \
--neuron.model_id <<model_id>>
```

You can easily change some key parameters at the CLI, e.g.:
```bash
python3 neurons/miners/openai/miner.py \
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test> \
--wallet.name <<your-wallet-name>> \
--wallet.hotkey <<your-hotkey>> \
--neuron.model_id gpt-4-1106-preview # default value is gpt3.5 turbo \
--neuron.max_tokens 1024 # default value is 256 \
--neuron.temperature 0.9 # default value is 0.7
```

or use pm2 to run the miner in the background:
```bash
pm2 start neurons/miners/openai/miner.py \
--name "openai_miner" \
--interpreter "python" \
-- --wallet.name <<your-wallet-name>> \
--wallet.hotkey <<your-hotkey>> \
--neuron.model_id <<model_id>> \
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test> \
```
