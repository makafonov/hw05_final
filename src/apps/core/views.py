from django.shortcuts import render


_HTTP404 = 404
_HTTP500 = 500


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=_HTTP404,
    )


def server_error(request):
    return render(request, 'misc/500.html', status=_HTTP500)
