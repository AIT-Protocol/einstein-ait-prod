# OpenAI Bittensor Miner

This repository contains a Bittensor Miner that uses langchain and OpenAI's model as its synapse. The miner connects to the Bittensor network, registers its wallet, and serves the GPT model to the network.

## Prerequisites

- Python 3.8+
- [OpenAI Python API](https://github.com/openai/openai)

## Installation

1. Clone the repository

```bash
git clone https://github.com/LVH-Tony/einstein-ait.git & cd einstein-ait
```

2. Install the required packages

```bash
pip install -r requirements.txt
```

3. Install the required packages for the openai miner

```bash
cd neurons/miners/openai && pip install -r requirements.txt
```

4. Ensure that you have a `.env` file with your `OPENAI_API_KEY` key

```bash
echo OPENAI_API_KEY=your-openai-api-key > .env
```

For more configuration options related to the wallet, axon, subtensor, logging, and metagraph, please refer to the Bittensor documentation.

## Example Usage

To run the OpenAI Bittensor Miner with default settings, use the following command:

```bash
python3 neurons/miners/openai/miner.py \
    --wallet.name <<your-wallet-name>> \
    --wallet.hotkey <<your-hotkey>>     
```

You can easily change some key parameters at the CLI, e.g.:
```bash
python3 neurons/miners/openai/miner.py \
    --wallet.name <<your-wallet-name>> \
    --wallet.hotkey <<your-hotkey>> 
    --neuron.model_id gpt-4-1106-preview #
    --neuron.max_tokens 1024
    --neuron.temperature 0.9
```

*NOTE: Your wallet and wallet's hotkey must be created using the bittensor-cli and registered to the netuid 78 (our testnet uid). Additionally, you can run the validator in trace mode by using `--logging.trace` instead of `--logging.debug`*

*- The `--neuron.model_id` flag is used to specify the model you want to use. The default value is `gpt3.5-turbo`*

*- The `--neuron.max_tokens` flag is used to specify the maximum number of tokens the model can generate. The default value is `256`*

*- The `--neuron.temperature` flag is used to specify the temperature of the model. The default value is `0.7`*
