# Arcturus

Arcturus will be a ChatGPT plugin that will be able to retrieve and combine real-time data from the Stellar Blockchain and Soroban. Once the user activates the plugin from the ChatGPT store, he can request and receive text-based, real-time information from the Stellar Blockchain and Soroban by prompting ChatGPT. 

The main advantage of the plugin is the improvement of usability, which will allow users and developers to use natural language to obtain data from the Stellar Blockchain and Soroban. It will also allow users to easily create transactions and send them to the Network by prompting the AI Model using natural language.

In this first step I want to implement the core functionality, so that the Arcturus Stellar ChatGPT Plugin can request and interpret data from Stellar Horizon and Soroban RPC. To do so, the Arcturus API needs to be implemented and the specifications and examples for the AI Model need to be prepared and extensively tested. 

Furthermore, the Arcturus Plugin will be capable of composing transactions and after external signing, able to send them to Stellar Horizon and Soroban RPC via the Arcturus API. External signing will be implemented via WalletConnect.

Over time, the system will evolve by implementing different SEPs and using additional services like for example Stellar Expert and Soroban Assistant AI.

## Setup locally
To run the plugin you need to have developer access to ChatGPT plugin development. If you do not already have plugin developer access, please [join the waitlist](https://openai.com/waitlist/plugins).

You can install the current version of the plugin from source code.

```bash
git clone https://github.com/Soneso/Arcturus.git
cd Arcturus
pip install .
```

To run the plugin, enter the following command:

```bash
python main.py
```

Once the local server is running:

1. Navigate to https://chat.openai.com. 
2. In the Model drop down, select "Plugins" (note, if you don't see it there, you don't have access yet).
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter in `localhost:5003` since this is the URL the server is running on locally, then select "Find manifest file".

The plugin should now be installed and enabled! You can start with a question like "Please display the account details of this Stellar account: GARDNV3Q7YGT4AKSDF25LT32YSCCW4EV22Y2TV3I2PU2MMXJTEDL5T55"

