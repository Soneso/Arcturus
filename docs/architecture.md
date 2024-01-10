# Arcturus Architecture

## Overview

This section shows the components involved in the Arcturus project and how they interact with each other.

![Architecture overview](./images/architecture.png)

## Components

### GPTs

The `Arcturus Stellar GPT` and the `Arcturus Soroban GPT` live and run within `ChatGPT`. They provide a detailed openAPI specification, so that ChatGPT can act as an intelligent API caller to process the user's prompt.

### Arcturus Server

The `Arcturus Server` provides the API endpoints needed by the Arcturus GPTs, so that they can fetch the data they need. They can also send transaction data to the server for signing.

If the user requests the signing and sending of a transaction via GPT, such as sending a stellar payment or invoking a soroban contract function, the server composes the needed transaction (xdr) first. Then it stores it in its internal database and returns a signing link to the user.
Next, the user presses the link, which leads her to the corresponding Arcturus signing page. Here she can sign her transaction via the Freighter Wallet and send it to the Network.

### Website

Arcturus serves a couple of static pages (e.g., the landing page) and the dynamic signing pages.

### Stellar Infrastructure

The Arcturus Server uses Stellar Infrastructure Tools such as `Stellar Horizon`, `Stellar Expert`, `Soroban RPC Servers` to fetch the real time data needed by the GPTs to process the user's prompt. 

Furthermore, the signing pages use this infrastructure tools to send the signed transactions to the Stellar Network.
