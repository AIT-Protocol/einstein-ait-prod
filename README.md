 
<div align="center">
  <h1>🧠 SN3: Einstein - AIT 🤖</h1>

## **Testnet uid: 78 \ Mainnet uid: 3🌐**

---

### 🚀 The Incentivized Internet <!-- omit in toc -->


[Discord](https://discord.com/invite/GvEMzStVN6) • [AIT Discord](https://discord.gg/aitprotocols) • [AIT Telegram](AIT_Protocol) • [Subnet Roadmap & Info](https://einstein-ait.notion.site/SN3-Einstein-AIT-Subnet-1f6a76b53b094fd994526443a9937228)

</div>

---

This repository is the **official codebase for the Einstein - AIT subnet**. It contains the code for the validators and miners that are used to validate and mine on the subnet.

# 📚 Introduction

**About Einstein-AIT Subnet:**

Einstein-AIT subnet has a primary focus on developing an AI/ML model that specializes in mathematics, computational thinking and data analysis.  Einstein-AIT subnet has two near term objectives:

1. The launch of **NumPAL** LLM chain supercharger, and
2. The launch of a Hugging Face leaderboard, fine tuning competition for specialized AI/ML models with a focus on complex mathematics. This includes the open sourcing of AIT’s custom AI/ML which can be cloned, iterated and improved upon with custom data sets by mining competitors. 

**Currently**, we have released an LLM chain (supercharger), we call **NumPAL** which can be hooked into any LLM (custom model or API) to accomplish the following: 

1. Improve response accuracy,
2. Minimize the cost of iteration, and
3. Minimize processing time over iterations

We’ve charted the results of a benchmarking session where we took ChatGPT 3.5 supercharged by NumPAL, against ChatGPT 4 Turbo, [See results here](https://www.notion.so/SN3-Einstein-AIT-Subnet-1f6a76b53b094fd994526443a9937228?pvs=21).

**How NumPAL works:** NumPAL is a LLM chain that forces the LLM to ‘think’ before it (’speaks’) spits out a generalized response. NumPAL forces the LLM to write python code, for example by calculating the result of a math problem, and running that code through it’s built-in python executor, finally sending that result back to the LLM to generate a response with a logical explanation to the prompter. 

**NumPAL can be used to supercharge any LLM / miner on the Bittensor network 👀**

## 🎯 Mission

At Einstein-AIT, our mission is to enhance the Bittensor ecosystem by providing a robust and reliable subnet dedicated to the computation of complex mathematical operations and logical reasoning. We strive to empower startups and enterprises by offering seamless access to our advanced computational resources through user-friendly APIs, tailored for real-world applications.

Our mission extends to creating symbiotic relationships with other subnets, fostering a culture of mutual growth and knowledge exchange, thereby adding capabilities to the broader network of models and applications.

## 🔮 Vision

We are dedicated to aligning with Bittensor's core values of permissionless participation and the decentralization of services. Our vision is to cultivate a subnet that embodies these principles, fostering an environment where innovation thrives on the collective strength and diversity of its participants. Together, we are building the foundation for a more open, collaborative, and decentralized world.

# 💻 Compute Requirements

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

- Python 3.9 or 3.10

# 🛠️ Tools

Currently, the tooling stack includes `mathgenerator`, `OpenAI`, `HuggingFace`, `LangChain`, and `WandB`

Comming soon to public:

- MIT Database
- UCD OneSearch
- Research Paper Database

More tooling will be included in future releases.

# 📋 Tasks

The validation process supports an ever-growing number of tasks. Tasks drive agent behaviour based on specific goals, such as;

- Mathematics

Coming soon in future releases:

- Logics and Reasoning
- Data Analysis
- API for other subnets to access to our LLM supercharge extensions

Tasks contain a **query** (basic question/problem) and a **reference** (ideal answer), where a downstream HumanAgent creates a more nuanced version of the **query**.

# 📲 Installation

1. This repository requires python3.9 or higher. To install it, simply clone this repository and run the [install.sh](./scripts/install.sh) script.
   ```bash
   git clone https://github.com/ait-protocol/einstein-ait-prod.git
   cd einstein-ait-prod
   bash scripts/install.sh
   ```

   to update the repository, you can run the [update.sh](./scripts/update.sh) script.
   ```bash
   bash scripts/update.sh
   ```

   Alternatively, if you are running on a clean Ubuntu machine, you can run `scripts/install_ubuntu.sh` to effortlessly install everything you need. If you are wanting to run an OpenAI miner, you will need to place your OpenAI API key in the `OPENAI_API_KEY` variable in the script. 

> Important: vLLM currently faces a [notable limitation](https://github.com/vllm-project/vllm/issues/3012) in designating a specific GPU for model execution via code. Consequently, to employ a particular CUDA device for your model's operations, it's necessary to manually adjust your environment variable `CUDA_VISIBLE_DEVICES`. For instance, setting `export CUDA_VISIBLE_DEVICES=1,2` will explicitly define the CUDA devices available for use.


2. Install [PM2](https://pm2.io/docs/runtime/guide/installation/) and the [`jq` package](https://jqlang.github.io/jq/) on your system.

   **- On Linux**:
  
   ```bash
   sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update
   ```
  
   **- On Mac OS**
  
   ```bash
   brew update && brew install jq && brew install npm && sudo npm install pm2 -g && pm2 update
   ```
---

# 🏃 Running Validators and Miners

*Disclaimer:*

We encourage miners to use testnet as this gives you a risk-free playground before running on mainnet. If you require test tao, please reach out to our [Testnet 78 Discord](https://discord.gg/wVPZrVu9).

For miners and validators running on mainnet, we **strongly recommend** using a [local subtensor](https://github.com/opentensor/subtensor) for improved performance and security.

Prior to running a miner or validator, you must [create a wallet](https://github.com/opentensor/docs/blob/main/reference/btcli.md) and [register the wallet to a netuid](https://github.com/opentensor/docs/blob/main/subnetworks/registration.md). Once you have done so, you can run the miner and validator with the following commands.

## Login to Weight and Biases

   ```bash
   wandb login
   ```

---

## 🧾 Running Validators

1. Install this repository, you can do so by following the steps outlined in [the installation section](#installation) 

2. Install [Weights and Biases](https://docs.wandb.ai/quickstart) and run `wandb login` within this repository. This will initialize Weights and Biases, enabling you to view KPIs and Metrics on your validator. (Strongly recommended to help the network improve from data sharing)
3. Run the `run.sh` script which will handle running your validator and pulling the latest updates as they are issued.

   ```bash
   pm2 start run.sh --name s3_validator_autoupdate -- --wallet.name <your-wallet-name> --wallet.hotkey <your-wallet-hot-key>
   ```

   The `run.sh` script will automatically pull the latest updates from the repository and restart the validator. This is useful for keeping your validator up to date with the latest changes.

   - Some useful pm2 commands:

   ```bash
   pm2 status # This will show you the status of all pm2 processes
   pm2 logs VALIDATOR # This will show you the logs of the validator
   pm2 stop {process_id} # This will stop the process
   ```

4. **OPTIONAL if you are not running by pm2:**

   ```bash
   python neurons/validator.py \
   --netuid 78 or 3 \ # 78 for testnet and 3 for mainnet
   --subtensor.network test or finney \ # test for testnet and finney for mainnet
   --neuron.device cuda \
   --wallet.name <your validator wallet> \
   --wallet.hotkey <your validator hotkey> \
   --logging.debug
   ```

   *NOTE: Your wallet and wallet's hotkey must be created using the bittensor-cli and registered to the netuid 78 (our testnet uid) or 3 (our mainnet uid). Additionally, you can run the validator in trace mode by using `--logging.trace` instead of `--logging.debug`*x

---

## 🏗️ Running Miners

Running Miners is very competitive and requires a lot of resources. We encourage miners to use testnet as this gives you a risk-free playground before running on mainnet. Due to its competitive nature, we encourage miners to do fine-tuning and optimization before running on mainnet. feel free to also develop your own miner too! 

### Base Models

   1. AIT Custom API  `Work In Progress - Not yet public`
   2. [OpenAI](https://platform.openai.com/docs/introduction) (GPT variants)
   3. [Zephyr Model](https://github.com/AIT-Protocol/einstein-ait-prod/blob/main/neurons/miners/zephyr/)

### Alternative Mining Options

If you're a real competitor... try setting up an alternative miner API or your own custom GPU script.

Miners are able to run alternative API's for example, the from Wolfram Alpha API, or others, by going into [neruons/miners/openai/miner.py](https://github.com/AIT-Protocol/einstein-ait-prod/blob/main/neurons/miners/openai/miner.py) and editing the script for your desired model. 

To run your own GPU model you can customize the script in [neurons/miners/zephyr](https://github.com/AIT-Protocol/einstein-ait-prod/blob/main/neurons/miners/zephyr/miner.py).


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

   We recommend using pm2 to run the miner as it will automatically restart the miner if it crashes.

   ```bash
   pm2 start neurons/miners/openai/miner.py --name s3_openai_miner \
   --interpreter python \
   -- --netuid 78 or 3 \ # 78 for testnet and 3 for mainnet
   --subtensor.network test or finney \ # test for testnet and finney for mainnet
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

   *NOTE: Your wallet and wallet's hotkey must be created using the bittensor-cli and registered to the netuid 78 (our testnet uid) or 3 (our mainnet uid). Additionally, you can run the validator in trace mode by using `--logging.trace` instead of `--logging.debug`*

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
   pm2 logs s3_openai_miner # This will show you the logs of the miner
   pm2 stop {process_id} # This will stop the process
   ```

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
