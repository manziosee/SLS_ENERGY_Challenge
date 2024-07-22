from django.http import JsonResponse
from django.db.models import Count
from django.core.cache import cache
from api.models import Tweet, User
import math
from collections import defaultdict
import logging

CACHE_TIMEOUT = 60 * 5  # Cache timeout in seconds (5 minutes)
logger = logging.getLogger(__name__)

def log_base_e(x):
    return math.log(x)

def calculate_interaction_score(reply_count, retweet_count):
    return log_base_e(1 + 2 * reply_count + retweet_count)

def calculate_hashtag_score(same_tag_count):
    if same_tag_count > 10:
        return 1 + log_base_e(1 + same_tag_count - 10)
    return 1

def calculate_keywords_score(number_of_matches):
    if number_of_matches == 0:
        return 0
    return 1 + log_base_e(1 + number_of_matches)

def user_recommendation(request):
    user_id = request.GET.get('user_id')
    type_ = request.GET.get('type')
    phrase = request.GET.get('phrase')
    hashtag = request.GET.get('hashtag').lower()
    
    if not all([user_id, type_, phrase, hashtag]):
        return JsonResponse({'error': 'Missing query parameters'}, status=400)
    
    cache_key = f"user_recommendation_{user_id}_{type_}_{phrase}_{hashtag}"
    response_data = cache.get(cache_key)
    
    if response_data is None:
        try:
            valid_tweets = Tweet.objects.filter(
                user_id=user_id,
                lang__in=['ar', 'en', 'fr', 'in', 'pt', 'es', 'tr', 'ja']
            ).exclude(
                id__isnull=True,
                text__isnull=True,
                text='',
                created_at__isnull=True,
                hashtags__isnull=True
            ).distinct('tweet_id')

            interaction_counts = valid_tweets.values('user_id').annotate(
                reply_count=Count('in_reply_to_user_id'),
                retweet_count=Count('retweeted_status')
            )

            interaction_scores = {entry['user_id']: calculate_interaction_score(entry['reply_count'], entry['retweet_count']) for entry in interaction_counts}

            hashtag_counts = defaultdict(int)
            for tweet in valid_tweets:
                for tag in tweet.hashtags:
                    if tag['text'].lower() == hashtag:
                        hashtag_counts[tweet.user_id] += 1

            hashtag_scores = {user_id: calculate_hashtag_score(count) for user_id, count in hashtag_counts.items()}

            keyword_counts = defaultdict(int)
            if type_ in ['reply', 'both']:
                reply_tweets = valid_tweets.filter(in_reply_to_user_id__isnull=False)
                for tweet in reply_tweets:
                    if phrase in tweet.text:
                        keyword_counts[tweet.user_id] += tweet.text.count(phrase)
                    if hashtag in [tag['text'].lower() for tag in tweet.hashtags]:
                        keyword_counts[tweet.user_id] += 1

            if type_ in ['retweet', 'both']:
                retweet_tweets = valid_tweets.filter(retweeted_status__isnull=False)
                for tweet in retweet_tweets:
                    if phrase in tweet.text:
                        keyword_counts[tweet.user_id] += tweet.text.count(phrase)
                    if hashtag in [tag['text'].lower() for tag in tweet.hashtags]:
                        keyword_counts[tweet.user_id] += 1

            keyword_scores = {user_id: calculate_keywords_score(count) for user_id, count in keyword_counts.items()}

            final_scores = {}
            for user_id in set(interaction_scores.keys()).union(set(hashtag_scores.keys())).union(set(keyword_scores.keys())):
                interaction_score = interaction_scores.get(user_id, 0)
                hashtag_score = hashtag_scores.get(user_id, 1)
                keywords_score = keyword_scores.get(user_id, 0)
                final_score = interaction_score * hashtag_score * keywords_score
                if final_score > 0:
                    final_scores[user_id] = final_score

            response_data = []
            for user_id in sorted(final_scores, key=final_scores.get, reverse=True):
                try:
                    user = User.objects.get(user_id=user_id)
                    contact_tweet = Tweet.objects.filter(user_id=user_id).latest('created_at')
                    response_data.append({
                        'user_id': user.user_id,
                        'screen_name': user.screen_name,
                        'description': user.description,
                        'contact_tweet_text': contact_tweet.text
                    })
                except User.DoesNotExist:
                    continue

            cache.set(cache_key, response_data, CACHE_TIMEOUT)
        except Exception as e:
            logger.error(f"Error processing user recommendation: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    return JsonResponse({
        'TEAMID': 'YourTeamID',
        'TEAM_AWS_ACCOUNT_ID': 'YourAWSAccountID',
        'recommendations': response_data
    })