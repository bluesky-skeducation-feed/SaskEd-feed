from collections import defaultdict
from atproto import models, Client
from server.logger import logger
from server.database import db, Post
from server import config
from datetime import datetime, timedelta

# Initialize client
client = Client()
client.login(config.BSKY_HANDLE, config.BSKY_APP_PASSWORD)

# Cache for list members
_list_members_cache = {
    'members': [],
    'last_updated': None
}

def get_list_members():
    """Get the current members of the authorized list with caching"""
    global _list_members_cache
    
    # Only fetch new list if cache is empty or older than 5 minutes
    now = datetime.now()
    if (_list_members_cache['last_updated'] is None or 
        now - _list_members_cache['last_updated'] > timedelta(minutes=5)):
        try:
            response = client.app.bsky.graph.get_list({'list': config.AUTHORIZED_LIST_URI})
            _list_members_cache['members'] = [item.subject.did for item in response.items]
            _list_members_cache['last_updated'] = now
            logger.info(f"Updated list members cache, found {len(_list_members_cache['members'])} members")
        except Exception as e:
            logger.error(f"Error fetching list members: {e}")
            # If there's an error, use cached members if available
            if not _list_members_cache['members']:
                return []
    
    return _list_members_cache['members']


def operations_callback(ops: defaultdict) -> None:
    posts_to_create = []

    # Get current list members
    authorized_users = get_list_members()

    for created_post in ops[models.ids.AppBskyFeedPost]["created"]:
        author = created_post["author"]
        record = created_post["record"]

        # print all texts just as demo that data stream works
        post_with_images = isinstance(record.embed, models.AppBskyEmbedImages.Main)
        inlined_text = record.text.replace("\n", " ")
        logger.info(
            f"NEW POST "
            f"[CREATED_AT={record.created_at}]"
            f"[AUTHOR={author}]"
            f"[WITH_IMAGE={post_with_images}]"
            f": {inlined_text}"
        )

        # Check if author is in the list
        if author in authorized_users:
            # Check for hashtags
            watched_hashtags = ["#sasked", "#saskedchat"]
            if record.text and any(
                hashtag in record.text.lower() for hashtag in watched_hashtags
            ):
                reply_root = reply_parent = None
                if record.reply:
                    reply_root = record.reply.root.uri
                    reply_parent = record.reply.parent.uri

                post_dict = {
                    "uri": created_post["uri"],
                    "cid": created_post["cid"],
                    "reply_parent": reply_parent,
                    "reply_root": reply_root,
                }
                posts_to_create.append(post_dict)

    posts_to_delete = ops[models.ids.AppBskyFeedPost]["deleted"]
    if posts_to_delete:
        post_uris_to_delete = [post["uri"] for post in posts_to_delete]
        Post.delete().where(Post.uri.in_(post_uris_to_delete))
        logger.info(f"Deleted from feed: {len(post_uris_to_delete)}")

    if posts_to_create:
        with db.atomic():
            for post_dict in posts_to_create:
                Post.create(**post_dict)
        logger.info(f"Added to feed: {len(posts_to_create)}")
