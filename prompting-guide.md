# Prompting guide

This prompting guide provides general information and prompting examples for the Arcturus GPT.

# General

## Network

By default, Arcturus uses the main Stellar Network (public net). If you would like to obtain data or perform actions on testnet or futurenet, you need to specify the network in your prompt.

For example:

`How many lumens does the account GDZZDOTFUGDM56SRA2RYHL6GXV7HF3R6V5SR3SKYTG5STVQES4QCNWBP have on the testnet?`

## Conversation

You do not have to specify the account or other data in every prompt. Chat GPT remembers the conversation from previous prompts. For example, if you request some data for an account:

`Is there any home domain associated with this account GA2T6GR7VXXXBETTERSAFETHANSORRYXXXPROTECTEDBYLOBSTRVAULT?`
> ChatGPT answer

`Did the account issue any assets?`
> ChatGPT answer

`Is there any directory info associated with the account?`
> ChatGPT answer

`Is the domain associated with the account blacklisted?`
> ChatGPT answer

`Show me the stellar toml data associated with the domain`


# Accounts

You can ask Arcturus for account details and any data they contain. Furthermore, you can ask Arcturus for other on-chain and off-chain data associated with the account:

Here are some example prompts:

`Show me the details of this account: GARDNV3Q7YGT4AKSDF25LT32YSCCW4EV22Y2TV3I2PU2MMXJTEDL5T55`

`How many lumens does the account GBXEFLHWOXNNUBBYYDNSCK4QBZOUS6TTJGBUNCI5CDG7CRAY27UXVONL have`

`Show me current sequence number of this account GA2T6GR7VXXXBETTERSAFETHANSORRYXXXPROTECTEDBYLOBSTRVAULT`

On-chain data associated with the account can be fetched, like for example assets, claimable balances, payments, operations, transactions, liquidity pools, offers and trades. 

`Did this account issue any assets? G...`

`Does this account have any claimable balances? G...`

`Show me the 3 most recent payments of this account: G...`

`Show me the 3 most recent operations of this account: G...`

`Show me the 3 most recent transactions for this account: G...`

`Are there any liquidity pools associated with this account? G...` 

`Are there any offers associated with this account: G...`

`Show me the 3 most recent trades for this account: G...`

Off-chain:

Also off-chain data such as directory info from stellar expert:

`Display the directory info for this account: G...`

`Show me the stellar toml data for the domain associated with this account and check if the domain is blacklisted: GBUVRNH4RW4VLHP4C5MOF46RRIRZLAVHYGX45MVSTKA2F6TMR7E7L6NW`

`Can I trust this account?`


# Assets

You can ask Arcturus for asset details and fetch lists of assets for an issuer and/or asset code:

`Show me the details for the asset with code BOB and issuer GBUVRNH4RW4VLHP4C5MOF46RRIRZLAVHYGX45MVSTKA2F6TMR7E7L6NW`

`Show me the details for this asset: BOB:GBUVRNH4RW4VLHP4C5MOF46RRIRZLAVHYGX45MVSTKA2F6TMR7E7L6NW`

`Show me the list of assets with this code: yXLM`

`Did this account issue any assets? GBUVRNH4RW4VLHP4C5MOF46RRIRZLAVHYGX45MVSTKA2F6TMR7E7L6NW`

# Claimable balances

You can ask Arcturus for claimable balances details and fetch lists of claimable balances for a claimant is and/or sponsor id:

`Show me the details for this claimable balance: 00000000178826fbfe339e1f5c53417c6fedfe2c05e8bec14303143ec46b38981b09c3f9`

`Are there any claimable balances for this claimant? G...`

`Can any of them be claimed now?`

`Did this account sponsor any claimable balances? GBUVRNH4RW4VLHP4C5MOF46RRIRZLAVHYGX45MVSTKA2F6TMR7E7L6NW`

# Payments

You can ask Arcturus for payment details and fetch lists of payments for accounts, transactions, ledger:

`List the 2 most recent payments for this account and show me their details: G...`

`List the 2 most recent payments for this transaction: 3389e9f0f1a65f19736cacf544c2e825313e8447f569233bb8db39aa607c8889`

`And now for the ledger 49122497`

# Operations

You can ask Arcturus for operation details and fetch lists of operations for accounts, transactions, ledgers, liquidity pools, claimable balances:

`Show me the details of the operation with the id 12884905987`

`List the operations for this transaction: 3389e9f0f1a65f19736cacf544c2e825313e8447f569233bb8db39aa607c8889`

`Show me the 3 most recent operations for this account: G...`

`And now for the ledger 49122497`

`Next the 3 most recent for this liquidity pool 0000a8198b5e25994c1ca5b0556faeb27325ac746296944144e0a7406d501e8a`

# Transactions

You can ask Arcturus for transaction details and fetch lists of transactions for accounts, ledgers, liquidity pools, claimable balances:

`Show me the details of the transaction 3389e9f0f1a65f19736cacf544c2e825313e8447f569233bb8db39aa607c8889`

`Show me the 3 most recent transactions for this account: G...`

You can also submit signed xdr transactions to the Stellar Network:

`Submit this transaction to the Stellar Network: AAAAAgAAAAA6UgSUt5BkCY...`

# Liquidity Pools

You can ask Arcturus for liquidity pool details and fetch lists of liquidity pools for accounts, transactions, ledgers, liquidity pools, claimable balances:

`Display the details of this liquidity pool: 00027e57b10c37b92854c439e2406c110a9b0a545c463aa1aefe4efe524090e0`

`Are there any liquidity pools for lumens and OPAL:GCRNZGPSVIUDYJDQFQKP53GSJ77MPD36HQ7GKRMDKLSKJLD2AX3LDVOG ?`

# Offers

You can ask Arcturus for offer details and fetch lists of offers for accounts, selling asset, buying asset, sponsor, seller:

`Display the details of the offer with id: 1408264946`

`Does this account have any active offers: G...`

`Show me the 3 most recent offers of this seller: G...`


# Orderbook

You can ask Arcturus for orderbook entries by selling and buying asset:

`Show me the orderbook entries for lumens vs yXLM:GARDNV3Q7YGT4AKSDF25LT32YSCCW4EV22Y2TV3I2PU2MMXJTEDL5T55`

# Trades

You can ask Arcturus for lists of trades for accounts, liquidity pools, offers, base assets, counter assets:

`Show me the 2 most recent trades for lumes as base asset and yXLM:GARDNV3Q7YGT4AKSDF25LT32YSCCW4EV22Y2TV3I2PU2MMXJTEDL5T55 as counter asset`

`Show me the 2 most recent trades for this account: G...`

`Show me the 2 most recent trades for the offer with id: ...`

# Domains

You can ask Arcturus for directory info (from Stellar Expert) for a given domain.

`Show me the directory info for the domain ultrastellar.com`

`And now for the domain associated with this account: G...`

You can also ask if a domain is blacklisted (Stellar Expert):

`Is this domain blacklisted? binance.srl`

# Stellar toml

You can ask Arcturus for off-chain stellar (toml) data for a given domain:

`Show me the stellar toml data for the domain ultrastellar.com`

`Is there any off-chain data available for the domain ultrastellar.com`

`Show me the stellar toml data for the domain associated with this account: G...`


# Soroban

At the time being only works with the testnet and futurenet as Soroban is not yet published to public net.

Fetch contract metadata for contract id or wasm id:

`From testnet, show me the contract metadata for the contract with this id: CDROOMSAQBNXOL4TTPBDI3ONZNH5QNO4QTVQ3NPGT7FRX3KTGJKYBD6I`

List contract events:

`Did the contract with the id CD2VYCS6AT37NIBI3FJ2HPWUQQHDA44VGGB64FR5IYUHNQSKQ33ZX5KE publish any events on testnet within the last 1000 ledgers?`

Fetch contract data:

`Show me the contract data with the key "COUNTER" stored by this contract on testnet: CDROOMSAQBNXOL4TTPBDI3ONZNH5QNO4QTVQ3NPGT7FRX3KTGJKYBD6I - storage type: instance`

Fetch contract code for wasm id and contract id (WebAssembly bytecode as base64):

`Show me the contract coide for the contract with id: CDROOMSAQBNXOL4TTPBDI3ONZNH5QNO4QTVQ3NPGT7FRX3KTGJKYBD6I on testnet.`

Fetch the status of a given transaction:

`What is the status of the soroban transaction with id ... on testnet?` 

Get latest ledger sequence:

`What is the latest soroban ledger sequence?`

Encode and decode smart contract values (SCVal):











