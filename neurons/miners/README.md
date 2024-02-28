# Biττensor: Einstein Subnet Miner Setup
*How to Mine on the Bittensor Einstein Subnet (SN5)*
## 1. INTRODUCTION
Our primary narrative as a mathematics, logic, and data analysis AI subnet is to optimize response accuracy. We achieve this by enabling the language model to autonomously write, test, and execute code within unique Python environments. This approach ensures that our responses are not only precise but also practical, effectively addressing everyday challenges faced by users. Furthermore, our deployment offers significant advantages to the Bittensor ecosystem. By providing a model capable of independent code writing and execution, we bolster the capabilities of other subnets, thereby enhancing their accuracy and improving the quality of responses network-wide. Therefore, our contributions extend beyond direct user support to elevating the overall functionality of the Bittensor ecosystem.
<br>
<br>
### Mission
At Einstein-AIT, our mission is to enhance the Bittensor ecosystem by providing a robust and reliable subnet dedicated to the computation of complex mathematical operations and logical reasoning. We strive to empower startups and enterprises by offering seamless access to our advanced computational resources through user-friendly APIs, tailored for real-world applications.
Our mission extends to creating symbiotic relationships with other subnets, fostering a culture of mutual growth and knowledge exchange, thereby adding capabilities to the broader network of models and applications.
### Vision
We are dedicated to aligning with Bittensor's core values of permissionless participation and the decentralization of services. Our vision is to cultivate a subnet that embodies these principles, fostering an environment where innovation thrives on the collective strength and diversity of its participants. Together, we are building the foundation for a more open, collaborative, and decentralized world.
### Compute Requirements
#### FINE TUNED MINER (WIP) REQUIREMENTS
- GPU with 18GB or higher VRAM
- Ubuntu 20.04.01 or 22.04.01 (Recommended)
- Python 3.9 or 3.10 (Recommended)
- CUDA 12.0 or higher
#### OPENAI MINER REQUIREMENTS
- Python 3.9 or 3.10 (Recommended)
## 2. INSTALLATION
This installation process requires [Ubuntu 22.04.1](https://old-releases.ubuntu.com/releases/22.04.1/ubuntu-22.04.1-desktop-amd64.iso) and python 3.9 or 3.10.
### 2.1 BEGIN BY INSTALLING BITTENSOR:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/opentensor/bittensor/master/scripts/install.sh)"
```
See Bittensor’s documentation for alternative installation instructions.
<Br>
**Bittensor Documentation:** [https://docs.bittensor.com/](https://docs.bittensor.com/)
### 2.2 VERIFY THE INSTALLATION:
Verify using the ***btcli*** command
```
btcli --help
```
which will give you the below output:
```

Explain
usage: btcli <command> <command args>

bittensor cli v6.1.0

positional arguments:
  {subnets,s,subnet,root,r,roots,wallet,w,wallets,stake,st,stakes,sudo,su,sudos,legacy,l}
    subnets (s, subnet)
                        Commands for managing and viewing subnetworks.
    root (r, roots)     Commands for managing and viewing the root network.
    wallet (w, wallets)
                        Commands for managing and viewing wallets.
    stake (st, stakes)  Commands for staking and removing stake from hotkey accounts.
    sudo (su, sudos)    Commands for subnet management
    legacy (l)          Miscellaneous commands.

options:
  -h, --help            show this help message and exit
  --config CONFIG       If set, defaults are overridden by passed file.
  --strict              If flagged, config will check that only exact arguments have been set.
  --no_version_checking
                        Set true to stop cli version checking.
  --no_prompt           Set true to stop cli from prompting the user.using the [Bittensor Command Line Interface](<https://docs.bittensor.com/getting-started/reference/btcli>) with **btcli --help*** and/or check the installation in python.Run the below command to install Bittensor in the above virtual environment.
```
Create a Cold & Hotkey with the commands below:
```
btcli w new_coldkey
```
```
btcli w new_hotkey
```
>   If you already have a Key, you can regenerate it ‘safely’ on a machine using btcli w regen_coldkeypub. However, you must regen the full key if you plan to register or transfer from that wallet. regen_coldkeypub lets you load the key without exposing your mnemonic to the server. If you want to, you can generate a key pair on a local safe machine to use as cold storage for the funds that you send.
```
btcli w regen_coldkeypub
```
```
btcli w regen_coldkey
```
```
btcli w regen_hotkey
```
## 4. CLONE EINSTEIN-SUBNET
```
git clone https://github.com/AIT-Protocol/einstein-ait-prod
```
Access the Einstein-Subnet Directory
```
cd einstein-ait-prod
```
## 5. EINSTEIN SUBNET DEPENDENCIES
> For optimal functionality of the Compute Subnet, it's essential to install the appropriate graphics drivers and dependencies.<br>

### Required dependencies for miners:
```
python -m pip install -r requirements.txt && python -m pip install -e .
```
```
pip install -r neurons/miners/openai/requirements.txt
```
```
echo 'OPENAI_API_KEY=your_api_key_here' >> .env
```
> You can access [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) to create new api key (Secret Key) <br>
>
### Login to Weight and Biases
```
wandb login
```
### Install the NVIDIA Driver
> Note: Loading the graphics card may be corrupted because your operating system is running in secure boot mode. To avoid this error you should turn off security boot in BIOS

```
nvidia-smi
```
Output:
```
Command 'nvidia-smi' not found, but can be installed with:
sudo apt install nvidia-utils-390         # version 390.157-0ubuntu0.22.04.2, or
sudo apt install nvidia-utils-418-server  # version 418.226.00-0ubuntu5~0.22.04.1
sudo apt install nvidia-utils-450-server  # version 450.248.02-0ubuntu0.22.04.1
sudo apt install nvidia-utils-470         # version 470.223.02-0ubuntu0.22.04.1
sudo apt install nvidia-utils-470-server  # version 470.223.02-0ubuntu0.22.04.1
sudo apt install nvidia-utils-525         # version 525.147.05-0ubuntu0.22.04.1
sudo apt install nvidia-utils-525-server  # version 525.147.05-0ubuntu0.22.04.1
sudo apt install nvidia-utils-535         # version 535.129.03-0ubuntu0.22.04.1
sudo apt install nvidia-utils-535-server  # version 535.129.03-0ubuntu0.22.04.1
sudo apt install nvidia-utils-510         # version 510.60.02-0ubuntu1
sudo apt install nvidia-utils-510-server  # version 510.47.03-0ubuntu3

```
Currently I am using ubuntu 22.04.1 operating system so I choose version 535
```
sudo apt install nvidia-driver-535
```
> Note: Nvidia requires to install the correct graphics card driver version for the operating system otherwise there will be an error.
```
sudo reboot
```
Then,
```
nvidia-smi
```
The output of which should look something like:
```
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.154.05             Driver Version: 535.154.05   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA Graphics Device         Off | 00000000:01:00.0  On |                  N/A |
|  0%   27C    P8               4W / 320W |    201MiB / 16376MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|    0   N/A  N/A      1478      G   /usr/lib/xorg/Xorg                          106MiB |
|    0   N/A  N/A      1792      G   /usr/bin/gnome-shell                         86MiB |
+---------------------------------------------------------------------------------------+
```
### Install the NVIDIA CUDA Toolkit
```
wget https://developer.download.nvidia.com/compute/cuda/12.3.1/local_installers/cuda-repo-ubuntu2204-12-3-local_12.3.1-545.23.08-1_amd64.deb
```
```
sudo dpkg -i cuda-repo-ubuntu2204-12-3-local_12.3.1-545.23.08-1_amd64.deb
```
```
sudo cp /var/cuda-repo-ubuntu2204-12-3-local/cuda-*-keyring.gpg /usr/share/keyrings/
```
```
sudo apt-get update
```
```
sudo apt-get -y install cuda-toolkit-12-3
```
```
sudo apt-get -y install -y cuda-drivers
```
```
export CUDA_VERSION=cuda-12.3
export PATH=$PATH:/usr/local/$CUDA_VERSION/bin
export LD_LIBRARY_PATH=/usr/local/$CUDA_VERSION/lib64
```
```
echo "">>~/.bashrc
echo "PATH=$PATH">>~/.bashrc
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH">>~/.bashrc
```
The output of which should look something like:
```
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2023 NVIDIA Corporation
Built on Fri_Nov__3_17:16:49_PDT_2023
Cuda compilation tools, release 12.3, V12.3.103
Build cuda_12.3.r12.3/compiler.33492891_0
```
You can refer to the Cuda installation documentation [here](https://developer.nvidia.com/cuda-12-3-1-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_local)
## 6. SETTING UP A MINER 
### Hotkey Registration
At this point, you will need some $TAO in your coldkey address for miner registration. Once your coldkey is funded, run the command below to register your hotkey:
#### Testnet
- subtensor.network: test
- netuid: 78
```
btcli s register --subtensor.network test --netuid 78 
```
#### Mainnet
- subtensor.network: finney
- netuid: 5
```
btcli s register --subtensor.network finney --netuid 5 
```
> When running this command, you must enter the wallet name and hotkey name that we instructed in step 2.2

> You should test on testnet before running on mainnet

### Start the miner:
Move to the einstein-ait-prod directory and run the following command:
#### Testnet:
```
python neurons/miners/openai/miner.py \
--netuid 78 
--subtensor.network test \
--wallet.name <your miner wallet name> \
--wallet.hotkey <your miner hotkey name> \
--neuron.model_id gpt-4 \
--neuron.max_tokens 1024 \
--neuron.temperature 0.9 \
--logging.debug
```
#### Mainnet:
```
python neurons/miners/openai/miner.py \
--netuid 5
--subtensor.network finney \
--wallet.name <your miner wallet name> \
--wallet.hotkey <your miner hotkey name> \
--neuron.model_id gpt-4 \
--neuron.max_tokens 1024 \
--neuron.temperature 0.9 \
--logging.debug
```
- The <mark>--neuron.model_id</mark> flag is used to specify the model you want to use. The default value is gpt3.5-turbo
- The <mark>--neuron.max_tokens</mark>  flag is used to specify the maximum number of tokens the model can generate. The default value is 256
- The <mark>--neuron.temperature</mark> flag is used to specify the temperature of the model. The default value is 0.7

The output when you run the miner will look something like this:
![alt text](image.png)
### Congratulations, you have successfully run the miner!