import signal
import sys

import asab
import asab.web

from .service import BSPumpService
from .__version__ import __version__, __build__


class BSPumpApplication(asab.Application):


    """
    BSPumpApplication is responsible for the main life cycle of the `Application <https://asab.readthedocs.io/en/latest/asab/application.html#>`_. It is based on ASAB `Application <https://asab.readthedocs.io/en/latest/asab/application.html#>`_ class

    |

    """

    def __init__(self, args=None, web_listen=None):
        '''
        Initiates the Application and looks for config with additional arguments.

        **Parameters**

        args : default= None

        web_listen : default= None



        '''
        super().__init__(args=args)

        # Banner
        print("BitSwan BSPump version {}".format(__version__))

        from asab.proactor import Module
        self.add_module(Module)

        from asab.metrics import Module
        self.add_module(Module)

        self.PumpService = BSPumpService(self)
        self.WebContainer = None

        try:
            # Signals are not available on Windows
            self.Loop.add_signal_handler(signal.SIGUSR1, self._on_signal_usr1)
        except (NotImplementedError, AttributeError):
            pass

        # Register bspump API endpoints, if requested (the web service is present)
        if asab.Config["web"].get("listen"):

            # Initialize API service
            self.add_module(asab.web.Module)

            self.WebService = self.get_service("asab.WebService")

            from .web import initialize_web
            self.WebContainer = initialize_web(self.WebService.WebContainer)


    def create_argument_parser(self):
        """
        Enables to create arguments that can be called within the command prompt when starting the application

        :return: parser

        """
        prog = sys.argv[0]
        if prog[-11:] == '__main__.py':
            prog = sys.executable + " -m bspump"

        description = '''
BSPump is a stream processor. It is a part of BitSwan.
For more information, visit: https://github.com/LibertyAces/BitSwanPump

version: {}
build: {} [{}]
'''.format(__version__, __build__, __build__[:7])


        parser = super().create_argument_parser(
            prog=prog,
            description=description
        )
        return parser


    def parse_arguments(self, args=None):
        """
        Parses argument in the ASAB `Application <https://asab.readthedocs.io/en/latest/asab/application.html#>`_ using super() method.

        **Parameters**

        args : default= None

        :return: args

        |

        """
        args = super().parse_arguments(args=args)
        self._web_listen = args.web_api
        return args


    async def main(self):
        """
        Prints a message about how many pipelines are ready.

        |

        """
        print("{} pipeline(s) ready.".format(len(self.PumpService.Pipelines)))


    def _on_signal_usr1(self):
        """
        Description:

        :return:

        :hint: To clear reset from all pipelines, run
        $ kill -SIGUSR1 xxxx
        Equivalently, you can use `docker kill -s SIGUSR1 ....` to reset containerized BSPump.
        """
        # Reset errors from all pipelines
        for pipeline in self.PumpService.Pipelines.values():
            if not pipeline.is_error():
                continue  # Focus only on pipelines that has errors
            pipeline.set_error(None, None, None)
