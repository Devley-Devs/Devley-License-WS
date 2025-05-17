from json import JSONDecodeError
import uvicorn, dotenv, os, httpx
from collections import defaultdict
from typing import Union, Dict, Tuple
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from utils.utils import LicenseObject, ClientWSObject, ProductObject, UserObject

dotenv.load_dotenv()
PORT: int = int(os.getenv('PORT', 5000))

app = FastAPI()

CONN_CLIENTS: Dict[str, Dict[str, ClientWSObject]] = defaultdict(dict)
VERSION: float = float(os.getenv('VERSION', 1))
DASHBOARD_URL: str = os.getenv('DASHBOARD_URL', '')

def check_authorization(request: Request) -> Tuple[bool, Union[UserObject, None], Union[JSONResponse, None]]:
    authorization: Union[str, None] = request.headers.get('Authorization')
    if authorization is None:
        return False, None, JSONResponse(
            status_code=401,
            content={ "error": "Authorization not Found" }
        )
    user_obj = UserObject(httpx.get(f"{DASHBOARD_URL}/api/account", headers={"Authorization": authorization}, timeout=10).json())
    if user_obj._id is None:
        return False, user_obj, JSONResponse(
            status_code=401,
            content={ "error": "Invalid Authentication" }
        )
    return True, user_obj, None

@app.get("/")
async def license_welcome():
    return PlainTextResponse(f"Devley License Websocket System V{VERSION}")

@app.get("/api/getActiveInstances")
async def active_instances(request: Request):
    auth_status, user_obj, auth_response = check_authorization(request)
    if not auth_status or user_obj == None:
        return auth_response
    user_id: Union[str, None] = request.query_params.get('user_id')
    connected_client = []
    for conn in CONN_CLIENTS.values():
        for instance in conn.values():
            if ((user_obj.role == 'owner') and (user_id == '*')) or (instance.user_id == user_id) or (instance.user_id == user_obj._id):
                connected_client.append(dict(instance))
    return JSONResponse(
        status_code=200,
        content=connected_client
    )

@app.post("/api/terminateInstances")
async def terminate_instances(request: Request):
    auth_status, user_obj, auth_response = check_authorization(request)
    if not auth_status or user_obj == None:
        return auth_response
    request_body = await request.json()
    product_slug: Union[str, None] = request_body.get('product_slug')
    license_key: Union[str, None] = request_body.get('license_key')
    message: Union[str, None] = request_body.get('message')
    if (product_slug == None) or (license_key == None) or (message == None):
        return JSONResponse(
            status_code=403,
            content={ "error": "JSON Body is not fully passed" }
        )
    license_obj = LicenseObject(license_key)
    if ((user_obj.role != 'owner') and (license_obj.user_id != user_obj.id)):
        return JSONResponse(
            status_code=401,
            content={ "error": "Invalid Authentication" }
        )
    client_key = f'{license_obj.transaction_id}_{license_obj.user_id}'
    instance = CONN_CLIENTS.get(product_slug, {}).get(client_key)
    if instance == None:
        return JSONResponse(
            status_code=404,
            content={ "error": "The Request Instance not found in the connected list" }
        )
    print("[!] Terminating Client Connection", instance.ws, instance.product_slug, license_key)
    await instance.ws.send_json({ "event": "terminate", "error": message or "Forcibly Terminated by the User via Dashboard" })
    await instance.ws.close()
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "success": True
        }
    )

@app.websocket("/ws/{product_slug}/{product_version}/{license_key}")
async def license_websocket(websocket: WebSocket, product_slug: str, product_version: float, license_key: str):
    await websocket.accept()
    valid_license = httpx.post(f"{DASHBOARD_URL}/api/getLicense", headers={"origin": 'devley-ws'}, timeout=10,
                                json={ 'product_slug': product_slug, 'license_key': license_key, 'version': product_version }
                            )
    if valid_license.status_code != 200:
        await websocket.send_json({ "error": "Invalid License Key Provided" })
        return await websocket.close()
    license_obj = LicenseObject(license_key)
    product_obj = ProductObject(valid_license.json())
    client_key = f'{license_obj.transaction_id}_{license_obj.user_id}'
    last_client = CONN_CLIENTS.get(product_slug, {}).get(client_key)
    if last_client != None:
        print("[!] Closing Existing Client Connection", last_client.ws, last_client.product_slug, license_key)
        await last_client.ws.send_json({ "event": "terminate", "error": "Another Product Session is using the same License Key" })
        await last_client.ws.close()
    print("[+] Client Connected", websocket, product_slug, license_key)
    ws_client = ClientWSObject(websocket, product_obj, product_version, license_obj)
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

if __name__ == "__main__":
    uvicorn.run("websocket:app", host="0.0.0.0", port=PORT, reload=True)