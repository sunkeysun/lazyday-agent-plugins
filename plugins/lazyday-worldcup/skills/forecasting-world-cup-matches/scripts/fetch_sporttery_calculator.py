#!/usr/bin/env python3
"""获取官方 Sporttery 足球计算器 API。"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

try:
    from .forecast_math import extract_sporttery_all_up_options
except ImportError:
    from forecast_math import extract_sporttery_all_up_options


DEFAULT_CALCULATOR_URL = (
    "https://webapi.sporttery.cn/gateway/uniform/football/"
    "getMatchCalculatorV1.qry"
)
DEFAULT_REFERER = "https://m.sporttery.cn/"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)


class TlsCertificateVerificationError(ValueError):
    """本地 Python 证书链拒绝官方 HTTPS endpoint。"""


def _is_certificate_verification_error(error: urllib.error.URLError) -> bool:
    reason = getattr(error, "reason", None)
    if isinstance(reason, ssl.SSLCertVerificationError):
        return True
    return "CERTIFICATE_VERIFY_FAILED" in str(error)


def _url_with_pool_code(url: str, pool_code: str | None) -> str:
    if not pool_code:
        return url
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        return url
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = [(key, value) for key, value in query if key.lower() != "poolcode"]
    query.append(("poolCode", pool_code.upper()))
    return urllib.parse.urlunsplit(
        parsed._replace(query=urllib.parse.urlencode(query))
    )


def fetch_json(
    url: str,
    *,
    referer: str = DEFAULT_REFERER,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: float = 20.0,
    verify_tls: bool = True,
) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "identity",
            "Referer": referer,
            "User-Agent": user_agent,
        },
    )
    ssl_context = None if verify_tls else ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=ssl_context,
        ) as response:
            raw_body = response.read()
            content_type = response.headers.get_content_type()
            charset = response.headers.get_content_charset() or "utf-8"
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:300]
        raise ValueError(
            f"官方 Sporttery API 返回 HTTP {error.code}: {body}"
        ) from error
    except urllib.error.URLError as error:
        if verify_tls and _is_certificate_verification_error(error):
            raise TlsCertificateVerificationError(
                "官方 Sporttery API TLS 证书校验失败：本地 Python 证书链拒绝"
                "官方 endpoint。优先修复本机证书；若只是诊断当前官方数据，"
                "可显式使用 --retry-insecure-on-cert-error 自动重试一次，或使用"
                " --insecure，并在报告中标注 tls_verified=false。"
            ) from error
        raise ValueError(f"官方 Sporttery API 请求失败: {error}") from error

    text = raw_body.decode(charset, errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        snippet = " ".join(text[:300].split())
        raise ValueError(
            "官方 Sporttery API 未返回 JSON "
            f"(content-type={content_type}): {snippet}"
        ) from error
    if not isinstance(payload, dict):
        raise ValueError("官方 Sporttery API JSON 必须是对象")
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser._optionals.title = "选项"
    parser.add_argument("-h", "--help", action="help", help="显示帮助并退出")
    parser.add_argument(
        "--url",
        default=DEFAULT_CALCULATOR_URL,
        help="官方计算器 API URL；默认 getMatchCalculatorV1.qry",
    )
    parser.add_argument(
        "--pool-code",
        choices=("HAD", "HHAD"),
        help="官方 API 可选 poolCode 查询值",
    )
    parser.add_argument("--referer", default=DEFAULT_REFERER)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--insecure",
        action="store_true",
        help=(
            "仅当本地 Python 证书链拒绝官方 endpoint 时，禁用 TLS 证书校验"
        ),
    )
    parser.add_argument(
        "--retry-insecure-on-cert-error",
        action="store_true",
        help=(
            "默认先启用 TLS 校验；仅当出现 CERTIFICATE_VERIFY_FAILED 时，"
            "自动用 tls_verified=false 重试一次"
        ),
    )
    parser.add_argument(
        "--extract-options",
        action="store_true",
        help="输出 eligible HAD/HHAD 过关选项，而不是 raw payload",
    )
    parser.add_argument("--pretty", action="store_true", help="格式化输出 JSON")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    source_url = _url_with_pool_code(args.url, args.pool_code)
    tls_verified = not args.insecure
    tls_fallback_reason = None
    try:
        try:
            payload = fetch_json(
                source_url,
                referer=args.referer,
                user_agent=args.user_agent,
                timeout=args.timeout,
                verify_tls=tls_verified,
            )
        except TlsCertificateVerificationError:
            if args.insecure or not args.retry_insecure_on_cert_error:
                raise
            payload = fetch_json(
                source_url,
                referer=args.referer,
                user_agent=args.user_agent,
                timeout=args.timeout,
                verify_tls=False,
            )
            tls_verified = False
            tls_fallback_reason = "certificate_verify_failed"
        result: dict[str, object] = {
            "retrieval": {
                "source_url": source_url,
                "referer": args.referer,
                "pool_code": args.pool_code,
                "tls_verified": tls_verified,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        }
        if tls_fallback_reason:
            result["retrieval"]["tls_fallback_reason"] = tls_fallback_reason
        if args.extract_options:
            options = extract_sporttery_all_up_options(payload)
            result["sporttery_all_up_options"] = options
            result["count"] = len(options)
        else:
            result["sporttery_api_response"] = payload
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error

    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent, sort_keys=True))


if __name__ == "__main__":
    main()
