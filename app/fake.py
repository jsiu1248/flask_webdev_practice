from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Composition
from random import randint
import string

def users(count=20):
    """Creating users with fake data
    args: count of how many users needed"""

    # an instance of Faker is called and below are many of their functions with different types of fake data
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 bio=fake.text(),
                 last_seen=fake.past_date())
        db.session.add(u)

        # trying to commit data, but if it is a duplicate then it rollbacks
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def compositions(count=100):
    """Function that creates fake composition
        args: create a certain amount of compositions"""
    fake = Faker()

    # checking how many users are in the table
    user_count = User.query.count()
    for i in range(count):
        # offset dicards a certain number of results, n is a random number between 0 and then user_count -1
        # so it is picking a random user and don't care about duplicated users because users can have multiple compositions
        u = User.query.offset(randint(0, user_count - 1)).first()
        c = Composition(release_type=randint(0,2),

        # bs generates cool sounding titles
                        title=string.capwords(fake.bs()),
                        description=fake.text(),
                        timestamp=fake.past_date(),
                        artist=u)
        db.session.add(c)
    db.session.commit()

    # you can use the shell to create more fake users in the dev environment