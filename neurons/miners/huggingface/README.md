 # Hugging Face Bittensor Miner
This repository contains a Bittensor Miner integrated with 🤗 Hugging Face pipelines. The miner connects to the Bittensor network, registers its wallet, and serves a hugging face model to the network.

## Prerequisites

- Python 3.8+
- OpenAI Python API (https://github.com/openai/openai)

## Installation
Clone the repository 
```bash
git clone https://github.com/ait-protocol/einstein-ait-prod.git
cd prompting
bash install.sh
pip uninstall uvloop -y
```

For ease of use, you can run the scripts as well with PM2. Installation of PM2 is: On Linux:
```bash
sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update
```


For more configuration options related to the wallet, axon, subtensor, logging, and metagraph, please refer to the Bittensor documentation.

## Example Usage

Here are some model examples that could be leveraged by the HuggingFace Miner, alongside suggested GPU footprint to run the models comfortably:
| model_id | Default GPU footprint | 8bits quantization GPU footprint | 4bits quantization GPU footprint |
| --- | ---- | ---- | ---- |  
| HuggingFaceH4/zephyr-7b-beta | 18 GB | 12 GB | 7 GB |
| teknium/OpenHermes-2.5-Mistral-7B | 30 GB | 10 GB | 7 GB |
| upstage/SOLAR-10.7B-Instruct-v1.0 | 42 GB | 14 GB| 8 GB |
| mistralai/Mixtral-8x7B-Instruct-v0.1 | 92 GB* | 64 GB* | 30 GB* |

> \* Big models such as mixtral are very costly to run and optimize, so always bear in mind the trade-offs between model speed, model quality and infra cost.


To run the Hugging Face Bittensor Miner with default settings, use the following command:
```bash
python3 neurons/miners/huggingface/miner.py \
--wallet.name <<your-wallet-name>> \
--wallet.hotkey <<your-hotkey>> \
--neuron.model_id <<model_id>> \
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test>
```

or use pm2 to run the miner in the background:
```bash
pm2 start neurons/miners/huggingface/miner.py \
--name "huggingface_miner" \
--interpreter "python" \
-- --wallet.name <<your-wallet-name>> \
--wallet.hotkey <<your-hotkey>> \
--neuron.model_id <<model_id>> \
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test>
```

You can also run automatic quantization by adding the flag `--neuron.load_in_8bit` for 8bits quantization and `--neuron.load_in_4bit` for 4 bits quantization:
```bash
python3 neurons/miners/huggingface/miner.py \
--wallet.name <<your-wallet-name>> \
--wallet.hotkey <<your-hotkey>> \
--neuron.model_id <<model_id>> \
--neuron.load_in_8bit True \
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test>
```

or use pm2 to run the miner in the background:
```bash
pm2 start neurons/miners/huggingface/miner.py \
--name "huggingface_miner" \
--interpreter "python" \
-- --wallet.name <<your-wallet-name>> \
--wallet.hotkey <<your-hotkey>> \
--neuron.model_id <<model_id>> \
--neuron.load_in_8bit True \
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test>
```