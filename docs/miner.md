# 🏗️ Running Miners

## Base Models
1. AIT Custom API `Work In Progress`
2. [OpenAI](https://platform.openai.com/docs/introduction) (GPT variants)
3. [Zephyr Model](https://github.com/AIT-Protocol/einstein-ait-prod/blob/main/neurons/miners/zephyr/)

## OpenAI Miner

1. **Install Dependencies**:
   ```bash
   pip install -r neurons/miners/openai/requirements.txt
   ```

2. **Set OpenAI API Key**:
   ```bash
   echo 'OPENAI_API_KEY=your_api_key_here' >> .env
   ```

3. **Start Miner**:
   ```bash
   pm2 start neurons/miners/openai/miner.py --name s3_openai_miner --interpreter python -- --netuid 78 or {} --subtensor.network test or finney --wallet.name <your miner wallet> --wallet.hotkey <your miner hotkey> --logging.debug --logging.trace --neuron.model_id gpt-3.5-turbo-0125 --neuron.max_tokens 1024 --neuron.temperature 0.9 --neuron.top_p 0.9 --neuron.top_k 50 --neuron.system_prompt "your prompt engineering"
   ```

## Useful PM2 Commands
   ```bash
   pm2 status # Show status of all pm2 processes
   pm2 logs s3_openai_miner # Show logs of the miner
   pm2 stop s3_openai_miner # Stop the miner process
   ```

## Important Notes

- **CUDA Devices**: To use specific CUDA devices, set the `CUDA_VISIBLE_DEVICES` environment variable. For example:
  ```bash
  export CUDA_VISIBLE_DEVICES=1,2
  ```

- **Model Configuration**: You can customize the miner by editing the script in `neurons/miners/openai/miner.py` for your desired model. The flags and options allow you to specify the model, tokens, temperature, top_p, top_k, and system prompt.