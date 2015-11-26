from .model import Posts, Users, Tags
import pickle
import random
import sys

def main():
    min_answers = 2
    test_set_length = 1000

    questions = Posts.select().where((Posts.posttypeid == 1))
    answers = Posts.select().where((Posts.posttypeid == 2))
    users = Users.select()
    tags = Tags.select()
    print questions.count()
    print answers.count()
    print users.count()
    print tags.count()
    return

    all_questions = Posts.select().where(Posts.posttypeid == 1)
    all_questions_accepted_answer = Posts.select().where((Posts.posttypeid == 1) & (Posts.acceptedanswerid.is_null(False)))
    all_questions_answers = Posts.select().where((Posts.posttypeid == 1) & (Posts.answercount >= min_answers))
    print "Count (All questions): " + str(all_questions.count())
    print "Count (All questions with accepted answers): " + str(all_questions_accepted_answer.count())
    print "Count (All questions with answers (min %d): " % min_answers + str(all_questions_answers.count())
    print "Number of samples = {0}".format(test_set_length)

    question_ids = []
    for Post in all_questions_answers:
        question_ids.append(Post.id)

    random.shuffle(question_ids)
    question_ids = question_ids[:test_set_length]
    for questionId in question_ids:
        print("Setting forevaluation for question {0}".format(questionId))
        q = Posts.update(forevaluation = 1).where(Posts.id == questionId)
        q.execute()
   

if __name__ == "__main__":
        main()
