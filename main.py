from fastapi import FastAPI
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.hashing import Hash
from fastapi import FastAPI, HTTPException, Depends, Request,status
from auth.oauth import get_current_user
from auth.jwttoken import create_access_token
from fastapi.middleware.cors import CORSMiddleware
from database.models import User,Post,Likes
from bson.objectid import ObjectId
from config import collection,collection_user,collection_likes
from typing import Optional
app=FastAPI()




#------------------------------------------------------------------Authentication---------------------------------------------------------------------------

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root(current_user:User = Depends(get_current_user)):
	return {"data":"Hello OWrld",'user':current_user}



@app.post('/register')
def create_user(request:User):
	try:
		hashed_pass = Hash.bcrypt(request.password)
		user_object = dict(request)
		user = collection_user.find_one({"username":user_object['username']})
		if user:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail = f'Username Alreday Exists')
		user_object["password"] = hashed_pass
		user = collection_user.insert_one(user_object)
		print(user)
		return {"res":"created"}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail = str(e))


@app.post('/login')
def login(request:OAuth2PasswordRequestForm = Depends()):
	try:

		user = collection_user.find_one({"username":request.username})
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'No user found with this {request.username} username')
		if not Hash.verify(user["password"],request.password):
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Wrong Username or password')
		access_token = create_access_token(data={"sub": user["username"] })
		return {"access_token": access_token, "token_type": "bearer"}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail = str(e))



#---------------------------------------------------------------------Blog Posts--------------------------------------------------------------------------------

@app.post('/blog')
def create_blog(request:Post,current_user:User = Depends(get_current_user)):
	try:
		if not current_user.username:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Required Login')
		blog_object=dict(request)
		user = collection_user.find_one({"username":current_user.username})
		blog_object['owner_id']=user['_id']
		blog=collection.insert_one(blog_object)
		print(blog)
		return {"res":"blog has been created"}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail = str(e))

@app.post('/blog/{post_id}/update')
def update_blog(post_id:str,request:Post,current_user:User = Depends(get_current_user)):
	try:
		if not current_user.username:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Required Login')
		id= ObjectId(post_id)
		blog=collection.find_one({'_id':id})
		#print(blog,id,dict(request))
		if not blog:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Post does not exists')
		update_to=dict(request)
		for key,value in update_to.items():
			if  value is None:
				update_to[key]=blog[key]
		updated_blog=collection.update_one({"_id":id},{"$set":update_to})
		return {"res":"blog has been updated"}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail = str(e))

@app.post('/blog/{post_id}/delete')
def delete_blog(post_id:str,current_user:User = Depends(get_current_user)):
	try:
		if not current_user.username:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Required Login')
		id= ObjectId(post_id)
		blog=collection.find_one({'_id':id})
		if not blog:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Post does not exists')
		
		delete_blog=collection.delete_one({"_id":id})
		return {"res":"blog has been delete"}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail = str(e))


#-------------------------------------------------------------Like Post-------------------------------------------------------------------------

@app.post('/blog/like')
def like_post(request:Likes,current_user:User = Depends(get_current_user)):
	try:
		if not current_user.username:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Required Login')
		print(request)
		id= ObjectId(request.post_id)
		blog=collection.find_one({'_id':id})
		if not blog:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f'Post does not exists')
		user = collection_user.find_one({"username":current_user.username})
		find_likes=collection_likes.find_one({'user_id':user['_id']})
		find=collection_likes.find_one({'user_id':user['_id'],'post_id':id})
		if not find_likes:
			likes_object=dict(request)
			likes_object['post_id']=[likes_object['post_id']]
			likes_object["post_id"][0]=ObjectId(likes_object['post_id'][0])
			likes_object['user_id']=user['_id']
			like=collection_likes.insert_one(likes_object)
		elif find:
			raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail = f'Already Liked this Post')
		else:
			likes_object=dict(request)
			likes_object['post_id']=ObjectId(likes_object['post_id'])
			like=collection_likes.update_one({'_id':find_likes['_id']},{"$push":likes_object})
		return {"res":"liked the post"}
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail = str(e))