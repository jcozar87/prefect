"""
Access attributes of the current task run dynamically.

Note that if a task run cannot be discovered, all attributes will return empty values.

You can mock the runtime attributes for testing purposes by setting environment variables
prefixed with `PREFECT__RUNTIME__TASK_RUN`.

Available attributes:
    - `id`: the task run's unique ID
    - `name`: the name of the task run
    - `tags`: the task run's set of tags
    - `parameters`: the parameters the task was called with
"""
import os
from typing import Any, Dict, List, Optional

import dateparser
import pendulum

from prefect.context import TaskRunContext

__all__ = ["id", "tags", "name", "parameters", "task_name"]


def __getattr__(name: str) -> Any:
    """
    Attribute accessor for this submodule; note that imports also work with this:

        from prefect.runtime.task_run import id
    """

    func = FIELDS.get(name)

    # if `name` is an attribute but it is mocked through environment variable, the mocked type will be str,
    # which might be different from original one. For consistency, cast env var to the same type
    env_key = f"PREFECT__RUNTIME__TASK_RUN__{name.upper()}"

    if func is not None:
        real_value = func()
        if env_key in os.environ:
            mocked_value = os.environ[env_key]
            # cast `mocked_value` to the same type than `real_value`
            if isinstance(real_value, bool):
                return bool(mocked_value)
            elif isinstance(real_value, int):
                return int(mocked_value)
            elif isinstance(real_value, float):
                return float(mocked_value)
            elif isinstance(real_value, pendulum.DateTime):
                return pendulum.instance(dateparser.parse(mocked_value))
            else:
                # default str
                return mocked_value
        else:
            return real_value
    else:
        if env_key in os.environ:
            return os.environ[env_key]
        else:
            raise AttributeError(f"{__name__} has no attribute {name!r}")


def __dir__() -> List[str]:
    return sorted(__all__)


def get_id() -> str:
    task_run_ctx = TaskRunContext.get()
    if task_run_ctx is not None:
        return str(task_run_ctx.task_run.id)


def get_tags() -> List[str]:
    task_run_ctx = TaskRunContext.get()
    if task_run_ctx is None:
        return []
    else:
        return task_run_ctx.task_run.tags


def get_name() -> Optional[str]:
    task_run_ctx = TaskRunContext.get()
    if task_run_ctx is None:
        return None
    else:
        return task_run_ctx.task_run.name


def get_task_name() -> Optional[str]:
    task_run_ctx = TaskRunContext.get()
    if task_run_ctx is None:
        return None
    else:
        return task_run_ctx.task.name


def get_parameters() -> Dict[str, Any]:
    task_run_ctx = TaskRunContext.get()
    if task_run_ctx is not None:
        return task_run_ctx.parameters
    else:
        return {}


FIELDS = {
    "id": get_id,
    "tags": get_tags,
    "name": get_name,
    "parameters": get_parameters,
    "task_name": get_task_name,
}
