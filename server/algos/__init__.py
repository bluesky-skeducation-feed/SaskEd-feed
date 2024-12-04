from server.database import Post


def get_feed(cursor=None, limit=20):
    try:
        query = Post.select().order_by(Post.indexed_at.desc())
        
        if cursor:
            query = query.where(Post.indexed_at < cursor)
        
        posts = query.limit(limit)
        
        feed = [{'post': post.uri} for post in posts]
        next_cursor = posts[-1].indexed_at.isoformat() if posts else None
        
        return {'feed': feed, 'cursor': next_cursor}
    except Exception as e:
        print(f"Feed error: {e}")
        return {'feed': [], 'cursor': None}

algos = {
    'at://did:plc:yhebq6pwmyhlhdyhosu7jpmi/app.bsky.feed.generator/sask-ed-feed': get_feed
}
