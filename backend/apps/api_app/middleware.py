from django.middleware.csrf import CsrfViewMiddleware


class StrictApiCsrfMiddleware:
    """对 Ninja API 补一层 Django 原生 CSRF 校验。

    当前环境里的 django-ninja 版本没有 `NinjaAPI(csrf=True)` 参数。
    这里不重新实现 CSRF 规则，只复用 Django 自带的 CsrfViewMiddleware，
    保证 `/api/` 下的写操作仍然必须带合法 CSRF token。
    """

    unsafe_methods = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response
        self.csrf = CsrfViewMiddleware(get_response)

    def __call__(self, request):
        if (
            request.path.startswith("/api/")
            and request.path != "/api/csrf"
            and request.method in self.unsafe_methods
        ):
            response = self.csrf.process_view(request, lambda *_: None, (), {})
            if response is not None:
                return response
        return self.get_response(request)
