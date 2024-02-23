
<div align="center">
  <h1>Einstein - AIT</h1>

## **Subnet 5**

---

### The Incentivized Internet <!-- omit in toc -->

[Bittensor Discord](https://discord.gg/bittensor) • [AIT Discord](https://discord.gg/aitprotocols) • [AIT Telegram](AIT_Protocol) • [AIT Website](https://ait.tech)

</div>

---

This repository is the **official codebase for the Einstein - AIT subnet**. It contains the code for the validators and miners that are used to validate and mine on the subnet.

# Introduction

Our primary narrative as a mathematics, logic, and data analysis AI subnet is to optimize response accuracy. We achieve this by enabling the language model to autonomously write, test, and execute code within unique Python environments. This approach ensures that our responses are not only precise but also practical, effectively addressing everyday challenges faced by users. Furthermore, our deployment offers significant advantages to the Bittensor ecosystem. By providing a model capable of independent code writing and execution, we bolster the capabilities of other subnets, thereby enhancing their accuracy and improving the quality of responses network-wide. Therefore, our contributions extend beyond direct user support to elevating the overall functionality of the Bittensor ecosystem.

## Mission

At Einstein-AIT, our mission is to enhance the Bittensor ecosystem by providing a robust and reliable subnet dedicated to the computation of complex mathematical operations and logical reasoning. We strive to empower startups and enterprises by offering seamless access to our advanced computational resources through user-friendly APIs, tailored for real-world applications.

Our mission extends to creating symbiotic relationships with other subnets, fostering a culture of mutual growth and knowledge exchange, thereby adding capabilities to the broader network of models and applications.

## Vision

We are dedicated to aligning with Bittensor's core values of permissionless participation and the decentralization of services. Our vision is to cultivate a subnet that embodies these principles, fostering an environment where innovation thrives on the collective strength and diversity of its participants. Together, we are building the foundation for a more open, collaborative, and decentralized world.

# Compute Requirements

**VALIDATOR** REQUIREMENTS

- GPU with 24GB or higher VRAM
- Ubuntu 20.04 or 22.04
- Python 3.9 or 3.10
- CUDA 12.0 or higher

FINE TUNED **MINER** (`WIP`) REQUIREMENTS

- GPU with 18GB or higher VRAM
- Ubuntu 20.04 or 22.04
- Python 3.9 or 3.10
- CUDA 12.0 or higher

**OPENAI MINER** REQUIREMENTS

- Python 3.8, 3.9 or 3.10

# Tools

Currently, the tooling stack includes `mathgenerator`, `OpenAI`, `HuggingFace`, `LangChain`, and `WandB`

Comming soon to public:

- MIT Database
- UCD OneSearch
- Research Paper Database

More tooling will be included in future releases.

# Tasks

The validation process supports an ever-growing number of tasks. Tasks drive agent behaviour based on specific goals, such as;

- Mathematics

Coming soon in future releases:

- Logics and Reasoning
- Data Analysis
- API for other subnets to access to our LLM supercharge extensions

Tasks contain a **query** (basic question/problem) and a **reference** (ideal answer), where a downstream HumanAgent creates a more nuanced version of the **query**.

# Installation

This repository requires python3.9 or higher. To install, simply clone this repository and install the requirements.

```bash
git clone https://github.com/LVH-Tony/einstein-ait.git && cd einstein-ait
```

```bash
python -m pip install -r requirements.txt && python -m pip install -e .
```

---

# Running Validators and Miners

*Disclaimer:*

We encourage miners to use testnet as this gives you a risk-free playground before running on mainnet. If you require test tao, please reach out to <steffen@opentensor.dev>

Prior to running a miner or validator, you must [create a wallet](https://github.com/opentensor/docs/blob/main/reference/btcli.md) and [register the wallet to a netuid](https://github.com/opentensor/docs/blob/main/subnetworks/registration.md). Once you have done so, you can run the miner and validator with the following commands.

## Login to Weight and Biases

   ```bash
   wandb login
   ```
   
---

## Running Validators

1. Install this repository, you can do so by following the steps outlined in [the installation section](#installation).
2. Install [Weights and Biases](https://docs.wandb.ai/quickstart) and run `wandb login` within this repository. This will initialize Weights and Biases, enabling you to view KPIs and Metrics on your validator. (Strongly recommended to help the network improve from data sharing)
3. Install [PM2](https://pm2.io/docs/runtime/guide/installation/) and the [`jq` package](https://jqlang.github.io/jq/) on your system.
   **On Linux**:

   ```bash
   sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update
   ```

   **On Mac OS**

   ```bash
   brew update && brew install jq && brew install npm && sudo npm install pm2 -g && pm2 update
   ```

4. Run the `run.sh` script which will handle running your validator and pulling the latest updates as they are issued.

   ```bash
   pm2 start run.sh --name s1_validator_autoupdate -- --wallet.name <your-wallet-name> --wallet.hotkey <your-wallet-hot-key>
   ```

   The `run.sh` script will automatically pull the latest updates from the repository and restart the validator. This is useful for keeping your validator up to date with the latest changes.

5. **Running the Validator:**

  ```bash
  python neurons/validator.py \
   --netuid < 78 / 5> \ #78 is our testnet and 5 is our mainnet
   --subtensor.network <test/finney> \
  --neuron.device cuda \
  --wallet.name <your validator wallet> \
  --wallet.hotkey <your validator hotkey> \
  --logging.debug
  ```

   *NOTE: Your wallet and wallet's hotkey must be created using the bittensor-cli and registered to the netuid 78 (our testnet uid). Additionally, you can run the validator in trace mode by using `--logging.trace` instead of `--logging.debug`*

---

## Running Miners

### Base Models

   1. AIT Custom API  `Work In Progress - Not yet public`
   2. [OpenAI](https://platform.openai.com/docs/introduction) (GPT variants)

### OpenAI Miner

1. Install the required dependencies by:

   ```bash
   pip install -r neurons/miners/openai/requirements.txt
   ```

2. Include your OpenAI API key into .env and you can do so by:

   ```bash
   echo 'OPENAI_API_KEY=your_api_key_here' >> .env
   ```

3. Start the miner:

   ```bash
   python neurons/miners/openai/miner.py \
   --netuid <78 / 5> \ #78 is our testnet and 5 is our mainnet
   --subtensor.network <test/finney> \
   --wallet.name <your miner wallet> \
   --wallet.hotkey <your miner hotkey> \
   --neuron.model_id gpt-4 \
   --neuron.max_tokens 1024 \
   --neuron.temperature 0.9 \
   --logging.debug
   ```

   *NOTE: Your wallet and wallet's hotkey must be created using the bittensor-cli and registered to the netuid 78 (our testnet uid). Additionally, you can run the validator in trace mode by using `--logging.trace` instead of `--logging.debug`*

   *- The `--neuron.model_id` flag is used to specify the model you want to use. The default value is `gpt3.5-turbo`*

   *- The `--neuron.max_tokens` flag is used to specify the maximum number of tokens the model can generate. The default value is `256`*

   *- The `--neuron.temperature` flag is used to specify the temperature of the model. The default value is `0.7`*

---

# Real-time monitoring with wandb integration

Check out real-time public logging by looking at the project [here](https://wandb.ai/ait-ai/einstein-ait)

---

## License

This repository is licensed under the MIT License.

```text
# The MIT License (MIT)
# Copyright © 2024 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```

---
