
export interface WebSocketData {
  product_slug: string;
  product_version: number;
  license_key: string;
}

export class UserObject {
  _id: string | null;
  role: string;
  // id: string;
  // username: string;
  // avatar: string;
  // discriminator: string;
  // public_flags: number;
  // premium_type: boolean;
  // flags: number;
  // banner: string | null;
  // accent_color: number;
  // global_name: string;
  // avatar_decoration_data: any | null;
  // banner_color: string;
  // mfa_enabled: boolean;
  // locale: string;
  // clan: any | null;
  // email: string;
  // verified: boolean;

  constructor(data: any) {
    this._id = data._id || null;
    this.role = data.role || 'customer';
    // this.id = data.id || '';
    // this.username = data.username || '';
    // this.avatar = data.avatar || '';
    // this.discriminator = data.discriminator || '';
    // this.public_flags = data.public_flags || 0;
    // this.premium_type = data.premium_type || false;
    // this.flags = data.flags || 0;
    // this.banner = data.banner || null;
    // this.accent_color = data.accent_color || 0;
    // this.global_name = data.global_name || '';
    // this.avatar_decoration_data = data.avatar_decoration_data || null;
    // this.banner_color = data.banner_color || '';
    // this.mfa_enabled = data.mfa_enabled || false;
    // this.locale = data.locale || '';
    // this.clan = data.clan || null;
    // this.email = data.email || '';
    // this.verified = data.verified || false;
  }
}

export class LicenseObject {
  license_key: string;
  transaction_id: string;
  user_id: string;
  uuid: string;

  constructor(license_key: string = '') {
    this.license_key = license_key;
    const splitted_data = license_key ? license_key.split('_') : [];
    this.transaction_id = splitted_data[0] || '';
    this.user_id = splitted_data[1] || '';
    this.uuid = splitted_data[2] || '';
  }
}

export class ProductObject {
  _id: string;
  slug: string;
  // name: string;
  // tag: string;
  // icon: string;
  // description: string;
  // description_full: string;
  // gallery: string[];
  // additional: any;
  // color_hex: string;
  // priority: number;
  // version: number;
  // price: number;
  // license: string;
  // max_price: number;
  // link: string;
  // license_key: string;

  constructor(data: any) {
    this._id = data?.product?._id || '';
    this.slug = data?.product?.slug || '';
    // this.name = data?.product?.name || '';
    // this.tag = data?.product?.tag || '';
    // this.icon = data?.product?.icon || '';
    // this.description = data?.product?.description || '';
    // this.description_full = data?.product?.description_full || '';
    // this.gallery = data?.product?.gallery || [];
    // this.additional = data?.product?.additional || {};
    // this.color_hex = data?.product?.color_hex || '';
    // this.priority = data?.product?.priority || 0;
    // this.version = data?.product?.version || 0;
    // this.price = data?.product?.price || 0.0;
    // this.license = data?.product?.license || '';
    // this.max_price = data?.product?.max_price || 0.0;
    // this.link = data?.product?.link || '';
    // this.license_key = data?.license_key || '';
  }
}

export class ClientWSObject {
  ws?: any;
  ip: string;
  version: number;
  connect_time: number;
  session_id: string;
  product_slug: string;
  product_id: string;
  user_id: string;
  transaction_id: string;

  constructor(ws: any, product: ProductObject, product_version: number, license: LicenseObject) {
    this.ws = ws;
    this.ip = this.ws.client?.[0] || '127.0.0.1';
    this.version = product_version;
    this.connect_time = Math.floor(Date.now() / 1000);
    this.session_id = Math.random().toString(36).substring(2, 15);
    this.product_slug = product.slug;
    this.product_id = product._id;
    this.user_id = license.user_id;
    this.transaction_id = license.transaction_id;
  }
}
