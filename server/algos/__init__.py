from typing import Optional
from server.database import Post

def get_feed(cursor: Optional[str] = None, limit: int = 20):
    try:
        query = Post.select().order_by(Post.indexed_at.desc())
        
        if cursor:
            query = query.where(Post.indexed_at < cursor)
            
        posts = list(query.limit(limit))
        
        return {
            'cursor': posts[-1].indexed_at.isoformat() if posts else None,
            'feed': [{'post': post.uri} for post in posts] if posts else []
        }
    except Exception as e:
        print(f"Error in get_feed: {e}")
        return {'cursor': None, 'feed': []}

algos = {
    'at://did:plc:yhebq6pwmyhlhdyhosu7jpmi/app.bsky.feed.generator/sask-ed-feed': get_feed
}