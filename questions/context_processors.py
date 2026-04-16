from .views import QUESTIONS  

def all_tags_processor(request):
    all_tags = []
    for q in QUESTIONS:
        all_tags.extend(q.get('tags', []))
    
    unique_tags = sorted(list(set(all_tags)))
    
    return {
        'global_unique_tags': unique_tags
    }