import { CONN_CLIENTS } from '../index';
import { LicenseObject, ProductObject, ClientWSObject } from './types';

const DASHBOARD_URL = Bun.env.DASHBOARD_URL || '';
const MAX_CONNECTIONS = parseInt(Bun.env.MAX_CONNECTIONS || "10000");

export const websocket = {
  async open(ws: WebSocket, product_slug: string, product_version: number, license_key: string) {
    if (CONN_CLIENTS.size >= MAX_CONNECTIONS) {
      console.log(`[WS] Connection refused: Max connections reached (${MAX_CONNECTIONS})`);
      ws.send(JSON.stringify({ event: 'terminate', message: 'Server is at maximum capacity' }));
      await new Promise(resolve => setTimeout(resolve, 2000));
      ws.close();
      return;
    }

    try {
      const valid_license = await fetch(
        `${DASHBOARD_URL}/api/getLicense`,
        {
          headers: { origin: 'devley-ws' },
          method: 'POST',
          body: JSON.stringify({ product_slug, license_key, version: product_version }),
        },
      );

      if (!valid_license.ok) {
        ws.send(JSON.stringify({ event: 'terminate', message: 'Invalid License Key Provided' }));
        await new Promise(resolve => setTimeout(resolve, 2000));
        ws.close();
        return;
      }

      const data = await valid_license.json();
      const license_obj = new LicenseObject(license_key);
      const product_obj = new ProductObject(data);
      const client_key = `${license_obj.transaction_id}_${license_obj.user_id}`;

      const existingClient = CONN_CLIENTS.get(client_key);
      if (existingClient?.ws) {
        console.log('[!] Closing Existing Client Connection', product_slug, product_version, license_key);
        existingClient.ws.send(JSON.stringify({ event: 'terminate', message: 'Another Product Session is using the same License Key' }));
        existingClient.ws.close();
      }

      const ws_client = new ClientWSObject(ws, product_obj, product_version, license_obj);
      CONN_CLIENTS.set(client_key, ws_client);

      console.log(`[+] Client Connected ${product_slug} ${product_version} ${license_key}`);
    } catch (error: any) {
      console.error({ error: error.message }, 'Error validating license:');
      ws.close();
    }
  },
  message(ws: WebSocket, message: string) {
    console.log('[#] Data Received', { message });
  },
  close(ws: WebSocket) {
    for (const [key, client] of CONN_CLIENTS.entries()) {
      if (client.ws === ws) {
        console.log(`[-] Client Disconnected ${client.product_slug} ${client.version} ${client.transaction_id} ${client.user_id}`);
        CONN_CLIENTS.delete(key);
        break;
      }
    }
  },
};
