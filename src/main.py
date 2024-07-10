"""The main file that should be run to execute the app. To run: uvicorn  src.main:app --reload"""
import sys
import os

sys.path.append(os.path.join(sys.path[0], 'src'))

from fastapi import FastAPI, Request
from posts.router import router_posts, Validate_Post_Text
from auth.router import router_auth


tags_metadata = [
    {
        "name": "Auth",
        "description": "The block to manage a user's authorization",
    },
    {
        "name": "Posts",
        "description": "The block to manage the user's posts",
    },
]

app = FastAPI(openapi_tags=tags_metadata)



#the routers for Login and Signup
app.include_router(router_auth)  


#Implement request validation to limit the size of the payload for the AddPost endpoint
@app.middleware("http")
async def CheckPostSize(request: Request, call_next):
    return await Validate_Post_Text(request, call_next)
    

#the routers for GetPosts, AddPost and DeletePost
app.include_router(router_posts)  

@app.get("/")
async def read_root(request: Request):
    return {"message": "Open '{}docs' in order to read the endpoints documentation".format(request.base_url)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)