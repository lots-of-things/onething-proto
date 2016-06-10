import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users

from models.content import Article, Question
from models.vote import Vote
from models.vote import UPVOTE, DOWNVOTE
from models.auth import OUser

class AddVoteHandler(webapp2.RequestHandler):

  def post(self, article_id, vote_type):
    article = Article.get_by_id(int(article_id))

    google_user = users.get_current_user()
    if google_user:
      ouser_key = OUser.key_from_user(google_user)
    if ouser_key:
      # TODO Votes are now being created properly, Add update requests to a pull queue
      if vote_type == 'down':
        vote = Vote.create(article_key=article.key, ouser_key=ouser_key, value=DOWNVOTE)
        article.rating = article.rating - 1.0
      else:
        vote = Vote.create(article_key=article.key, ouser_key=ouser_key, value=UPVOTE)
        article.rating = article.rating + 1.0

      ndb.put_multi([article, vote])

      return self.redirect('/', body="Thanks for your vote!")
    return self.redirect('/', body="Must be logged in to vote.")

  def get(self, article_id, vote_type):
    return self.post(article_id, vote_type)

class AddAnswerHandler(webapp2.RequestHandler):

  def post(self, question_id, ans_type):
    question = Question.get_by_id(int(question_id))

    google_user = users.get_current_user()
    if google_user:
      ouser_key = OUser.key_from_user(google_user)
    if ouser_key:
      question.tries = question.tries + 1
      # TODO Votes are now being created properly, Add update requests to a pull queue
      gotit = False
      if ans_type == 'true':
          if question.answer == True:
              question.correct += question.correct + 1
              gotit = True
          else:
              question.correct += question.correct - 1
      else:
          if question.answer == True:
              question.correct += question.correct - 1
          else:
              question.correct += question.correct + 1
              gotit = True

      return self.redirect('/', body="Thanks for your answer!")
    return self.redirect('/', body="Must be logged in to write answers.")

  def get(self, article_id, vote_type):
    return self.post(article_id, vote_type)

class PopHandler(webapp2.RequestHandler):

  def get(self):
      articles = Article.query(Article.mark==0).order(Article.mark).fetch(1)
      for article in articles:
          article.mark=1
          article.put()
      articles = Article.query(Article.mark<0).order(Article.mark, -Article.rating).fetch(1)
      for article in articles:
          article.mark=0
          article.put()
      return self.redirect('/', body="Popped.")
