import { CONN_CLIENTS } from "../..";
import { checkAuthorization } from "../auth";
import type { ClientWSObject } from "../types";

export default async function getActiveInstances(
  req: Request,
  url: URL
): Promise<Response> {
  const authResult = await checkAuthorization({ request: req });

  if ((authResult.status !== 200) || (authResult.user == null)) {
    return new Response(JSON.stringify(authResult.body), {
      status: authResult.status,
    });
  }

  const user = authResult.user;
  const urlParams = new URLSearchParams(url.search);
  const user_id = urlParams.get("user_id") || user._id || "";
  const connected_client: ClientWSObject[] = [];

  for (const instance of CONN_CLIENTS.values()) {
    if (
      instance &&
      ((user.role === "owner" && user_id === "*") ||
        String(instance.user_id) === user_id ||
        (user && user._id && String(instance.user_id) === user._id))
    ) {
      const { ws, ...instance_copy } = instance;
      connected_client.push(instance_copy);
    }
  }

  return new Response(JSON.stringify(connected_client), {
    headers: { "Content-Type": "application/json" },
  });
}
