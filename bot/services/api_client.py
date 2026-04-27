from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


JsonMapping = Mapping[str, Any]


@dataclass(frozen=True)
class ApiResult:
    method: str
    path: str
    params: JsonMapping | None
    request_body: JsonMapping | None
    configured: bool
    ok: bool
    status_code: int | None = None
    url: str | None = None
    response_body: Any = None
    response_text: str | None = None
    error: str | None = None


def _api_base_url() -> str:
    return os.getenv('API_BASE_URL', '').strip().rstrip('/')


def _clean_mapping(mapping: JsonMapping | None) -> dict[str, Any] | None:
    if mapping is None:
        return None

    cleaned = {key: value for key, value in mapping.items() if value is not None}
    return cleaned or None


def _build_url(base_url: str, path: str, params: JsonMapping | None) -> str:
    url = f'{base_url}{path}'
    clean_params = _clean_mapping(params)
    if clean_params:
        url = f'{url}?{urlencode(clean_params)}'
    return url


def _decode_response(body: bytes, content_type: str) -> tuple[Any, str | None]:
    if not body:
        return None, None

    text = body.decode('utf-8', errors='replace')
    if 'application/json' not in content_type.lower():
        return None, text

    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text


def _request_sync(
    method: str,
    path: str,
    request_body: JsonMapping | None = None,
    params: JsonMapping | None = None,
    timeout_seconds: int = 10,
) -> ApiResult:
    clean_body = _clean_mapping(request_body)
    clean_params = _clean_mapping(params)
    base_url = _api_base_url()

    if not base_url:
        pending_request = {
            'method': method.upper(),
            'path': path,
            'params': clean_params,
            'json': clean_body,
        }
        print('API_BASE_URL is not configured. Pending API request:')
        print(json.dumps(pending_request, indent=2, sort_keys=True))
        return ApiResult(
            method=method.upper(),
            path=path,
            params=clean_params,
            request_body=clean_body,
            configured=False,
            ok=False,
        )

    url = _build_url(base_url, path, clean_params)
    data = None
    headers = {'Accept': 'application/json'}
    if clean_body is not None:
        data = json.dumps(clean_body).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    request = Request(url, data=data, headers=headers, method=method.upper())

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            response_body, response_text = _decode_response(
                response.read(),
                response.headers.get('Content-Type', ''),
            )
            status_code = response.status
            return ApiResult(
                method=method.upper(),
                path=path,
                params=clean_params,
                request_body=clean_body,
                configured=True,
                ok=200 <= status_code < 300,
                status_code=status_code,
                url=url,
                response_body=response_body,
                response_text=response_text,
            )
    except HTTPError as exc:
        response_body, response_text = _decode_response(
            exc.read(),
            exc.headers.get('Content-Type', ''),
        )
        return ApiResult(
            method=method.upper(),
            path=path,
            params=clean_params,
            request_body=clean_body,
            configured=True,
            ok=False,
            status_code=exc.code,
            url=url,
            response_body=response_body,
            response_text=response_text,
            error=str(exc),
        )
    except URLError as exc:
        return ApiResult(
            method=method.upper(),
            path=path,
            params=clean_params,
            request_body=clean_body,
            configured=True,
            ok=False,
            url=url,
            error=str(exc.reason),
        )
    except TimeoutError:
        return ApiResult(
            method=method.upper(),
            path=path,
            params=clean_params,
            request_body=clean_body,
            configured=True,
            ok=False,
            url=url,
            error='Request timed out.',
        )


async def api_request(
    method: str,
    path: str,
    request_body: JsonMapping | None = None,
    params: JsonMapping | None = None,
    timeout_seconds: int = 10,
) -> ApiResult:
    return await asyncio.to_thread(
        _request_sync,
        method,
        path,
        request_body,
        params,
        timeout_seconds,
    )
