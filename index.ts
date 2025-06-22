import { websocket } from './src/websocket';
import { ClientWSObject, type WebSocketData } from './src/types';
import terminateInstances from './src/routes/terminateInstances';
import getActiveInstances from './src/routes/getActiveInstances';

const PORT = parseInt(Bun.env.PORT || "3000");
const VERSION = parseFloat(Bun.env.VERSION || "1.8");

export const CONN_CLIENTS: Map<string, ClientWSObject> = new Map();

Bun.serve({
  port: Number(PORT),
  async fetch(req, server) {
    const url = new URL(req.url);

    if (url.pathname === "/") {
      return new Response(`Devley License Websocket Server V${VERSION}`);
    }

    if (url.pathname === "/api/getActiveInstances") {
      return await getActiveInstances(req, url);
    }

    if (url.pathname === "/api/terminateInstances") {
      return await terminateInstances(req);
    }

    if (url.pathname.startsWith("/ws/")) {
      const parts = url.pathname.split("/");
      const product_slug = parts[2];
      const product_version = parseFloat(parts[3] || "2.4");
      const license_key = parts[4];

      if (server.upgrade(req, {
        data: { product_slug, product_version, license_key }
      })) {
        return;
      }
    }

    return new Response("Endpoint not found :>", { status: 404 });
  },
  websocket: {
    open(ws) {
      const { product_slug, product_version, license_key } = ws.data as WebSocketData;
      websocket.open(ws as any, product_slug as string, product_version as number, license_key as string);
    },
    message(ws, message) {
      websocket.message(ws as any, String(message));
    },
    close(ws) {
      websocket.close(ws as any);
    },
  },
});

console.log(`
██████╗ ███████╗██╗   ██╗██╗     ███████╗██╗   ██╗                     
██╔══██╗██╔════╝██║   ██║██║     ██╔════╝╚██╗ ██╔╝                     
██║  ██║█████╗  ██║   ██║██║     █████╗   ╚████╔╝                      
██║  ██║██╔══╝  ╚██╗ ██╔╝██║     ██╔══╝    ╚██╔╝                       
██████╔╝███████╗ ╚████╔╝ ███████╗███████╗   ██║                        
╚═════╝ ╚══════╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝                                                                                   
██╗     ██╗ ██████╗███████╗███╗   ██╗███████╗███████╗                  
██║     ██║██╔════╝██╔════╝████╗  ██║██╔════╝██╔════╝                  
██║     ██║██║     █████╗  ██╔██╗ ██║███████╗█████╗                    
██║     ██║██║     ██╔══╝  ██║╚██╗██║╚════██║██╔══╝                    
███████╗██║╚██████╗███████╗██║ ╚████║███████║███████╗                  
╚══════╝╚═╝ ╚═════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝                                                                     
██╗    ██╗███████╗    ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗ 
██║    ██║██╔════╝    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
██║ █╗ ██║███████╗    ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝
██║███╗██║╚════██║    ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗
╚███╔███╔╝███████║    ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║
 ╚══╝╚══╝ ╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
`);
console.log(`Accepting connections on => http://0.0.0.0:${PORT}`);