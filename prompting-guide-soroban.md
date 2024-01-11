# Arcturus Soroban GPT Prompting guide

This prompting guide provides general information and prompting examples for the Arcturus Soroban GPT.

# General

## Network

By default, currently Arcturus uses the testnet by default. As soon as Soroban will be released to main net, it will use the main net by default. If you would like to obtain data or perform actions on futurenet, you need to specify the network in your prompt.

# Soroban prompts

Fetch contract metadata for contract id or wasm id:

`From testnet, show me the contract metadata for the contract with this id: CBMIGP7IBD47JCSKYPHCFG2FQIFE66RMGNYTGGYK356U7WJ3XXXITLMM`

Get latest ledger sequence:

`What is the latest soroban ledger sequence?`

List contract events:

`Did the contract with the id CD2VYCS6AT37NIBI3FJ2HPWUQQHDA44VGGB64FR5IYUHNQSKQ33ZX5KE publish any events on testnet within the last 1000 ledgers?`

Fetch contract code for wasm id and contract id (WebAssembly bytecode as base64):

`Show me the contract code for the contract with id: CB7INA2ZOVWTIWD7W5FSNXY2XRPXKGNMJO7Q6SH7LWQB4KNHA3IZU4VY on testnet.`

Fetch the status of a given transaction:

`What is the status of the soroban transaction with id ... on testnet?` 

Encode and decode smart contract values (SCVal):

`Can you please encode the string "friend" to a scval?`

`Decode this scval: AAAADgAAAAZmcmllbmQAAA==`

Fetch contract data:

`Transform the symbol "COUNTER" to a scval`
> ChatGPT answer: `The symbol "COUNTER" has been transformed into a SCVal, encoded as a base64 XDR string: AAAADwAAAAdDT1VOVEVSAA==`

`Show me the contract data with the key AAAADwAAAAdDT1VOVEVSAA== stored by this contract on testnet: CB7INA2ZOVWTIWD7W5FSNXY2XRPXKGNMJO7Q6SH7LWQB4KNHA3IZU4VY - storage type: persistent`

Invoke contract function:

`invoke the contract function 'increment' of this contract: CB7INA2ZOVWTIWD7W5FSNXY2XRPXKGNMJO7Q6SH7LWQB4KNHA3IZU4VY using the account <your source account id from the freighter wallet here>`

`invoke the contract function 'hello' with the argument 'friend' of type symbol of the contract CB6IWUN5WOUAB64QO7E23IMKGB3HBMDGOE3AASDSA22ECJ4MROG3RRF3 with the source account <your source account id from the freighter wallet here>`