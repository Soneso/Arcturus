import json

import quart
import quart_cors
from quart import request
import arcturus.account as account
from stellar_sdk.exceptions import NotFoundError

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

HORIZON_URL = "https://horizon-testnet.stellar.org" 

@app.get("/account/details/<string:account_id>")
async def get_account_details(account_id):
    print("test: get account details")
    try:
        details = await account.get_details(HORIZON_URL, account_id)
    except NotFoundError:
        return quart.Response(response="Account not found", status=404)
    else:
        return quart.Response(response=json.dumps(details), status=200)

@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
