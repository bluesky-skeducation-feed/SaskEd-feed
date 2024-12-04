from typing import Optional
from server.database import Post
from server.logger import logger

def get_feed(cursor: Optional[str] = None, limit: int = 20):
    logger.info(f"Feed request - cursor: {cursor}, limit: {limit}")
    try:
        query = Post.select().order_by(Post.indexed_at.desc())
        posts = list(query)
        logger.info(f"Raw posts from database: {posts}")
        logger.info(f"Number of posts found: {len(posts)}")
        
        response = {'cursor': None, 'feed': []}
        logger.info(f"Response structure: {response}")
        return response
    except Exception as e:
        logger.error(f"Feed error: {e}")
        logger.error(f"Exception details: {str(e)}")
        return {'cursor': None, 'feed': []}

algos = {
    'at://did:plc:yhebq6pwmyhlhdyhosu7jpmi/app.bsky.feed.generator/sask-ed-feed': get_feed
}