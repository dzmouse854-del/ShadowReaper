import tweepy, re, phonenumbers, requests, json
from datetime import datetime

BEARER = "YOUR_BEARER_TOKEN"
client = tweepy.Client(bearer_token=BEARER, wait_on_rate_limit=True)

EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_RE = re.compile(r'(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9})')

def deep_extract(handle: str):
    user = client.get_user(username=handle, user_fields=['created_at','location','public_metrics'])
    if not user.data: return {"error": "Not found"}

    user_id = user.data.id
    bio = user.data.description or ""
    emails, phones, domains, geo = [], [], [], []

    # Bio scan
    emails.extend(EMAIL_RE.findall(bio))
    for p in PHONE_RE.findall(bio):
        try:
            parsed = phonenumbers.parse(p, None)
            if phonenumbers.is_possible_number(parsed):
                phones.append(phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
        except: pass
    domains.extend([mail.split('@')[1] for mail in emails if '@' in mail])

    # Timeline sweep (200 tweets)
    tweets = client.get_users_tweets(id=user_id, max_results=100, tweet_fields=['created_at','geo','text'])
    if tweets.data:
        for t in tweets.data:
            txt = t.text
            emails.extend(EMAIL_RE.findall(txt))
            for p in PHONE_RE.findall(txt):
                try:
                    parsed = phonenumbers.parse(p, None)
                    if phonenumbers.is_possible_number(parsed):
                        phones.append(phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
                except: pass
            if t.geo: geo.append(t.geo.get('full_name', ''))

    return {
        "handle": handle,
        "created": str(user.data.created_at),
        "bio": bio,
        "location": user.data.location or "",
        "email_domains": list(set(domains)),
        "emails": list(set(emails)),
        "phones_intl": list(set(phones)),
        "geo_tags": list(set(geo)),
        "followers": user.data.public_metrics['followers_count'],
        "tweets": user.data.public_metrics['tweet_count'],
        "scan_time": datetime.utcnow().isoformat()
    }
