from __future__ import annotations

import inspect
import types as tys
import typing as ty
from inspect import isclass

from aiogram.types import Message

from models.db import Chat, User
from .base import Param, HandlerParam
from .cutters import (
    Cutter,
    MessageCutter,
    ChatCutter,
    SenderCutter,
    TargetCutter,
    IntegerCutter,
    FloatCutter,
    WordCutter,
    StringCutter,
    OptionalCutter,
    UnionCutter,
    LiteralCutter,
)

if ty.TYPE_CHECKING:
    from inspect import Parameter


def resolve_type(parameter: Parameter) -> HandlerParam:
    if isinstance(parameter.default, Param):
        param_settings = parameter.default
    elif parameter.default != parameter.empty:
        param_settings = Param(default=parameter.default)
    else:
        param_settings = Param()

    if (
        param_settings.default is not None
        or param_settings.default_factory is not None
        and not ty.get_origin(parameter.annotation) is ty.Union
    ):
        param_annotation = ty.Optional[parameter.annotation]
    else:
        param_annotation = parameter.annotation

    cutter = _resolve_cutter(
        param_name=parameter.name,
        param_annotation=param_annotation,
        param_settings=param_settings,
        param_kind=parameter.kind,
    )
    return HandlerParam(
        param_name=parameter.name,
        param_settings=param_settings,
        cutter=cutter,
    )


def _resolve_cutter(
    *, param_name: str, param_annotation: ty.Any, param_settings: Param, param_kind
) -> Cutter:
    if isinstance(param_annotation, str):
        param_annotation = eval(param_annotation)

    if isclass(param_annotation) and Cutter.__subclasscheck__(param_annotation):
        return param_annotation()

    if param_annotation is Message:
        return MessageCutter()
    elif param_annotation is Chat:
        return ChatCutter()
    elif param_annotation is User:
        if param_name == "target":
            return TargetCutter()
        elif param_name == "target_user":
            return TargetCutter(can_be_bot=False)
        else:
            return SenderCutter()

    elif param_annotation is int:
        return IntegerCutter()
    elif param_annotation is float:
        return FloatCutter()
    elif param_annotation is str:
        if param_kind == inspect.Parameter.KEYWORD_ONLY:
            return StringCutter()
        return WordCutter()

    # Optional
    elif ty.get_origin(param_annotation) in {ty.Union, tys.UnionType} and type(
        None
    ) in ty.get_args(param_annotation):
        return OptionalCutter(
            _resolve_cutter(
                param_name=param_name,
                param_annotation=ty.get_args(param_annotation)[0],
                param_settings=param_settings,
                param_kind=param_kind,
            ),
            default=param_settings.default,
            default_factory=param_settings.default_factory,
        )
    # Union
    elif ty.get_origin(param_annotation) in {ty.Union, tys.UnionType}:
        arg_type_cutters = (
            _resolve_cutter(
                param_name=param_name,
                param_annotation=arg_types,
                param_settings=param_settings,
                param_kind=param_kind,
            )
            for arg_types in ty.get_args(param_annotation)
        )
        return UnionCutter(*arg_type_cutters)
    # Literal
    elif ty.get_origin(param_annotation) is ty.Literal:
        return LiteralCutter(*ty.get_args(param_annotation))

    else:
        raise TypeError(
            f"Can't resolve cutter from argument `{param_name}` ({param_annotation})"
        )
