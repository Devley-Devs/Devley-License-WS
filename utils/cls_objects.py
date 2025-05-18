import time, uuid
from typing import Union
from fastapi import WebSocket

class LicenseObject:
    def __init__(self, license_key: str = ''):
        self.license_key: str = license_key
        splitted_data: list = license_key.split('_') if license_key else []
        self.transaction_id: str =  splitted_data[0] if len(splitted_data) > 0 else ''
        self.user_id: str = splitted_data[1] if len(splitted_data) > 1 else ''
        self.uuid: str = splitted_data[2] if len(splitted_data) > 2 else ''

class ProductObject:
    def __init__(self, data: dict):
        self._id: str = data.get('product', {}).get('_id', '')
        self.slug: str = data.get('product', {}).get('slug', '')
        self.name: str = data.get('product', {}).get('name', '')
        self.tag: str = data.get('product', {}).get('tag', '')
        self.icon: str = data.get('product', {}).get('icon', '')
        self.description: str = data.get('product', {}).get('description', '')
        self.description_full: str = data.get('product', {}).get('description_full', '')
        self.gallery: list = data.get('product', {}).get('gallery', [])
        self.additional: dict = data.get('product', {}).get('additional', {})
        self.color_hex: str = data.get('product', {}).get('color_hex', '')
        self.priority: int = data.get('product', {}).get('priority', 0)
        self.version: float = data.get('product', {}).get('version', 0)
        self.price: float = data.get('product', {}).get('price', 0.0)
        self.license: str = data.get('product', {}).get('license', '')
        self.max_price: float = data.get('product', {}).get('max_price', 0.0)
        self.link: str = data.get('product', {}).get('link', '')
        self.license_key: str = data.get('license_key', '')

    def __iter__(self):
        yield "_id", self._id
        yield "slug", self.slug
        yield "name", self.name
        yield "tag", self.tag
        yield "icon", self.icon
        yield "description", self.description
        yield "description_full", self.description_full
        yield "gallery", self.gallery
        yield "additional", self.additional
        yield "color_hex", self.color_hex
        yield "priority", self.priority
        yield "version", self.version
        yield "price", self.price
        yield "license", self.license
        yield "max_price", self.max_price
        yield "link", self.link
        yield "license_key", self.license_key

class ClientWSObject:
    def __init__(self, ws: WebSocket, product: ProductObject, product_version: float, license: LicenseObject):
        self.ws: WebSocket = ws
        self.ip = (self.ws.client or ['127.0.0.1'])[0]
        self.version = product_version
        self.connect_time: int = int(time.time())
        self.session_id: str = str(uuid.uuid4()).split('-')[0]
        self.product_slug: str = product.slug
        self.product_id: str = product._id
        self.user_id: str = license.user_id
        self.transaction_id: str = license.transaction_id

    def __iter__(self):
        yield "ip", self.ip
        yield "version", self.version
        yield "product_slug", self.product_slug
        yield "connect_time", self.connect_time
        yield "session_id", self.session_id
        yield "product_id", self.product_id
        yield "user_id", self.user_id
        yield "transaction_id", self.transaction_id


class UserObject:
    def __init__(self, data: dict):
        self._id: Union[str, None] = data.get('_id')
        self.id: str = data.get('id', '')
        self.username: str = data.get('username', '')
        self.avatar: str = data.get('avatar', '')
        self.discriminator: str = data.get('discriminator', '')
        self.public_flags: int = data.get('public_flags', 0)
        self.premium_type: bool = data.get('premium_type', False)
        self.flags: int = data.get('flags', 0)
        self.banner: Union[str, None] = data.get('banner', None)
        self.accent_color: int = data.get('accent_color', 0)
        self.global_name: str = data.get('global_name', '')
        self.avatar_decoration_data: Union[dict, None] = data.get('avatar_decoration_data', None)
        self.banner_color: str = data.get('banner_color', '')
        self.mfa_enabled: bool = data.get('mfa_enabled', False)
        self.locale: str = data.get('locale', '')
        self.clan: Union[dict, None] = data.get('clan', None)
        self.email: str = data.get('email', '')
        self.verified: bool = data.get('verified', False)
        self.role: str = data.get('role', 'customer')

    def __iter__(self):
        yield "_id", self._id
        yield "id", self.id
        yield "username", self.username
        yield "avatar", self.avatar
        yield "discriminator", self.discriminator
        yield "public_flags", self.public_flags
        yield "premium_type", self.premium_type
        yield "flags", self.flags
        yield "banner", self.banner
        yield "accent_color", self.accent_color
        yield "global_name", self.global_name
        yield "avatar_decoration_data", self.avatar_decoration_data
        yield "banner_color", self.banner_color
        yield "mfa_enabled", self.mfa_enabled
        yield "locale", self.locale
        yield "clan", self.clan
        yield "email", self.email
        yield "verified", self.verified
        yield "role", self.role