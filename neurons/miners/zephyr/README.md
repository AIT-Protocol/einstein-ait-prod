# Zephyr Bittensor Miner
This repository contains a Bittensor Miner that uses [HuggingFaceH4/zephyr-7b-beta](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta). The miner connects to the Bittensor network, registers its wallet, and serves the zephyr model to the network.

## Prerequisites

- Python 3.9+
- CUDA 12.0+
- GPU with at least 20GB of VRAM

## Installation
1. Clone the repository 
```bash
git clone https://github.com/ait-protocol/einstein-ait-prod.git
```
2. Install the required packages for the [repository requirements](../../../requirements.txt) with `pip install -r requirements.txt`
3. Install the required packages for the [zephyr miner](requirements.txt) with `pip install -r requirements.txt`


For more configuration options related to the wallet, axon, subtensor, logging, and metagraph, please refer to the Bittensor documentation.

## Example Usage

To run the Zephyr Bittensor Miner with default settings, use the following command:
```bash
pm2 start neurons/miners/zephyr/miner.py \
--name "s3_zephyr" \
--interpreter "python" \
-- --netuid <netuid> \
--subtensor.network <network> \
--wallet.name <wallet_name> \
--wallet.hotkey <wallet_hotkey> \
--neuron.model_id HuggingFaceH4/zephyr-7b-beta
```

To run the zephyr Bittensor Miner with custom settings, use the following command:
```bash
pm2 start neurons/miners/zephyr/miner.py \
--name "s3_zephyr" \
--interpreter "python" \
-- --netuid <netuid> \
--subtensor.network <network> \
--wallet.name <wallet_name> \
--wallet.hotkey <wallet_hotkey> \
--axon.port <port> \
--axon.external_port <port> \
--logging.debug True \
--neuron.model_id HuggingFaceH4/zephyr-7b-beta \
--neuron.max_tokens 1024 \
--neuron.do_sample True \
--neuron.temperature 0.9 \
--neuron.top_k 50 \
--neuron.top_p 0.95 \
--wandb.on True \
--wandb.entity {your entity} \
--wandb.project_name {your project name} \
```

You will need 20GB of GPU to run this miner in comfortable settings.

You can also run the quantized version of this model that takes ~10GB of GPU RAM by adding the flag `--neuron.load_quantized`:
```bash
pm2 start neurons/miners/zephyr/miner.py \
--name "s3_zephyr" \
--interpreter "python" \
-- --netuid <netuid> \
--subtensor.network <network> \
--wallet.name <wallet_name> \
--wallet.hotkey <wallet_hotkey> \
--neuron.model_id HuggingFaceH4/zephyr-7b-beta \
--neuron.load_quantized True
```