## Prerequisites
- To run a validator, you will need at least 62GB of VRAM.

## Installation
Clone the repository 
```bash
git clone https://github.com/ait-protocol/einstein-ait-prod.git
cd prompting
bash install.sh
```

For ease of use, you can run the scripts as well with PM2. Installation of PM2 is: On Linux:
```bash
sudo apt update && sudo apt install jq && sudo apt install npm && sudo npm install pm2 -g && pm2 update
```

For more configuration options related to the wallet, axon, subtensor, logging, and metagraph, please refer to the Bittensor documentation.

To run the Hugging Face Bittensor Validator with default settings, use the following command:
```bash
python neurons/validator.py
--netuid 35/78 (35 is our mainnet and 78 is our testnet) \
--subtensor.network <finney/local/test> \
--neuron.device cuda \
--wallet.name <your wallet> # Must be created using the bittensor-cli \
--wallet.hotkey <your hotkey> # Must be created using the bittensor-cli \
--logging.debug # Run in debug mode, alternatively --logging.trace for trace mode \
--axon.port # VERY IMPORTANT: set the port to be one of the open TCP ports on your machine \
```

or use pm2 to run the miner in the background:
```bash
pm2 start neurons/validator.py \
--name "Hugging Face Validator" \
--interpreter python \
-- \
--netuid 35/78 \
--subtensor.network <finney/local/test> \
--neuron.device cuda \
--wallet.name <your wallet> \
--wallet.hotkey <your hotkey> \
--logging.debug \
--axon.port <open TCP port>
```

Running with autoupdate
You can run the validator in auto-update mode by using pm2 along with the run.sh bash script. This command will initiate two pm2 processes: one for auto-update monitoring, named s1_validator_update, and another for running the validator itself, named s1_validator_main_process.

```bash
pm2 start run.sh --name validator_autoupdate -- --wallet.name <your-wallet-name> --wallet.hotkey <your-wallet-hot-key>
```
Note: this is not an end solution, major releases or changes in requirements will still require you to manually restart the processes. Regularly monitor the health of your validator to ensure optimal performance.