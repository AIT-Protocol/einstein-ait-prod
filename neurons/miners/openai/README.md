# OpenAI Bittensor Miner

This repository contains a Bittensor Miner that uses langchain and OpenAI's model as its synapse. The miner connects to the Bittensor network, registers its wallet, and serves the GPT model to the network.

## Prerequisites

- Python 3.8+
- [OpenAI Python API](https://github.com/openai/openai)

## Installation

1. Clone the repository

```bash
git clone https://github.com/ait-protocol/einstein-ait-prod.git & cd einstein-ait-prod
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

We recommend using pm2 to run the miner as it will automatically restart the miner if it crashes.

```bash
pm2 start neurons/miners/openai/miner.py --name s5_openai_miner \
--interpreter python \
-- --netuid <78 / 5> \ #78 is our testnet and 5 is our mainnet
--subtensor.network <test/finney> \
--wallet.name <your miner wallet> \
--wallet.hotkey <your miner hotkey> \
--logging.debug \
# WHAT BELOW IS OPTIONAL, PLEASE READ THE DESCRIPTIONS BELOW
--neuron.model_id gpt-3.5-turbo-0125 \
--neuron.max_tokens 1024 \
--neuron.temperature 0.9 \
--neuron.top_p 0.9 \
--neurom.top_k 50 \
--neuron.system_prompt "your prompt engineering"
--numpal.verbose.off \ # Set this if you want to disable verbose mode for NumPAL
--numpal.off \ # Set this if you want to disable NumPAL (Not recommended)

```

   *NOTE: Your wallet and wallet's hotkey must be created using the bittensor-cli and registered to the netuid 78 (our testnet uid). Additionally, you can run the validator in trace mode by using `--logging.trace` instead of `--logging.debug`*

   *- The `--numpal.off` flag is used to disable NumPAL. NumPAL is a feature that allows the miner to solve mathematical problems using the NumPAL supercharger model. Set this flag if you want to disable NumPAL.*

   *- The `--numpal.verbose.off` flag is used to disable logging mode for NumPAL. Set this flag if you want to disable logging mode for NumPAL.*

   *- The `--neuron.model_id` flag is used to specify the model you want to use. The default value is `gpt3.5-turbo` which is the latest model from OpenAI, you can find out more about the models [here](https://platform.openai.com/docs/models/)*

   *- The `--neuron.max_tokens` flag is used to specify the maximum number of tokens the model can generate which is the length of the response. The default value is `256`*

   *- The `--neuron.temperature` flag is used to specify the temperature of the model which controls the creativeness of the model. The default value is `0.7`*

   *- The `--neuron.top_p` This is like choosing ideas that together make a good story, instead of just picking the absolute best ones. It helps the text be both interesting and sensible. The default value is `0.95`*

   *- The `--neuron.top_k` It's like having a lot of ideas but only picking the few best ones to talk about. This makes the text make more sense.  Reducing the number ensures that the model's choices are among the most probable, leading to more coherent text. The default value is `50`*

   *- The `--neuron.system_prompt` flag is used to specify the prompt for the model. The default value is `"YYou are an AI that excels in solving mathematical problems. Always provide responses concisely and provide helpful explanations through step-by-step solutions. You are honest about things you don't know."`*

   Some useful pm2 commands:

   ```bash
   pm2 status # This will show you the status of all pm2 processes
   pm2 logs s5_openai_miner # This will show you the logs of the miner
   pm2 stop {process_id} # This will stop the process
   ```
