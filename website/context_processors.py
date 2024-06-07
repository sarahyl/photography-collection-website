def user_username_processor(request):
    if request.user.is_authenticated:
        user_username = request.user.username
    else:
        user_username = ""
    return {
        'user_username' : user_username
    }