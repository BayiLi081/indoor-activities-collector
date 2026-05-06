import json
import logging
from typing import Any
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

from django.conf import settings

logger = logging.getLogger(__name__)

MAX_REMOTE_JSON_BYTES = 2 * 1024 * 1024


def get_configured_assets_base_url() -> str:
  return normalize_base_url(getattr(settings, "ASSETS_BASE_URL", ""))


def get_buildings_manifest_url() -> str:
  configured_url = normalize_text(getattr(settings, "BUILDINGS_MANIFEST_URL", ""))
  if configured_url:
    return configured_url

  assets_base_url = get_configured_assets_base_url()
  if assets_base_url:
    return build_asset_url("buildings.manifest.json", assets_base_url=assets_base_url)

  return ""


def get_effective_assets_base_url() -> str:
  configured_base_url = get_configured_assets_base_url()
  if configured_base_url:
    return configured_base_url

  manifest_url = get_buildings_manifest_url()
  if manifest_url:
    return get_url_parent(manifest_url)

  return ""


def get_url_parent(url: str) -> str:
  parsed = urlparse.urlsplit(url.strip())
  if not parsed.scheme or not parsed.netloc:
    return ""

  parent_path = parsed.path.rsplit("/", 1)[0]
  parent_url = urlparse.urlunsplit((parsed.scheme, parsed.netloc, parent_path, "", ""))
  return normalize_base_url(parent_url)


def build_asset_url(relative_path: str, assets_base_url: str = "") -> str:
  base_url = normalize_base_url(assets_base_url) or get_configured_assets_base_url()
  path = normalize_asset_relative_path(relative_path, assets_base_url=base_url)
  parsed_path = urlparse.urlsplit(path)
  encoded_path = urlparse.quote(parsed_path.path, safe="/-._~@")
  encoded_relative_url = urlparse.urlunsplit(("", "", encoded_path, parsed_path.query, parsed_path.fragment))

  if base_url:
    return f"{base_url}/{encoded_relative_url}"

  if parsed_path.path.startswith("assets/"):
    return f"/{encoded_relative_url}"

  return f"/assets/{encoded_relative_url}"


def normalize_asset_relative_path(relative_path: str, assets_base_url: str = "") -> str:
  path = normalize_text(relative_path).replace("\\", "/").lstrip("/")
  while path.startswith("./"):
    path = path[2:]

  if path.startswith("assets/") and base_url_points_at_assets_container(assets_base_url):
    return path[len("assets/") :]

  return path


def base_url_points_at_assets_container(assets_base_url: str) -> bool:
  parsed = urlparse.urlsplit(normalize_base_url(assets_base_url))
  return parsed.path.rstrip("/").rsplit("/", 1)[-1] == "assets"


def is_absolute_http_url(value: str) -> bool:
  parsed = urlparse.urlsplit(value.strip())
  return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_allowed_asset_proxy_url(value: str, allowed_hosts: list[str]) -> bool:
  if not is_absolute_http_url(value):
    return False

  parsed = urlparse.urlsplit(value.strip())
  hostname = normalize_hostname(parsed.hostname)
  if not hostname:
    return False

  normalized_allowed_hosts = [normalize_allowed_host(host) for host in allowed_hosts]
  normalized_allowed_hosts = [host for host in normalized_allowed_hosts if host]
  if not normalized_allowed_hosts:
    return False

  return any(is_hostname_allowed(hostname, allowed_host) for allowed_host in normalized_allowed_hosts)


def is_hostname_allowed(hostname: str, allowed_host: str) -> bool:
  if allowed_host.startswith("."):
    suffix = allowed_host[1:]
    return hostname == suffix or hostname.endswith(f".{suffix}")

  return hostname == allowed_host


def normalize_allowed_host(value: Any) -> str:
  if not isinstance(value, str):
    return ""

  stripped = value.strip().lower().rstrip(".")
  if not stripped:
    return ""

  if stripped.startswith("."):
    suffix = stripped[1:].lstrip(".")
    return f".{suffix}" if suffix else ""

  return stripped


def normalize_hostname(value: Any) -> str:
  if not isinstance(value, str):
    return ""
  return value.strip().lower().rstrip(".")


def normalize_base_url(value: Any) -> str:
  text = normalize_text(value)
  if not text:
    return ""
  return text.rstrip("/")


def normalize_text(value: Any) -> str:
  if not isinstance(value, str):
    return ""
  return value.strip()


def fetch_json_from_url(url: str, timeout: int, label: str) -> Any | None:
  request = urlrequest.Request(
    url,
    headers={
      "Accept": "application/json",
      "User-Agent": "indoor-publicspace-collector/1.0",
    },
  )

  try:
    with urlrequest.urlopen(request, timeout=timeout) as response:
      content = response.read(MAX_REMOTE_JSON_BYTES + 1)
  except (OSError, ValueError, urlerror.URLError) as error:
    logger.warning("Could not fetch %s from %s: %s", label, url, error)
    return None

  if len(content) > MAX_REMOTE_JSON_BYTES:
    logger.warning("Ignoring %s from %s because it exceeds %s bytes.", label, url, MAX_REMOTE_JSON_BYTES)
    return None

  try:
    return json.loads(content.decode("utf-8"))
  except (UnicodeDecodeError, json.JSONDecodeError) as error:
    logger.warning("Could not parse %s from %s as JSON: %s", label, url, error)
    return None
