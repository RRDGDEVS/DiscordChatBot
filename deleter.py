import requests
import time
from datetime import datetime, timezone

BASE_URL = "https://discord.com/api/v10"

def get_headers(token):
    return {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

def is_older_than_14_days(message_id):
    """Discord snowflake ID encodes timestamp — check if message is older than 14 days."""
    timestamp_ms = (int(message_id) >> 22) + 1420070400000
    created_at = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    age = datetime.now(tz=timezone.utc) - created_at
    return age.days >= 14

def fetch_messages(token, channel_id, before=None):
    params = {"limit": 100}
    if before:
        params["before"] = before

    url = f"{BASE_URL}/channels/{channel_id}/messages"
    response = requests.get(url, headers=get_headers(token), params=params)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = response.json().get("retry_after", 1)
        print(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        return fetch_messages(token, channel_id, before)
    else:
        print(f"Failed to fetch messages: {response.status_code} {response.text}")
        return []

def bulk_delete(token, channel_id, message_ids):
    """Delete up to 100 messages at once (only works for messages < 14 days old)."""
    url = f"{BASE_URL}/channels/{channel_id}/messages/bulk-delete"
    response = requests.post(url, headers=get_headers(token), json={"messages": message_ids})

    if response.status_code == 204:
        print(f"Bulk deleted {len(message_ids)} messages.")
    elif response.status_code == 429:
        retry_after = response.json().get("retry_after", 1)
        print(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        bulk_delete(token, channel_id, message_ids)
    else:
        print(f"Bulk delete failed: {response.status_code} {response.text}")

def delete_single(token, channel_id, message_id):
    """Delete a single message (used for messages older than 14 days)."""
    url = f"{BASE_URL}/channels/{channel_id}/messages/{message_id}"
    response = requests.delete(url, headers=get_headers(token))

    if response.status_code == 204:
        print(f"Deleted old message {message_id}")
    elif response.status_code == 429:
        retry_after = response.json().get("retry_after", 1)
        print(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        delete_single(token, channel_id, message_id)
    else:
        print(f"Failed to delete {message_id}: {response.status_code}")

def delete_all_messages(token, channel_id):
    """Delete all messages in a channel — bulk for new, one-by-one for old."""
    before = None
    total_deleted = 0

    while True:
        messages = fetch_messages(token, channel_id, before)

        if not messages:
            break

        new_ids = [m["id"] for m in messages if not is_older_than_14_days(m["id"])]
        old_ids = [m["id"] for m in messages if is_older_than_14_days(m["id"])]

        # Bulk delete newer messages in chunks of 100
        if new_ids:
            for i in range(0, len(new_ids), 100):
                chunk = new_ids[i:i+100]
                if len(chunk) == 1:
                    # bulk-delete requires at least 2 messages
                    delete_single(token, channel_id, chunk[0])
                else:
                    bulk_delete(token, channel_id, chunk)
                total_deleted += len(chunk)
                time.sleep(1)

        # Delete older messages one by one
        for msg_id in old_ids:
            delete_single(token, channel_id, msg_id)
            total_deleted += 1
            time.sleep(0.5)

        before = messages[-1]["id"]

        if len(messages) < 100:
            break

    print(f"\nDone. Deleted {total_deleted} messages.")
