from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task, between
import json
import random
from testinfo import *


class UserBehavior( TaskSet):
    #*********************************USERS*********************************
    #create new user account
    @task(10)
    def create_account(self):
        if len(USER_CREDENTIALS) > 0:
            newUser = USER_CREDENTIALS.pop()
            ACTIVE_USERS.add(newUser)
            self.client.post("/user/register",data= {
              "email":newUser[0],
              "username":newUser[1],
              "password":newUser[2],
              "karma":0
            },
            headers=HEADERS,
            name = "Create new user")
    #test duplicate user
    @task(1)    
    def create_duplicate_account(self):
        #test for duplicate
        if len(ACTIVE_USERS) > 1:
            dupUser = ACTIVE_USERS.pop()
            with self.client.post("/user/register",data= {
                "email":dupUser[0],
                "username":dupUser[1],
                "password":dupUser[2],
                "karma":0
                },
                headers=HEADERS,
                name = "Create Duplicate user",
                catch_response=True) as res:
                if res.status_code == 409:
                    res.success()
                else:
                    res.failure('Duplicate User should fail: '+res.text)
            ACTIVE_USERS.add(dupUser)

    @task(10)
    def decrement_karma(self):
        if (len(ACTIVE_USERS) > 0):
            user = ACTIVE_USERS.pop()
            self.client.put("/user/sub_karma",data= {
            "username":user[1]
            },
            headers=HEADERS,
            name = "Decrement karma user")
            ACTIVE_USERS.add(user)
    @task(1)
    def decrement_karma_not_found(self):
        with self.client.put("/user/sub_karma",data= {
            "username":"InvalidUsername"
        },
        headers=HEADERS,
        name = "Decrement karma user not found",
        catch_response=True) as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure("Invalid User should not be found: "+res.text)

    @task(20)
    def increment_karma(self):
        if (len(ACTIVE_USERS) > 0):
            user = ACTIVE_USERS.pop()
            self.client.put("/user/add_karma",data= {
            "username":user[1]
            },
            headers=HEADERS,
            name = "Increment karma user")
            ACTIVE_USERS.add(user)
    @task(1)
    def increment_karma_not_found(self):
        with self.client.put("/user/add_karma",data= {
        "username":"invalid_username"
        },
        headers=HEADERS,
        name = "Increment karma user not found",
        catch_response=True) as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure("Invalid User should not be found: "+res.text)
    @task(5)
    def update_email(self):
        if (len(ACTIVE_USERS) > 0):
            user = ACTIVE_USERS.pop()
            self.client.put("/user/update_email",data= {
            "username":user[1],
            "email":"new_"+str(user[0])
            },
            headers=HEADERS,
            name = "Update email")
            ACTIVE_USERS.add(("new_"+str(user[0]),user[1],user[2]))
    @task(1)
    def update_email_not_found(self):
        with self.client.put("/user/update_email",data= {
        "username": "InvalidUser"+str(random.randint(1,1000)),
        "email":"InvalidEmail"+str(random.randint(1,1000))
        },
        headers=HEADERS,
        name = "Update email not found",
        catch_response=True) as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure("Invalid User should not be found: "+res.text)

    #*********************************POSTING*********************************
    @task(20)
    def create_post(self):
        if (len(ACTIVE_USERS) > 0):
            user = ACTIVE_USERS.pop()
            post = POSTS.pop()
            r = random.sample( SUBREDDITS, 1 )[0]
            with self.client.post("/posts/make_post",data= {
            "title":post[0],
            "text":post[1],
            "subreddit":r[0],
            "username":user[1]
            },
            headers=HEADERS,
            name = "Create new post",
            catch_response=True) as res:
                if( res.status_code == 201 ):
                    jsonData = res.json()
                    if len(jsonData) > 0:
                        postID = jsonData["postID"]
                        ACTIVE_POSTS.add((postID,r[0],user[1]))
            ACTIVE_USERS.add(user)
            POSTS.add(post)

    @task(1)
    def create_post_not_found(self):
        post = POSTS.pop()
        r = random.sample( SUBREDDITS, 1 )
        with self.client.post("/posts/make_post",data= {
            "title":post[0],
            "text":post[1],
            "subreddit":r[0],
            "username":"InvalidUser"+ str(random.randint(1,100))
        },
        headers=HEADERS,
        name = "Create new post user not found",
        catch_response=True) as res:
            if res.status_code == 409:
                res.success()
            else:
                res.failure("New post with inavlid user should fail: "+ res.text)

        POSTS.add(post)

    @task(1)
    def delete_post(self):
        if (len(ACTIVE_POSTS)>0):
            post = ACTIVE_POSTS.pop()
            
            self.client.delete("/posts/remove_post/"+str(post[0]),
            headers=HEADERS,
            name = "Delete post")
    @task(1)
    def delete_post_not_found(self):
        with self.client.delete("/posts/remove_post/invalid"+str(random.randint(1,100)),
        headers=HEADERS,
        name = "Delete post Not Found",
        catch_response=True) as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure("Delete Post should not be found: "+ res.text)

    @task(10)
    def retrieve_posts(self):
        if len(ACTIVE_POSTS) > 0:
            post = random.sample( ACTIVE_POSTS, 1 )[0]
            endpoint = "/posts/retrieve_post/"+str( post[0] )
            self.client.get(endpoint,
            headers=HEADERS,
            name = "Retrieve post")
    
    @task(1)
    def retrieve_posts_not_found(self):
        with self.client.get("/posts/retrieve_post/invalid"+str( random.randint( 0, 200 ) ),
        headers=HEADERS,
        name = "Retrieve post not found",
        catch_response=True) as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure("Invalid post ID should not be found: "+res.text)

    @task(10)
    def get_sub_posts(self):
        if len( ACTIVE_POSTS ) > 0:
            post = random.sample( ACTIVE_POSTS, 1 )[0]
            url = "/posts/list_post_sub/"+str( post[1] )+"/"
            self.client.get(
                url,
                headers=HEADERS,
                name="Get SubReddit Posts"
            )

    @task(5)
    def get_all_posts(self):
        self.client.get(
            "/posts/list_all_posts/",
            headers=HEADERS,
            name="Get All Posts"
        )

#*******************************VOTING*********************************************
    @task(10)
    def get_posts_votes(self):
        if len( ACTIVE_POSTS ) > 0:
            post = random.sample( ACTIVE_POSTS, 1 )[0]
            url = "/voting/post_votes/"+str( post[0] )
            self.client.get(
                url,
                headers=HEADERS,
                name="Get Posts Votes"
            )
    
    @task(1)
    def get_posts_votes_not_found(self):
        with self.client.get(
            "/voting/post_votes/99999999"+str( random.randint( 1, 100 ) ),
            headers=HEADERS,
            name="Get Post votes not found",
            catch_response=True
        ) as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure(res.text)

    @task(20)
    def upvote_posts(self):
        if len( ACTIVE_POSTS ) > 0:
            post = random.sample( ACTIVE_POSTS, 1 )[0]
            url = "/voting/upvote/"+str( post[0] )
            self.client.put(
                url,
                headers=HEADERS,
                name="Upvote Post"
            )

    @task(1)
    def upvote_posts_not_found(self):
        url = "/voting/upvote/99999999"+str( random.randint( 1, 100 ) )
        with self.client.put(
            url,
            headers=HEADERS,
            name="Upvote Post not found",
            catch_response=True
        )as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure(res.text)

    @task(20)
    def downvote_posts(self):
        if len( ACTIVE_POSTS ) > 0:
            post = random.sample( ACTIVE_POSTS, 1 )[0]
            url = "/voting/downvote/"+str( post[0] )
            self.client.put(
                url,
                headers=HEADERS,
                name="Downvote Post"
            )

    @task(1)
    def downvote_posts_not_found(self):
        url = "/voting/downvote/99999999"+str( random.randint( 1, 100 ) )
        with self.client.put(
            url,
            headers=HEADERS,
            name="Downvote Post not found",
            catch_response=True
        )as res:
            if res.status_code == 404:
                res.success()
            else:
                res.failure(res.text)
                
    @task(5)
    def get_top_posts(self):
        url = "/voting/list_top_posts/"
        self.client.get(
            url,
            headers=HEADERS,
            name="Get all Posts"
        )

    @task(10)
    def get_score_list(self):
        if len( ACTIVE_POSTS ) > 5:
            posts = random.sample( ACTIVE_POSTS, random.randint(2,5) )  
            params=set()
            for p in posts:
                params.add(str(p[0]))
            params = ",".join(params)
            url = "/voting/score_list/"+ params
            self.client.get(
                url,
                headers=HEADERS,
                name="Get Score List"
            )

    @task(20)
    def send_message(self):
        if len(ACTIVE_USERS) > 2:
            url = "/message/send_message"
            users = random.sample( ACTIVE_USERS, 2)
            with self.client.post(
                url,
                headers=HEADERS,
                data = {
                    "sender":users[0][1],
                    "receiver":users[1][1],
                    "content":"Message"+str(random.randint(100,999))
                },
                name="Send Message",
                catch_response=True
            ) as res:
                if( res.status_code == 201 ):
                    jsonData = res.json()
                    if len(jsonData) > 0:
                        messageID = jsonData["messageID"]
                        ACTIVE_MESSAGES.add(messageID)

    @task(5)
    def delete_message(self):
        if len(ACTIVE_MESSAGES) > 0:
            messageID = ACTIVE_MESSAGES.pop()
            url = "/message/remove_message/" + str(messageID)
            self.client.delete(
                url,
                headers=HEADERS,
                name="Delete Message"
            )

    @task(5)
    def favorite_message(self):
        if len(ACTIVE_MESSAGES) > 0:
            messageID = random.sample(ACTIVE_MESSAGES, 1)[0]
            url = "/message/favorite_message/" + str(messageID)
            self.client.put(
                url,
                headers=HEADERS,
                name="Favorite Message"
            )


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(2,5)