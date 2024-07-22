from django.db import models

class Tweet(models.Model):
    tweet_id = models.CharField(max_length=255, primary_key=True)
    user_id = models.CharField(max_length=255, db_index=True)
    text = models.TextField()
    created_at = models.DateTimeField(db_index=True)
    in_reply_to_user_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    retweeted_status = models.JSONField(null=True, blank=True)
    lang = models.CharField(max_length=10, db_index=True)
    hashtags = models.JSONField()

class User(models.Model):
    user_id = models.CharField(max_length=255, primary_key=True)
    screen_name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)
    latest_contact_tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
