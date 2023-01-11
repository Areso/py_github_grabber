# py_github_grabber
Allows you to download data about your public repos and track it

## Rate Limit info
Github Rate Limit Brief Overview  
We will quickly go over the specific rate limits for Github's REST APIs and some useful information to remember as well.  
```
    Unauthenticated Requests: 60 requests/hr
    Authenticated User Requests: 5000 requests/hr
```
To check current limit `curl -I https://api.github.com/users/Areso`  
403 means the limit is depleted  
200 means the limit is still valid  
To check current limit with token `curl -I -H "Authorization: Bearer your_token_here" https://api.github.com/users/Areso`   
This project could work without authentication, only for users with small amount of repos (<50).  

More information could be found there: https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting  
The token could be obtained here https://github.com/settings/tokens (Settings->Developer Settings->Personal Access Token)  
Here, the checkboxes:  
```
    repo-|
     v   |--repo:status 
     v   |--public_repo
     v   |--security_events
    
     v   |--read:packages
    
     v   |--read:org

v   user-|

     v   |--read:discussion

     v   |--read:project
```
I decided it's pretty safe to make this one with no expiration date 