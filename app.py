from datetime import datetime
import os
import pytz
from pytz import timezone
import request
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'logs.db')
db = SQLAlchemy(app)
mar = Marshmallow(app)

def get_time():
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstTime = date
    return pstTime

# create a class for the user
# holds their information
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    karma = Column(Integer, default=0)
    createtime = Column(DateTime, default=get_time())
    changetime = Column(DateTime, default=get_time())

# create a class for posts
# holds information for posts
class Post(db.Model):
    _table_name = 'post'
    postID = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False)
    title = Column(String(120), nullable=False)
    text = Column(String(500), nullable=False)
    subreddit = Column(String(20), nullable=False)
    createtime = Column(DateTime, default=get_time())
    changetime = Column(DateTime, default=get_time())

    # this function is used to list out the variables without manually returning them all
    # just reference this function to output everything
    def serialize(self):
        return {
            "postID": self.postID,
            "username": self.username,
            "title": self.title,
            "text": self.text,
            "subreddit": self.subreddit,
            "createtime": self.createtime,
            "changetime": self.changetime
        }

# create a class for votes
# holds information for votes
class Votes(db.Model):
    _table_name = 'votes'
    postID = Column(Integer, primary_key=True, autoincrement=True)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    def total_votes(self):
            return {
                "upvotes": self.upvotes,
                "downvotes": self.downvotes
            }

# create a class for messaging
# holds information for messaging
class Message(db.Model):
    _table_name = 'message'
    messageID = Column(Integer, primary_key=True, autoincrement=True, unique=True,)
    user_from = Column(String(20), nullable=False)
    user_to = Column(String(20), nullable=False)
    content = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=get_time())
    flag = Column(Integer, nullable=False, default=0)


# schema for Users
class UserData(mar.Schema):
    class Data:
        fields = ('id', 'username', 'email', 'password', 'karma', 'createtime', 'changetime')

# schema for posts
class PostData(mar.Schema):
    class Data:
        fields = ('id', 'username', 'title', 'text', 'subreddit', 'createtime', 'changetime')

# schema for votes
class VotesData(mar.Schema):
    class Data:
        fields = ('id', 'upvotes', 'downvotes')

# schema for messaging
class MessageData(mar.Schema):
    class Data:
        fields = ('id', 'from', 'to', 'content', 'timestamp', 'flag')


userdata = UserData()
usermultdata = UserData(many=True)

postdata = PostData()
postmultdata = PostData(many=True)

votedata = VotesData()
votemultdata = VotesData(many=True)

messagedata = MessageData()
messagemultdata = MessageData(many=True)

@app.cli.command('create_db')
def create_db():
    db.create_all()
    print('created a database')


@app.cli.command('drop_db')
def drop_db():
    db.drop_all()
    print('dropped the db')


@app.cli.command('seed_db')
def seed_db():
    post = Post(username='FrancisNguyen', title="CSUF goes virtual after coronavirus outbreak",
                text="Most of the classes will go on zoom", subreddit="CSUF")
    db.session.add(post)

    test = User(username='FrancisNguyen', email="test@gmail.com", password='testpass', karma=12)
    db.session.add(test)

    test2 = User(username='u2', email="test2@gmail.com", password='testpass2', karma=10)
    db.session.add(test2)

    vote = Votes(upvotes=5, downvotes=2)
    db.session.add(vote)

    message = Message(user_from='FrancisNguyen', user_to='u2', content='hey wassup')
    db.session.add(message)

    db.session.commit()

    print('DB seeded')


@app.route('/')
def index():
    return 'Hello\n', 200

#*******************************************USERS*******************************************
# Register users
@app.route('/v1/api/user/register', methods=['POST'])
def register():
    email = request.form['email']
    username = request.form['username']
    regis = User.query.filter_by(email=email).first() and User.query.filter_by(username=username).first()
    if regis:
        return jsonify(message='Email or Username Already exists'), 409
    else:
        username = request.form['username']
        password = request.form['password']
        karma = request.form['karma']
        createtime = get_time()
        changetime = get_time()
        user = User(username=username, email=email, password=password,
                    karma=karma, createtime=createtime, changetime=changetime)
        db.session.add(user)

        db.session.commit()
        return jsonify(message='User created'), 201

# increment karma
@app.route('/v1/api/user/add_karma', methods=['PUT'])
def add_karma():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user:
        user.karma += 1
        db.session.commit()
        return jsonify(message='Added karma'), 202
    else:
        return jsonify('Could not add karma'), 404

# decrement karma
@app.route('/v1/api/user/sub_karma', methods=['PUT'])
def sub_karma():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user:
        user.karma -= 1
        db.session.commit()
        return jsonify(message='Subtracted karma!'), 202
    else:
        return jsonify('Could not subtract karma'), 404

# update user's email
@app.route('/v1/api/user/update_email', methods=['PUT'])
def update_email():
    username = request.form['username']
    users = User.query.filter_by(username=username).first()
    if users:
        users.email = request.form['email']
        users.createtime = get_time()
        db.session.commit()
        return jsonify(message='Email updated'), 202
    else:
        return jsonify('This user does not exist'), 404

# delete user's account
@app.route('/v1/api/user/deactivate_acc/<string:username>', methods=['DELETE'])
def deactivate_account(username: str):
    username = User.query.filter_by(username=username).first()
    if username:
        db.session.delete(username)
        db.session.commit()
        return jsonify(message="deleted a user"), 202
    else:
        return jsonify(message="User doesn't exist"), 404

#*******************************************POSTING*******************************************
# create a post
@app.route('/v1/api/posts/make_post', methods=['POST'])
def make_post():
    username = request.form['username']
    makep = User.query.filter_by(username=username).first()
    if makep:
        username = request.form['username']
        title = request.form['title']
        text = request.form['text']
        subreddit = request.form['subreddit']
        createtime = get_time()
        changetime = get_time()
        post = Post(username=username, title=title, text=text, subreddit=subreddit,
                    createtime=createtime, changetime=changetime)
        vote = Votes(upvotes=1, downvotes=0)
        db.session.add(post)
        db.session.add(vote)
        db.session.commit()
        return jsonify(message='Post created', postID=post.postID), 201
    else:
        return jsonify(message='Username does not exist'), 409

# delete a post
@app.route('/v1/api/posts/remove_post/<int:pid>', methods=['DELETE'])
def delete_post(pid: int):
    post = Post.query.filter_by(postID=pid).first()
    vote = Votes.query.filter_by(postID=pid).first()
    if post:
        db.session.delete(post)
        db.session.delete(vote)
        db.session.commit()
        return jsonify(message="Deleted a post"), 202
    else:
        return jsonify(message="Post does not exist"), 404

# retrieve a post
@app.route('/v1/api/posts/retrieve_post/<int:pid>', methods=['GET'])
def get_post(pid: int):
    post = Post.query.filter_by(postID=pid).first()
    if post:
        # references serialize() to list out all fields
        return jsonify(post.serialize())
    else:
        return jsonify(message="Post does not exist"), 404

# list posts by subreddit
@app.route('/v1/api/posts/list_post_sub/<string:subreddit>/', methods=['GET'])
def list_post_sub(subreddit: str):
    # create amount argument to pass into the limit() function
    amount = request.args.get('amount')
    posts = db.session.query(Post).filter_by(subreddit=subreddit).order_by(Post.createtime.desc()).limit(amount)
    if posts:
        # serializes every variable in posts and returns them
        return jsonify(posts=[i.serialize() for i in posts])
    else:
        return jsonify(message="Post does not exist"), 404

# list all posts
@app.route('/v1/api/posts/list_all_posts/', methods=['GET'])
def list_all_posts():
    # create amount argument to pass into the limit() function
    amount = request.args.get('amount')
    listposts = db.session.query(Post).order_by(Post.createtime.desc()).limit(amount)
    return jsonify(listposts=[i.serialize() for i in listposts])

#*******************************************VOTING*******************************************
# Report the number of upvotes and downvotes for a post
@app.route('/v1/api/voting/post_votes/<int:pid>', methods=['GET'])
def get_post_votes(pid: int):
    post = Votes.query.filter_by(postID=pid).first()
    if post:
        return jsonify(post.total_votes())
    else:
        return jsonify(message="Post does not exist"), 404

# Upvote a post
@app.route('/v1/api/voting/upvote/<int:pid>', methods=['PUT'])
def upvote(pid: int):
    post = Votes.query.filter_by(postID=pid).first()
    if post:
        post.upvotes += 1
        db.session.commit()
        return jsonify(message='Upvoted post'), 202
    else:
        return jsonify('Could not upvote post'), 404

# Downvote a post
@app.route('/v1/api/voting/downvote/<int:pid>', methods=['PUT'])
def downvote(pid: int):
    post = Votes.query.filter_by(postID=pid).first()
    if post:
        post.downvotes += 1
        db.session.commit()
        return jsonify(message='Downvoted post'), 202
    else:
        return jsonify('Could not downvote post'), 404

# List the n top-scoring posts to any community
@app.route('/v1/api/voting/list_top_posts/', methods=['GET'])
def top_posts():
    # create amount argument to pass into the limit() function
    amount = request.args.get('amount')
    #ordered list of vote objects
    vote_order = db.session.query(Votes).order_by((Votes.upvotes-Votes.downvotes).desc()).limit(amount)

    #get post data
    listposts=[]
    for i in vote_order:
            post = Post.query.filter_by(postID=i.postID).first()
            if post:
                # references serialize() to list out all fields
                listposts.append(post.serialize())
    return jsonify(listposts)

# Given a list of post identifiers, return the list sorted by score.
@app.route('/v1/api/voting/score_list/<string:pid>', methods=['GET'])
def score_list(pid: str):
    #get int list
    posts = [int(x) for x in pid.split(',')]
    # create amount argument to pass into the limit() function
    print(posts)
    amount = request.args.get('amount')
    #ordered list of vote objects
    vote_order = db.session.query(Votes).filter(Votes.postID.in_(posts)).order_by((Votes.upvotes-Votes.downvotes).desc()).limit(amount)
    print(vote_order)

    #get post data
    listposts=[]
    for i in vote_order:
            post = Post.query.filter_by(postID=i.postID).first()
            if post:
                # references serialize() to list out all fields
                listposts.append(post.serialize())
    return jsonify(listposts)

#*******************************************MESSAGING*******************************************

# send message
@app.route('/v1/api/message/send_message', methods=['POST'])
def send():
    sender = request.form['sender']
    receiver = request.form['receiver']

    sender_q = User.query.filter_by(username=sender).first()
    receiver_q = User.query.filter_by(username=receiver).first()

    if sender_q and receiver_q:
        content = request.form['content']
        timestamp = get_time()

        message = Message(user_from=sender, user_to=receiver, content=content, timestamp=timestamp, flag=0)
        db.session.add(message)

        db.session.commit()
        return jsonify(message='Message created', messageID=message.messageID), 201
    else:
        return jsonify(message='Sender or receiver does not exist'), 409


# delete message
@app.route('/v1/api/message/remove_message/<int:mid>', methods=['DELETE'])
def delete_message(mid: int):
    message = Message.query.filter_by(messageID=mid).first()
    if message:
        db.session.delete(message)
        db.session.commit()
        return jsonify(message="Deleted a message"), 202
    else:
        return jsonify(message="Message does not exist"), 404

# favorite message
@app.route('/v1/api/message/favorite_message/<int:mid>', methods=['PUT'])
def favorite_message(mid: int):
    message = Message.query.filter_by(messageID=mid).first()
    if message:
        message.flag = 1
        db.session.commit()
        return jsonify(message="Favorited a message"), 201
    else:
        return jsonify(message="Message does not exist"), 404

if __name__ == '__main__':
    app.run()
