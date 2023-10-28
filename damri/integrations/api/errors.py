from typing import Callable, Type, TypeVar

Error = TypeVar("Error", bound=Exception)


class BaseAPIError(Exception):
    msg: str = ""
    except_: tuple[Type[Error]] = tuple()

    @classmethod
    def handle(cls, *args, exc: Exception, func_: Callable, **kwargs):
        cls.handle_(*args, exc=exc, func_=func_, **kwargs)

    @classmethod
    def handle_(cls, *args, exc: Exception, func_: Callable, **kwargs):
        raise cls(
            f"{'-'*10}\n\n{cls.msg}\n\n{exc}\n{getattr(getattr(exc,'response',''), 'content', '')}\n{func_}\n{args}\n{kwargs}\n\n{'-'*10}\n\n"
        )


class UnexpectedAPIError(BaseAPIError):
    msg = "Unhandled error!"
