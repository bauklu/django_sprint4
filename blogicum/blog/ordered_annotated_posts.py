from django.db.models import Count


def get_ordered_annotated_posts(posts):
    return posts.order_by('-pub_date').annotate(
        comment_count=Count('comments'))
