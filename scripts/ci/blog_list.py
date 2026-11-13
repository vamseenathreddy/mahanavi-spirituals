"""Lists the Blogger blogs the saved Blogger token can post to (name, url, id, language, post count)."""
from mahanavi.config import get_settings
from mahanavi.publishers import blogger_publisher as bp

blog = bp._build_service(get_settings())  # noqa: SLF001
for b in blog.blogs().listByUser(userId="self").execute().get("items", []):
    print(f"BLOG: {b.get('name')!r} | {b.get('url')} | id={b['id']} | locale={b.get('locale', {}).get('language')} | posts={b.get('posts', {}).get('totalItems')}")
