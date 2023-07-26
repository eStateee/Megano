from app_goods.models import Reviews


def create_review(user, good, text):
    Reviews.objects.create(user=user, good=good, text=text)
