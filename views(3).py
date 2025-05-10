from django.http import HttpResponse

# Create your views here.
# copied from example sorking to adjust what I need to complete assignment
# https://docs.djangoproject.com/en/4.2/ref/request-response/#django.http.HttpRequest.COOKIES
# HttpResponse.set_cookie(key, value='', max_age=None, expires=None, path='/',
#     domain=None, secure=None, httponly=False, samesite=None)


# https://www.youtube.com/watch?v=Ye8mB6VsUHw

def helloaustin(request) :
    num_visits = request.session.get('num_visits', 0) + 1
    request.session['num_visits'] = num_visits
    if num_visits > 3 : del(request.session['num_visits'])
    resp = HttpResponse('view count='+str(num_visits))
    resp.set_cookie('dj4e_cookie', '4d1e4ae2', max_age=1000)
    return resp