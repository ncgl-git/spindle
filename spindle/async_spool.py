from abc import abstractmethod
import typing
from typing import Any
import requests


class AsyncSpool:
    _spools = {}
    _spool_attrs = {}

    def __init_subclass__(cls) -> None:
        assert cls.key, f"A Spool subclass must declare its key! - {cls.__name__}"
        assert cls.key not in cls._spools, f"Two classes cannot have the same key! - {cls.key}"

        cls._spools[cls.key] = cls

    @classmethod
    def __get_item__(cls, key):
        return cls._spools[key]

    def __getattr__(self, __name):
        """Called when default attribute access fails...https://docs.python.org/3/reference/datamodel.html#object.__getattr__"""
        try:
            return self._spool_attrs[__name]
        except KeyError:
            pass

        raise AttributeError

    @classmethod
    def set_attributes(cls, **kwargs):
        """
        Because this pattern is intended to faciliate a wide-range of usecases: database connections, request sessions, open sockets, etc. We don't want
        to pollute our init signatures. Instead we encourage setting class attributes via this method.
        """
        cls._spool_attrs.update(kwargs)

    @classmethod
    def reset_attributes(cls):
        """
        Different event records may warrant different class attributes, so we clear the spool attrs with each Spindle init, in the case that database connection etc.
        are specific to the context of a an event or record.

        If this doesn't apply to you, instantiate the spindle at the top of your lambda instead of per record.

        """
        cls._spool_attrs = {}

    @abstractmethod
    async def hem(**kwargs):
        """Raise exception if certain criteria are met. Can be useful to prevent unintended circular loops"""
        ...

    @abstractmethod
    async def unwind(**kwargs):
        """Called by current spool. This is where the <whatever> is fetched from."""
        ...

    @abstractmethod
    async def stitch(**kwargs):
        """Called by the parent spool. This is where the <whatever>-response body is sent forward to another destination, presumably for further processing."""
        ...

    @abstractmethod
    async def backstitch(**kwargs):
        """Called by the parent Spool. This is where the <whatever>-response body is send back on the queue."""
        ...
