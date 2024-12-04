import sys
import signal
import threading

from server import config
from server import data_stream

from flask import Flask, jsonify, request

from server.algos import algos
from server.data_filter import operations_callback
from server.database import Subscriber, db

app = Flask(__name__)

stream_stop_event = threading.Event()
stream_thread = threading.Thread(
    target=data_stream.run,
    args=(
        config.SERVICE_DID,
        operations_callback,
        stream_stop_event,
    ),
)
stream_thread.start()


def sigint_handler(*_):
    print("Stopping data stream...")
    stream_stop_event.set()
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


@app.route("/")
def index():
    return "ATProto Feed Generator powered by The AT Protocol SDK for Python (https://github.com/MarshalX/atproto)."


@app.route("/.well-known/did.json", methods=["GET"])
def did_json():
    if not config.SERVICE_DID.endswith(config.HOSTNAME):
        return "", 404

    return jsonify(
        {
            "@context": ["https://www.w3.org/ns/did/v1"],
            "id": config.SERVICE_DID,
            "service": [
                {
                    "id": "#bsky_fg",
                    "type": "BskyFeedGenerator",
                    "serviceEndpoint": f"https://{config.HOSTNAME}",
                }
            ],
        }
    )


@app.route("/xrpc/app.bsky.feed.describeFeedGenerator", methods=["GET"])
def describe_feed_generator():
    feeds = [{"uri": uri} for uri in algos.keys()]
    response = {
        "encoding": "application/json",
        "body": {"did": config.SERVICE_DID, "feeds": feeds},
    }
    return jsonify(response)


@app.route("/xrpc/app.bsky.feed.getFeedSkeleton", methods=["GET"])
def get_feed_skeleton():
    feed = request.args.get("feed", default=None, type=str)
    algo = algos.get(feed)
    if not algo:
        return "Unsupported algorithm", 400

    # Example of how to check auth if giving user-specific results:
    """
    from server.auth import AuthorizationError, validate_auth
    try:
        requester_did = validate_auth(request)
    except AuthorizationError:
        return 'Unauthorized', 401
    """

    try:
        cursor = request.args.get("cursor", default=None, type=str)
        limit = request.args.get("limit", default=20, type=int)
        body = algo(cursor, limit)
    except ValueError:
        return "Malformed cursor", 400

    return jsonify(body)


@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()

    # Check if required data is present
    if not data or "did" not in data:
        return jsonify({"error": "DID is required"}), 400

    try:
        with db.atomic():
            # Create or get subscriber
            subscriber, created = Subscriber.get_or_create(did=data["did"])

            status = "subscribed" if created else "already subscribed"
            return jsonify({"status": status, "did": data["did"]}), (
                200 if created else 409
            )  # 409 if already exists

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.get_json()

    # Check if required data is present
    if not data or "did" not in data:
        return jsonify({"error": "DID is required"}), 400

    try:
        query = Subscriber.delete().where(Subscriber.did == data["did"])
        deleted_count = query.execute()

        if deleted_count > 0:
            return jsonify({"status": "unsubscribed", "did": data["did"]}), 200
        else:
            return jsonify({"status": "not found", "did": data["did"]}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/subscribers", methods=["GET"])
def list_subscribers():
    try:
        subscribers = [
            {"did": sub.did, "subscribed_at": sub.subscribed_at.isoformat()}
            for sub in Subscriber.select()
        ]

        return jsonify({"subscribers": subscribers, "count": len(subscribers)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
