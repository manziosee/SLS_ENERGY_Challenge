from django.test import TestCase, Client
from django.urls import reverse
from api.models import Tweet, User
import json
from datetime import datetime

class UserRecommendationTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(user_id="1", screen_name="user1", description="First user")
        self.user2 = User.objects.create(user_id="2", screen_name="user2", description="Second user")
        self.user3 = User.objects.create(user_id="3", screen_name="user3", description="Third user")

        self.tweet1 = Tweet.objects.create(
            tweet_id="1001", user_id="1", text="Hello world", created_at=datetime.now(),
            in_reply_to_user_id="2", lang="en", hashtags=[{"text": "test"}]
        )
        self.tweet2 = Tweet.objects.create(
            tweet_id="1002", user_id="2", text="Reply to user1", created_at=datetime.now(),
            in_reply_to_user_id="1", lang="en", hashtags=[{"text": "reply"}]
        )
        self.tweet3 = Tweet.objects.create(
            tweet_id="1003", user_id="3", text="Retweet from user1", created_at=datetime.now(),
            retweeted_status={"user": {"id_str": "1"}}, lang="en", hashtags=[{"text": "retweet"}]
        )

    def test_user_recommendation(self):
        client = Client()
        response = client.get(reverse('user_recommendation'), {
            'user_id': '1', 'type': 'both', 'phrase': 'Hello', 'hashtag': 'test'
        })
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        recommendations = response_data.get('recommendations', [])
        
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]['user_id'], '2')
        self.assertEqual(recommendations[1]['user_id'], '3')
        self.assertEqual(recommendations[0]['screen_name'], 'user2')
        self.assertEqual(recommendations[1]['screen_name'], 'user3')
