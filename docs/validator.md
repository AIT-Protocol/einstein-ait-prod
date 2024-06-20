# 🧾 Running Validators

## Installation
1. **Clone Repository and Install**:
   ```bash
   git clone https://github.com/ait-protocol/einstein-ait-prod.git
   cd einstein-ait-prod
   bash scripts/install.sh
   ```

2. **Update Repository**:
   ```bash
   bash scripts/update.sh
   ```

3. **Install PM2 and jq**:
   ```bash
   sudo apt update && sudo apt install jq npm && sudo npm install pm2 -g && pm2 update
   ```

## Running Validator
1. **Install Weights and Biases**:
   ```bash
   wandb login
   ```

2. **Run Validator**:
   ```bash
   pm2 start run.sh --name s3_validator_autoupdate -- --wallet.name <your-wallet-name> --wallet.hotkey <your-wallet-hot-key>
   ```

3. **Optional Commands**:
   ```bash
   python neurons/validator.py --netuid 78 or {} --subtensor.network test or finney --neuron.device cuda --wallet.name <your validator wallet> --wallet.hotkey <your validator hotkey> --logging.debug
   ```

4. **Useful PM2 Commands**:
   ```bash
   pm2 status # Show status of all pm2 processes
   pm2 logs s3_validator_autoupdate # Show logs of the validator
   pm2 stop s3_validator_autoupdate # Stop the validator process
   ```

## Important Notes

- **CUDA Devices**: To use specific CUDA devices, set the `CUDA_VISIBLE_DEVICES` environment variable. For example:
  ```bash
  export CUDA_VISIBLE_DEVICES=1,2
  ```

- **Weights and Biases**: Running `wandb login` initializes Weights and Biases, enabling you to view KPIs and metrics on your validator, which is strongly recommended to help the network improve from data sharing.