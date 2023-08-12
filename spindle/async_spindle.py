from spindle.async_spool import AsyncSpool


class AsyncSpindle:
    def __init__(self, key, body):
        AsyncSpool.reset_attributes()
        self.__spool = AsyncSpool[key](**body)

    @classmethod
    def set_attributes(cls, **kwargs):
        """
        Because this pattern is intended to faciliate a wide-range of usecases: database connections, request sessions, open sockets, etc. We don't want
        to pollute our init signatures. Instead we encourage setting class attributes via this method.
        """
        AsyncSpool.set_attributes(kwargs)

    async def weave(self, **kwargs):
        async for i, strand in enumerate(self.__spool.unwind(**kwargs)):
            logging.log(level="DEBUG", msg=f"Processed strand {strand}...")

        logging.log(level="INFO", msg=f"Processed {i + 1} total strands...")
