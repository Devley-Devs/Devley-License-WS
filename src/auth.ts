import { UserObject } from './types.ts';

const DASHBOARD_URL = process.env.DASHBOARD_URL ?? "";

export async function checkAuthorization({ request }: { request: Request }) {
  const authorization = request.headers.get('authorization') || "";

  if (!authorization) {
    console.warn('[!] Authorization not found');
    return {
      status: 401,
      body: { error: 'Authorization not Found' },
    };
  }

  try {
    const response = await fetch(
      `${DASHBOARD_URL}/api/account`,
      {
        headers: { Authorization: authorization },
        method: 'GET',
      },
    );

    if (!response.ok) {
      console.error(`[${response.status}] Failed to authorize request`);
      return {
        status: response.status,
        body: { error: 'Invalid Authentication' },
      };
    }

    const data = await response.json();
    const user = new UserObject(data);

    return {
      status: 200,
      user: user,
    };
  } catch (error) {
    console.error('Error fetching user data:', error);
    return {
      status: 500,
      body: { error: 'Internal Server Error' },
    };
  }
}
