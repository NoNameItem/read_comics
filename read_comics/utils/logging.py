import json
import logging
from functools import wraps, partial

from crum import get_current_user
from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response

SUCCESS = 25


class ReprEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return repr(o)


class Logger(logging.Logger):
    def success(self, msg, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)


def getLogger(name="default"):
    logging.addLevelName(SUCCESS, 'SUCCESS')
    logging.setLoggerClass(Logger)
    return logging.getLogger("read_comics." + name)


class LogUserFilter(logging.Filter):
    def filter(self, record):
        user = get_current_user()
        if user:
            record.username = get_current_user().username
        else:
            record.username = "-"
        return True


def log_value(arg):
    arg_type = type(arg)
    if isinstance(arg, QuerySet):
        arg = {
            "db": arg.db,
            # "query": str(arg.query)
        }
    if isinstance(arg, DRFRequest):
        _resolver_match = arg._request.resolver_match
        if _resolver_match:
            resolver_match = {
                "route": _resolver_match.route,
                "url_name": _resolver_match.url_name,
                "view_name": _resolver_match.view_name,
                "args": _resolver_match.args,
                "kwargs": _resolver_match.kwargs
            }
        else:
            resolver_match = None
        arg = {
            "method": arg._request.method,
            "path": arg._request.path,
            "resolver_match": resolver_match,
            "data": arg.data,
            "has_files": len(arg.FILES) > 0,
            "user": str(arg.user)

        }
    elif isinstance(arg, HttpRequest):
        _resolver_match = arg.resolver_match
        if _resolver_match:
            resolver_match = {
                "route": _resolver_match.route,
                "url_name": _resolver_match.url_name,
                "view_name": _resolver_match.view_name,
                "args": _resolver_match.args,
                "kwargs": _resolver_match.kwargs
            }
        else:
            resolver_match = None
        arg = {
            "method": arg.method,
            "path": arg.path,
            "resolver_match": resolver_match,
            "GET": dict(arg.GET.lists()),
            "POST": dict(arg.POST.lists()),
            "has_files": len(arg.FILES) > 0,
            "user": str(arg.user)

        }
    elif isinstance(arg, TemplateResponse):
        arg = {
            "template_name": arg.template_name,
            "context_data": arg.context_data
        }
    elif isinstance(arg, Response):
        arg = {
            "status_code": arg.status_code,
            "status_text": arg.status_text,
            "content_type": arg.content_type,
            "data": arg.data
        }
    try:
        arg_str = json.dumps(arg, indent=2, ensure_ascii=False, cls=ReprEncoder)
    except TypeError:
        arg_str = repr(arg)
    return arg_str, arg_type


def logged(logger, function_name=None, trace=False, unhandled_error_level=logging.WARNING, **kwargs_dec):
    def decorator(func):
        name = function_name or str(func).split(" ")[1]

        @wraps(func)
        def wrapped(*args, **kwargs):
            logger.info(">>> Starting {0}".format(name))
            for i in range(len(args)):
                arg = args[i]
                arg_str, arg_type = log_value(arg)
                logger.debug(">>> {2} args[{0}]({3}):\n{1}\n".format(i, arg_str, name, arg_type))
            for key, value in kwargs.items():
                arg_str, arg_type = log_value(value)
                logger.debug(">>> {2} {0}({3}):\n{1}\n".format(key, arg_str, name, arg_type))
            try:
                result = func(*args, **kwargs)
                result_str, result_type = log_value(result)
                logger.success("Successfully ended {0}".format(name))
                logger.debug("{0} return value ({2}): \n{1}\n".format(name, result_str, result_type))
                return result
            except Exception as e:
                logger.log(unhandled_error_level,
                           "Unhandled exception in {1}: \"{0}\". It may be handled later, "
                           "but check django logs for all unhandled errors".format(
                               repr(e),
                               name
                           ),
                           exc_info=trace)
                raise
            finally:
                logger.info("<<< Exiting {0}".format(name))

        return wrapped

    return decorator


def methods_logged(logger, methods=None):
    _decorator = partial(logged, logger)

    def class_decorator(cls):
        if not isinstance(cls, type):
            raise TypeError("Decorator `methods_logged` should be used on class. Got {0} instead".format(cls))

        if not methods:
            _methods = [(getattr(cls, x), x, {"function_name": "{0}.{1}".format(cls.__name__, x)}) for x in dir(cls)
                        if not x.startswith("__") and callable(getattr(cls, x))]
        else:
            _methods = []
            for method in methods:
                if isinstance(method, str):
                    method_name = method
                    method_conf = {"function_name": "{0}.{1}".format(cls.__name__, method_name)}
                else:
                    try:
                        method_name = method[0]
                        if isinstance(method[1], dict):
                            method_conf = method[1]
                            method_conf["function_name"] = method_conf.get("function_name",
                                                                           "{0}.{1}".format(cls.__name__, method_name))
                        else:
                            raise ValueError()
                    except (TypeError, ValueError):
                        raise ValueError(
                            "Elements of keyword argument `methods` must be either names of methods or tuples "
                            "(<name of method>, <logging parameters>). Got %s instead" % method
                        )
                if not (method_name and hasattr(cls, method_name)):
                    raise ValueError(
                        "The keyword argument `methods` must contain names of a methods "
                        "of the decorated class: %s. Got '%s' instead." % (cls, method_name)
                    )
                _method = getattr(cls, method_name)
                if not callable(_method):
                    raise TypeError(
                        "Cannot decorate '%s' as it isn't a callable attribute of "
                        "%s (%s)." % (method_name, cls, _method)
                    )
                _methods.append((_method, method_name, method_conf))

        for method, method_name, method_conf in _methods:
            _wrapped = _decorator(**method_conf)(method)
            setattr(cls, method_name, _wrapped)

        return cls

    return class_decorator
