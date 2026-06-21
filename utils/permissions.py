
from typing import Iterable


def _norm(v) -> str:
    return str(v).strip().lower()


def is_allowed_dm_user(author, allowed_names: Iterable[str], allowed_ids: Iterable[str]) -> bool:
    name = _norm(getattr(author, "name", ""))
    user_id = _norm(getattr(author, "id", ""))
    allowed_name_set = {_norm(x) for x in allowed_names}
    allowed_id_set = {_norm(x) for x in allowed_ids}
    return name in allowed_name_set or user_id in allowed_id_set
