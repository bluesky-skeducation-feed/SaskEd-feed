from server.database import Post


def get_feed(cursor=None, limit=20):
    posts = []
    try:
        query = Post.select().order_by(Post.indexed_at.desc())
        if cursor:
            query = query.where(Post.indexed_at < cursor)
        posts = list(query.limit(limit))
    except Exception as e:
        print(f"Feed error: {e}")
    
    return {
        'cursor': posts[-1].indexed_at.isoformat() if posts else None,
        'feed': [{'post': p.uri} for p in posts]
    }

algos = {
    'at://did:plc:yhebq6pwmyhlhdyhosu7jpmi/app.bsky.feed.generator/sask-ed-feed': get_feed
}
