import json
import logging
from django.core.management.base import BaseCommand
from api.models import Tweet, User
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db import transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load tweets from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file containing tweets')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        with open(file_path, 'r', encoding='utf-8') as file:
            tweets = []
            users = {}
            for line in file:
                try:
                    data = json.loads(line)
                    if 'id_str' not in data or 'user' not in data:
                        continue
                    
                    tweet_id = data['id_str']
                    user_id = data['user']['id_str']
                    text = data.get('text', '')
                    created_at = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                    in_reply_to_user_id = data.get('in_reply_to_user_id')
                    retweeted_status = data.get('retweeted_status')
                    lang = data.get('lang')
                    hashtags = data.get('entities', {}).get('hashtags', [])

                    if user_id not in users:
                        users[user_id] = User(
                            user_id=user_id,
                            screen_name=data['user'].get('screen_name', ''),
                            description=data['user'].get('description', '')
                        )

                    tweets.append(Tweet(
                        tweet_id=tweet_id,
                        user_id=user_id,
                        text=text,
                        created_at=created_at,
                        in_reply_to_user_id=in_reply_to_user_id,
                        retweeted_status=retweeted_status,
                        lang=lang,
                        hashtags=hashtags
                    ))

                    if len(tweets) >= 1000:
                        self.bulk_insert(tweets, users)
                        tweets = []
                        users = {}

                except json.JSONDecodeError:
                    logger.error('Malformed JSON line skipped')
                    continue

            if tweets:
                self.bulk_insert(tweets, users)

    def bulk_insert(self, tweets, users):
        with transaction.atomic():
            User.objects.bulk_create(users.values(), ignore_conflicts=True)
            Tweet.objects.bulk_create(tweets, ignore_conflicts=True)
            logger.info('Bulk insert completed')
