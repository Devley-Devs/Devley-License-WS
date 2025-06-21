import { CONN_CLIENTS } from "../..";
import { LicenseObject } from "../types";
import { checkAuthorization } from "../auth";

export default async function terminateInstances(
  req: Request
): Promise<Response> {
  const authResult = await checkAuthorization({ request: req });

  if ((authResult.status !== 200) || (authResult.user == null)) {
    return new Response(JSON.stringify(authResult.body), {
      status: authResult.status,
    });
  }

  try {
    const body = (await req.json()) as any;
    const { product_slug, license_key, message } = body;

    if (!product_slug || !license_key || !message) {
      return new Response(
        JSON.stringify({ error: "JSON Body is not fully passed" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    const license_obj = new LicenseObject(license_key);
    const client_key = `${license_obj.transaction_id}_${license_obj.user_id}`;
    const instance = CONN_CLIENTS.get(client_key);

    if (instance && ((instance.user_id === license_obj.user_id) || (authResult.user.role === "owner"))) {
      instance.ws.send(
        JSON.stringify({ event: "terminate", message: message })
      );
      instance.ws.close();
      CONN_CLIENTS.delete(client_key);
      console.log(`[!] Terminating Client Connection ${product_slug} ${license_key} ${message}`);
      return new Response(
        JSON.stringify({
          status: "success",
          success: true,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    } else {
      console.error(`[X] WebSocket connection not found ${product_slug} ${license_key}`);
      return new Response(
        JSON.stringify({ error: "WebSocket connection not found", success: false }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }
  } catch (error) {
    console.error("[X] Invalid request body passed");
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
