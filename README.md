# Arcturus

Arcturus is a so called [GPT](https://openai.com/blog/introducing-gpts) for ChatGPT. It is able to retrieve and combine real-time data from the Stellar Blockchain and Soroban. By prompting Arcturus GPT, you can request and receive text-based, real-time information from the Stellar Blockchain and Soroban. 

Arcturus was initially planned to be a ChatGPT Plugin. But plugins stopped working locally at some point in time and GPTs were announced by OpenAI as a successor to Chat GPT Plugins. It can still be used as a plugin, should they be reactivated. Another problem with plugins is that they had a very limited context window at the time of testing. This had bad consequences to the answers given by ChatGPT, because ChatGPT forgot parts of the plugin spec and tried to find the requested answers without using the plugin.

The main goal of Arcturus is the improvement of usability, allowing users and developers to use natural language to obtain data from the Stellar Blockchain and Soroban. It will also allow users to easily create transactions and send them to the Network by prompting the AI Model using natural language.

## Implementation status

Currently the plugin can fetch and interpret Stellar Blockchain data related to:

### Accounts
- account details (such as balances, thresholds, signers, etc.)
- directory info from stellar expert (off-chain data)

### Assets
- list assets for issuer and/or asset code
- asset details (such as issuer, number of trustlines, etc.)

### Claimable Balances
- list claimable balances for claimant id and/or sponsor id
- claimable balance details (such as the claiming conditions)

### Payments
- list payments for account, transaction, ledger
- payment details

### Operations
- list all types of operations for account, transaction, ledger, liquidity pool, claimable balance
- operation details for all types of Stellar operations

### Transactions
- list for account, ledger, claimable balance, liquidity pool
- transaction details

### Liquidity Pools
- list liquidity pools for account and reserves
- liquidity pool details 

### SDEX Offers
- list offers from given accounts
- list offers by selling asset, buying asset, sponsor seller, etc.
- offer details

### SDEX Orderbook
- list entries by selling and buying asset

### Trades
- list for account, liquidity pool, offers, base asset, counter asset, etc.

### Domains
- check if blocked by stellar expert (off-chain data)

### Stellar Toml
- Off-chain stellar (toml) data associated with the account's home domain

### Soroban
- list contract events
- fetch contract data 
- fetch contract code for wasm id and contract id
- fetch contract metadata for contract id and wasm id
- fetch the status of a given transaction
- get latest ledger
- encode and decode smart contract values (SCVal)

### Network
Arcturus can switch networks for its requests as given by the prompt. It can use public net, testnet and futurenet. Default is public net.

### Actions

Furthermore it can perform following actions:

- submit signed transactions (xdr) to the Stellar Network
- encode and decode muxed accounts
- prepare trust asset transaction and link to be signed with freighter on the Arcturus webpage
- prepare payment transaction and link to be signed with freighter on the Arcturus webpage 
