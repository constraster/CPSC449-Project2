HEADERS = {'content-type': 'application/x-www-form-urlencoded'}
USER_CREDENTIALS = set()
ACTIVE_USERS=set()
INACTIVE_USERS=set()
ACTIVE_POSTS=set()
ACTIVE_MESSAGES=set()
POSTS=set()
SUBREDDITS=set()
for i in range(1,10000):
    USER_CREDENTIALS.add(("TestEmail"+str(i).zfill(5)+"@example.com","TestUsername"+str(i).zfill(5), "TestPassword"+str(i).zfill(5)))
for i in range(1,1000000):
    POSTS.add(("TestTitle"+str(i).zfill(7),"TestBody"+str(i).zfill(7)))
for i in range(1,200):
    SUBREDDITS.add(("Subreddit_"+str(i).zfill(3),))