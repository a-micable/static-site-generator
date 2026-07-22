"""Plugin loading and hook dispatch for build extensions."""

from __future__ import annotations

import importlib
import importlib.util
import logging
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from ssg.config import SiteConfig
from ssg.exceptions import PluginError

logger = logging.getLogger(__name__)

HOOKS = {
    "content_indexed",
    "assets_processed",
    "page_rendered",
    "build_finished",
}


@dataclass
class Plugin:
    """Loaded plugin module and metadata."""

    name: str
    module: ModuleType


@dataclass
class HookContext:
    """Mutable context passed to plugin hooks."""

    config: SiteConfig
    phase: str
    data: dict[str, Any]


class PluginManager:
    """Loads configured plugins and dispatches supported hooks."""

    def __init__(self, config: SiteConfig) -> None:
        self.config = config
        self.plugins = [self._load(spec) for spec in config.plugins]

    def _load(self, spec: str) -> Plugin:
        try:
            module = self._load_file(spec) if spec.endswith(".py") else importlib.import_module(spec)
        except Exception as exc:
            raise PluginError(f"Failed to load plugin '{spec}': {exc}") from exc

        name = str(getattr(module, "PLUGIN_NAME", spec))
        logger.info("Loaded plugin: %s", name)
        return Plugin(name=name, module=module)

    def _load_file(self, spec: str) -> ModuleType:
        path = (self.config.source_root / spec).resolve()
        try:
            path.relative_to(self.config.source_root)
        except ValueError as exc:
            raise PluginError(f"Plugin path escapes source root: {spec}") from exc
        if not path.is_file():
            raise PluginError(f"Plugin file not found: {spec}")

        module_name = f"ssg_site_plugin_{path.stem}_{abs(hash(path))}"
        module_spec = importlib.util.spec_from_file_location(module_name, path)
        if module_spec is None or module_spec.loader is None:
            raise PluginError(f"Cannot import plugin file: {spec}")
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module

    def dispatch(self, hook: str, **data: Any) -> HookContext:
        if hook not in HOOKS:
            raise PluginError(f"Unknown plugin hook: {hook}")

        context = HookContext(config=self.config, phase=hook, data=data)
        for plugin in self.plugins:
            callback = getattr(plugin.module, hook, None)
            if callback is None:
                continue
            try:
                result = callback(context)
            except Exception as exc:
                raise PluginError(
                    f"Plugin '{plugin.name}' failed during '{hook}': {exc}"
                ) from exc
            if result is not None:
                context.data["result"] = result
        return context
# rewrite commit 313
# rewrite commit 314
# rewrite commit 315
# rewrite commit 316
# rewrite commit 317
# rewrite commit 318
# rewrite commit 319
# rewrite commit 320
# rewrite commit 321
# rewrite commit 322
# rewrite commit 323
