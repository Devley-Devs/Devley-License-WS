from typing import Union, Dict
from json import JSONDecodeError
import uvicorn, dotenv, os, httpx
from collections import defaultdict
from utils.utils import LicenseObject, ClientWSObject
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect

dotenv.load_dotenv()
PORT: int = int(os.getenv('PORT', 5000))

app = FastAPI()

CONN_CLIENTS: Dict[str, Dict[str, ClientWSObject]] = defaultdict(dict)
VERSION: float = float(os.getenv('VERSION', 1))
DASHBOARD_URL: str = os.getenv('DASHBOARD_URL', '')
SERVER_AUTH_CODE: str = os.getenv('SERVER_AUTH_CODE', '')

@app.get("/")
async def license_welcome():
    return PlainTextResponse(f"Devley License Websocket System V{VERSION}")

@app.get("/getActiveInstances")
async def active_instances(request: Request):
    authorization: Union[str, None] = request.headers.get('Authorization')
    if authorization != SERVER_AUTH_CODE:
        return JSONResponse(
            status_code=401,
            content={ "error": "Invalid Authorization" }
        )
    product_slug: Union[str, None] = request.query_params.get('product_slug')
    if product_slug:
        connected_client = {client: dict(client_obj) for client, client_obj in CONN_CLIENTS.get(product_slug, {}).items()}
        return JSONResponse(
            status_code=200,
            content=connected_client
        )
    return JSONResponse(
        status_code=404,
        content={ "error": "product_slug not found in query" }
    )

@app.websocket("/ws/{product_slug}/{license_key}")
async def license_websocket(websocket: WebSocket, product_slug: str, license_key: str):
    await websocket.accept()
    valid_license = httpx.post(f"{DASHBOARD_URL}/api/getLicense",
                                json={ 'product_slug': product_slug, 'license_key': license_key },
                                headers={"Authorization": SERVER_AUTH_CODE}
                            )
    if valid_license.status_code != 200:
        await websocket.send_json({ "error": "Invalid License Key Provided" })
        return await websocket.close()
    license_obj = LicenseObject(license_key)
    valid_license_obj = valid_license.json()
    await websocket.send_json(valid_license_obj)
    client_key = f'{license_obj.transaction_id}_{license_obj.user_id}'
    last_client = CONN_CLIENTS.get(product_slug, {}).get(client_key)
    if last_client != None:
        print("[!] Closing Existing Client Connection")
        await last_client.ws.send_json({ "event": "kill", "error": "Another Product Session is using the same License Key" })
        await last_client.ws.close()
    print("[+] Client Connected", websocket, product_slug, license_key)
    ws_client = ClientWSObject(websocket)
    CONN_CLIENTS[product_slug][client_key] = ws_client
    try:
        while True:
            try:
                data = await websocket.receive_json()
                print("[#] Data Received", websocket, product_slug, license_key, "\n", data)
            except JSONDecodeError:
                print("[?] Invalid JSON Passed", websocket, product_slug, license_key)
    except WebSocketDisconnect:
        last_client = CONN_CLIENTS.get(product_slug, {}).get(client_key)
        if last_client != None and last_client.session_id == ws_client.session_id:
            del CONN_CLIENTS[product_slug][client_key]
        print("[-] Client Disconnected", product_slug, websocket)

# TODO
# "event": "license_update"
# "event": "exit"

if __name__ == "__main__":
    uvicorn.run("websocket:app", host="0.0.0.0", port=PORT, reload=True)