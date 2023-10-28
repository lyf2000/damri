import csv
import io
import logging
from contextlib import contextmanager
from copy import deepcopy
from functools import partial, wraps
from io import StringIO
from itertools import chain
from typing import Any, Callable, Dict, Iterable, Optional, Type, TypeVar, Union

from damri.integrations.api.errors import BaseAPIError, UnexpectedAPIError
from damri.integrations.base.params import BaseLimitOffsetFilterParams
from damri.models.base import BaseModel
from damri.utils.data import item_by_source
from damri.utils.string import from_camel_case
from pydantic import ValidationError
from requests import Response, Session
from requests.exceptions import JSONDecodeError

# TODO mv to root
logger = logging.getLogger(__name__)


# region reponse parsers
class BaseResponseParser:
    def parse(self, data: Any) -> Any:
        return data


class CSVResponseParser(BaseResponseParser):
    def parse(self, data: str) -> list[dict]:
        return list(csv.DictReader(StringIO(data), skipinitialspace=True))


class SourceResponseParser(BaseResponseParser):
    def __init__(self, source: str) -> None:
        super().__init__()
        self.source = source  # Example: `response.accounts`

    def parse(self, data: dict) -> Union[dict, list]:
        return item_by_source(self.source, data)


class _CamelCaseResponseParser(BaseResponseParser):
    def parse(self, data: Any):
        if type(data) is dict:
            new = {}
            for key, value in data.items():
                new[from_camel_case(key)] = self.parse(value)
            return new
        elif type(data) in [list, set, tuple]:
            return [self.parse(item) for item in data]
        return data


CamelCaseResponseParser = _CamelCaseResponseParser()


class DumpDetailResponseParser(BaseResponseParser):
    def __init__(self, **specs: dict[str, str] | dict[str, tuple[str, type]]) -> None:
        super().__init__()
        self.specs = {field: (source[0] if isinstance(source, tuple) else source) for field, source in specs.items()}
        self.field_types = {field: source[1] for field, source in specs.items() if isinstance(source, tuple)}

    def parse(self, data: dict) -> dict:
        result = deepcopy(data) if type(data) is dict else dict()
        for field, source in self.specs.items():
            value = item_by_source(source, data)
            if new_type := self.field_types.get(field):
                value = new_type(value)

            result[field] = value

        return result


# endregion

# region API Clients


class BaseAPIClient:
    _session: Optional[Any] = None

    @property
    def session(self) -> Any:
        if self._session is None:
            self._update_session()

        return self._session

    def _api_call(self, *args, **kwargs) -> Response:
        raise NotImplementedError

    def _get_session(self) -> Any:
        raise NotImplementedError

    def _update_session(self):
        self._session = self._get_session()


class BaseRequestsAPIClient(BaseAPIClient):
    """
    Через requests.
    """

    _headers: Dict = {}
    domain: str = ""

    @property
    def session(self) -> Session:
        return super().session

    @property
    def headers(self) -> Dict:
        return self._headers

    def _api_call(self, method: str, url: str, **method_kwargs) -> Response:
        return getattr(self.session, method)(f"{self.domain}{url}", **method_kwargs)

    def _get_session(self) -> Session:
        session = Session()
        session.headers.update(self.headers)

        return session

    def get(self, url: str, data: dict | None = None) -> Response:
        return self._api_call("get", url, json=data or {})

    def post(self, url: str, data: dict | None = None) -> Response:
        return self._api_call("post", url, json=data or {})

    @contextmanager
    def _download_file(self, url: str):
        response = self.get(url)
        file_content = io.BytesIO()
        for chunk in response.iter_content(chunk_size=1024):
            file_content.write(chunk)
        file_content.seek(0)
        yield file_content


# endregion

ApiClass = TypeVar("ApiClass", bound=BaseAPIClient)


# TODO refactor
class BaseAdapterAPIClient:
    API_CLASS: ApiClass = None

    def __getattribute__(self, name: str) -> Any:
        if name != "API_CLASS" and name in super().__getattribute__("methods"):  # TODO fix
            strategy = getattr(self, f"_{self.selected_strategy}")
            result = partial(strategy, method=name)
            del self.selected_strategy
            return result

        return super().__getattribute__(name)

    @property
    def methods(self) -> tuple:
        decorated_methods = []
        api = self.API_CLASS
        for attr_name in dir(api):
            attr_value = getattr(api, attr_name)
            if callable(attr_value) and (request in getattr(attr_value, "_marked", [])):
                decorated_methods.append(attr_name)

        return tuple(decorated_methods)

    def all(self):
        self.selected_strategy = "all"
        return self

    def _all(self, method: str, *meth_args, **meth_kwargs):
        results = []
        for api in self._per_api():
            results = results + getattr(api, method)(*meth_args, **meth_kwargs)

        return results

    def _per_api(self) -> ApiClass:
        for init_data in self._per_api_init_data():
            yield self.API_CLASS(**init_data)

    def _per_api_init_data(self) -> Iterable[dict]:
        raise NotImplementedError


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
APIError = TypeVar("APIError", bound=BaseAPIError)


def _handle_response(content: dict, response_parser=None, detail_response_parser=None, response_model=None):
    if response_parser:
        content = response_parser.parse(content)

    def get_content(content) -> dict:
        if detail_response_parser:
            return detail_response_parser.parse(content)
        return content

    if not response_model:
        return content
    try:
        return (
            response_model(**get_content(content))
            if type(content) is dict or (type(content) is list and content and type(content[0]) in (int, float, str))
            else [response_model(**get_content(content_)) for content_ in content]
        )  # TODO: refact
    except ValidationError as exc:
        logger.exception(f"Error response model validation: {exc}\n\n{content}")
        raise exc


def request(
    response_model: Optional[ResponseModel] = None,
    response_parser: Optional[Type[BaseResponseParser]] = None,
    detail_response_parser: Optional[Type[BaseResponseParser]] = None,
    errors: tuple[Type[APIError]] | None = None,
) -> Callable:  # TODO: move response, parser to service
    def wrapper(func: Callable) -> Callable:
        func._marked = getattr(func, "_marked", [])
        func._marked.append(request)

        @wraps(func)
        def send_request(*args, **kwargs) -> ResponseModel | Any:  # TODO: fix hint
            try:
                resp: Response | Any = func(*args, **kwargs)

                if type(resp) is Response:
                    resp.raise_for_status()

                    try:
                        content: Any = resp.json()
                    except JSONDecodeError:
                        content: Any = resp.content.decode()

                else:
                    pass
            except tuple(chain.from_iterable(err.except_ for err in (errors or []))) or tuple() as err_handled:
                next(error for error in errors if type(err_handled) in error.except_).handle(
                    *args, exc=err_handled, func_=func, **kwargs
                )
            except Exception as err:
                UnexpectedAPIError.handle(*args, exc=err, func_=func, **kwargs)

            return _handle_response(content, response_parser, detail_response_parser, response_model)

        return send_request

    return wrapper


# region JRPC


def jrpc_request(
    response_model: Optional[ResponseModel] = None,
    response_parser: Optional[Type[BaseResponseParser]] = None,
    detail_response_parser: Optional[Type[BaseResponseParser]] = None,
    errors: tuple[Type[APIError]] | None = None,  # TODO handle err codes
) -> Callable:  # TODO: move response, parser to service
    def wrapper(func: Callable) -> Callable:
        func._marked = getattr(func, "_marked", [])
        func._marked.append(request)

        @wraps(func)
        def send_request(*args, **kwargs) -> ResponseModel | Any:  # TODO: fix hint
            try:
                resp: Response | Any = func(*args, **kwargs)

                if type(resp) is Response:
                    resp.raise_for_status()

                    try:
                        content: Any = resp.json()
                    except JSONDecodeError:
                        content: Any = resp.content.decode()

                else:
                    pass
            except tuple(chain.from_iterable(err.except_ for err in (errors or []))) or tuple() as err_handled:
                next(error for error in errors if type(err_handled) in error.except_).handle(
                    *args, exc=err_handled, func_=func, **kwargs
                )
            except Exception as err:
                UnexpectedAPIError.handle(*args, exc=err, func_=func, **kwargs)

            return _handle_response(content, response_parser, detail_response_parser, response_model)

        return send_request

    return wrapper


_RequestParams = TypeVar("_RequestParams", bound=BaseLimitOffsetFilterParams)


class JRPCClient(BaseRequestsAPIClient):
    domain = ""
    ACCESS_TOKEN = ""

    @property
    def base_params(self) -> dict:
        return {}

    def post(self, method: str, params: _RequestParams) -> Response:
        return super().post("", {"method": method, **params.dict(), **self.base_params})


# endregion
