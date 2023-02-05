import abc

import asab


class LookupProviderABC(abc.ABC, asab.ConfigObject):
    """
    Description:

    |

    """
    def __init__(self, lookup, url, id=None, config=None):
        """
        Description:

        """
        self.Id = "lookupprovider:{}".format(id if id is not None else self.__class__.__name__)
        super().__init__(config_section_name=self.Id, config=config)
        self.Lookup = lookup
        self.App = lookup.App
        self.URL = url
        self.ETag = None

    async def load(self):
        """
        Description:

        |

        """
        raise NotImplementedError()


class LookupBatchProviderABC(LookupProviderABC, abc.ABC):
    """
    Description:

    |

    """
    pass
