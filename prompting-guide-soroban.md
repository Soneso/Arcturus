# Arcturus Soroban GPT Prompting guide

This prompting guide provides general information and prompting examples for the Arcturus Soroban GPT.

# General

## Network

Arcturus uses the public net by default. If you would like to obtain data or perform actions on testnet or futurenet, you need to specify the network in your prompt.

# Soroban prompts

Fetch contract metadata for contract id or wasm id:

`From testnet, show me the contract metadata for the contract with this id: CBMIGP7IBD47JCSKYPHCFG2FQIFE66RMGNYTGGYK356U7WJ3XXXITLMM`

Get latest ledger sequence:

`What is the latest soroban ledger sequence?`

List contract events:

`Did the contract with the id CBMIGP7IBD47JCSKYPHCFG2FQIFE66RMGNYTGGYK356U7WJ3XXXITLMM publish any events on testnet within the last 1000 ledgers?`

Fetch contract code for wasm id and contract id (WebAssembly bytecode as base64):

`Show me the contract code for the contract with id: CBMIGP7IBD47JCSKYPHCFG2FQIFE66RMGNYTGGYK356U7WJ3XXXITLMM on testnet.`

Fetch the status of a given transaction:

`What is the status of the soroban transaction with id ... on testnet?` 

Encode and decode smart contract values (SCVal):

`Can you please encode the string "friend" to a scval?`

`Decode this scval: AAAADgAAAAZmcmllbmQAAA==`

Fetch contract data:

`Transform the symbol "COUNTER" to a scval`
> ChatGPT answer: `The symbol "COUNTER" has been transformed into a SCVal, encoded as a base64 XDR string: AAAADwAAAAdDT1VOVEVSAA==`

`Show me the contract data with the key AAAADwAAAAdDT1VOVEVSAA== stored by this contract on testnet: CBMIGP7IBD47JCSKYPHCFG2FQIFE66RMGNYTGGYK356U7WJ3XXXITLMM - storage type: persistent`

Invoke contract function:

When it comes to invoking a contract function, Arcturus will prepare the corresponding transaction. But you must sign it. To do so, use the Freighter Wallet. Make sure to enable "Experimental Mode" in "Settings->Preferences".

`Invoke the function 'increment' of this contract: CBMIGP7IBD47JCSKYPHCFG2FQIFE66RMGNYTGGYK356U7WJ3XXXITLMM using the account <your source account id from the freighter wallet here>`

`Invoke the function 'hello' with the argument 'friend' of type symbol of the contract CDGAOUYONVDFBVGQ2U5F7IJ5JJHKDNNO5775LARCLBHCSDT72PH7BUTY with the source account <your source account id from the freighter wallet here>`