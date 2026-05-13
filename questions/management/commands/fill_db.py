import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike
from core.models import Profile
from faker import Faker
from django.db.models import Subquery, OuterRef, Count
from django.db.models.functions import Coalesce

fake = Faker()

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        self.ratio = options['ratio']

        with transaction.atomic():
            self.stdout.write("Начало генерации данных...")
            
            users = self._create_users()
            tags = self._create_tags()
            
            user_ids = [u.id for u in users]
            tag_ids = [t.id for t in tags]
            
            question_ids = self._create_questions(user_ids, tag_ids)
            self._create_answers(user_ids, question_ids)
            answer_ids = list(Answer.objects.values_list('id', flat=True))
            self._create_likes(user_ids, question_ids, answer_ids)
            self.update_likes_and_answer_count()

        self.stdout.write(self.style.SUCCESS(f'База успешно наполнена! (ratio={self.ratio})'))

    def _create_users(self):
        self.stdout.write(f"Создание {self.ratio} пользователей...")
        hashed_pw = make_password('password123')
        users_to_create = [
            User(
                username=f"{fake.unique.user_name()}_{i}",
                email=f"user_{i}_{fake.unique.email()}",
                password=hashed_pw
            ) for i in range(self.ratio)
        ]
        created_users = User.objects.bulk_create(users_to_create)

        profiles = [
            Profile(user=user) for user in created_users
        ]
        Profile.objects.bulk_create(profiles)
        return created_users

    def _create_tags(self):
        self.stdout.write(f"Создание {self.ratio} тегов...")
        tags = [Tag(name=f"{fake.word()}_{i}") for i in range(self.ratio)]
        return Tag.objects.bulk_create(tags)

    def _create_questions(self, user_ids, tag_ids):
        count = self.ratio * 10
        chunk_size = 5000
        question_ids = []
        QuestionTag = Question.tags.through
        
        self.stdout.write(f"Создание {count} вопросов...")
        for i in range(0, count, chunk_size):
            current_size = min(chunk_size, count - i)
            
            batch = [
                Question(
                    author_id=random.choice(user_ids),
                    title=fake.text(max_nb_chars=80)[:-1],
                    content=fake.text(max_nb_chars=500),
                ) for _ in range(current_size)
            ]
            created = Question.objects.bulk_create(batch)
            
            m2m_batch = []
            for q in created:
                question_ids.append(q.id)
                chosen_tags = random.sample(tag_ids, random.randint(2, 5))
                for t_id in chosen_tags:
                    m2m_batch.append(QuestionTag(question_id=q.id, tag_id=t_id))
            
            QuestionTag.objects.bulk_create(m2m_batch, ignore_conflicts=True)
            
        return question_ids

    def _create_answers(self, user_ids, question_ids):
        count = self.ratio * 100
        chunk_size = 10000 
        self.stdout.write(f"Создание {count} ответов...")
        text_pool = [fake.text(max_nb_chars=200) for _ in range(200)]

        for i in range(0, count, chunk_size):
            current_size = min(chunk_size, count - i)

            ans_batch = [
                Answer(
                    author_id=random.choice(user_ids),
                    related_question_id=random.choice(question_ids),
                    content=random.choice(text_pool),
                    is_correct=(random.random() < 0.25)
                ) for _ in range(current_size)
            ]
            Answer.objects.bulk_create(ans_batch)

            # if (i + chunk_size) % 50000 == 0 or i + current_size == count:
            #     self.stdout.write(f"Прогресс: {i + current_size} / {count}")

    def _create_likes(self, user_ids, question_ids, answer_ids):
                count = self.ratio * 100
                chunk_size = 10000
                self.stdout.write(f"Создание по {count} лайков для ответов и вопросов...")
                for i in range(0, count, chunk_size):
                    current_size = min(chunk_size, count - i)

                    q_likes = [
                        QuestionLike(
                            user_id=random.choice(user_ids),
                            question_id=random.choice(question_ids),
                            is_like=(random.random() > 0.5)
                        ) for _ in range(current_size)
                    ]
                    QuestionLike.objects.bulk_create(q_likes, ignore_conflicts=True)

                    ans_likes = [
                        AnswerLike(
                            user_id=random.choice(user_ids),
                            answer_id=random.choice(answer_ids),
                            is_like=(random.random() > 0.5)
                        ) for _ in range(current_size)
                    ]
                    AnswerLike.objects.bulk_create(ans_likes, ignore_conflicts=True)  

    def update_likes_and_answer_count(self):
        self.stdout.write("Считаем лайки, ответы и статистику профилей...")

        ans_likes = AnswerLike.objects.filter(answer=OuterRef('pk'), is_like=True).values('answer').annotate(c=Count('*')).values('c')
        ans_dislikes = AnswerLike.objects.filter(answer=OuterRef('pk'), is_like=False).values('answer').annotate(c=Count('*')).values('c')
        
        Answer.objects.update(
            rating=Coalesce(Subquery(ans_likes), 0) - Coalesce(Subquery(ans_dislikes), 0)
        )

        q_likes = QuestionLike.objects.filter(question=OuterRef('pk'), is_like=True).values('question').annotate(c=Count('*')).values('c')
        q_dislikes = QuestionLike.objects.filter(question=OuterRef('pk'), is_like=False).values('question').annotate(c=Count('*')).values('c')
        q_ans_count = Answer.objects.filter(related_question=OuterRef('pk')).values('related_question').annotate(c=Count('*')).values('c')

        Question.objects.update(
            rating=Coalesce(Subquery(q_likes), 0) - Coalesce(Subquery(q_dislikes), 0),
            answers_count=Coalesce(Subquery(q_ans_count), 0)
        )

        tag_questions_count = Question.objects.filter(tags=OuterRef('pk')).values('tags').annotate(c=Count('*')).values('c')
        
        Tag.objects.update(
            question_count=Coalesce(Subquery(tag_questions_count), 0)
        )

        prof_q_count = Question.objects.filter(author=OuterRef('user')).values('author').annotate(c=Count('*')).values('c')

        prof_a_count = Answer.objects.filter(author=OuterRef('user')).values('author').annotate(c=Count('*')).values('c')

        Profile.objects.update(
            questions_count=Coalesce(Subquery(prof_q_count), 0),
            answers_count=Coalesce(Subquery(prof_a_count), 0)
        )
