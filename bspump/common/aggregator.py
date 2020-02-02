from abc import ABC, abstractmethod

from bspump import Generator


class AggregationStrategy(ABC):
    @abstractmethod
    def append(self, context, event):
        raise NotImplementedError()

    @abstractmethod
    def flush(self):
        raise NotImplementedError()

    @abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError()


class ListAggregationStrategy(AggregationStrategy):

    def __init__(self) -> None:
        super().__init__()
        self.AggregatedEvent = []

    def append(self, context, event):
        self.AggregatedEvent.append((context, event))

    def flush(self):
        result = self.AggregatedEvent
        self.AggregatedEvent = []
        return result

    def is_empty(self) -> bool:
        return len(self.AggregatedEvent) == 0


class ListEventAggregationStrategy(AggregationStrategy):

    def __init__(self) -> None:
        super().__init__()
        self.AggregatedEvent = []

    def append(self, context, event):
        self.AggregatedEvent.append(event)

    def flush(self):
        result = self.AggregatedEvent
        self.AggregatedEvent = []
        return result

    def is_empty(self) -> bool:
        return len(self.AggregatedEvent) == 0


class StringAggregationStrategy(AggregationStrategy):

    def __init__(self, delimiter='\n') -> None:
        super().__init__()
        self.Delimiter = delimiter
        self.AggregatedEvent = ""

    def append(self, context, event):
        self.AggregatedEvent += str(event) + self.Delimiter

    def flush(self):
        result = self.AggregatedEvent[0:-len(self.Delimiter)]  # Remove trailing delimiter
        self.AggregatedEvent = ""
        return result

    def is_empty(self) -> bool:
        return len(self.AggregatedEvent) == 0


class Aggregator(Generator):
    ConfigDefaults = {
        'completion_size': 10,
        'completion_timeout': 0,  # 0 means no timeout,
        'completion_interval': 0  # 0 means no completion interval
    }

    def __init__(self, app, pipeline,
                 aggregation_strategy: AggregationStrategy = ListAggregationStrategy(),
                 id=None, config=None):
        super().__init__(app, pipeline, id, config)
        self.CompletionSize = int(self.Config['completion_size'])
        self.CompletionTimeout = int(self.Config['completion_timeout'])
        self.CompletionInterval = int(self.Config['completion_interval'])

        if self.CompletionTimeout > 0 and self.CompletionInterval > 0:
            raise ValueError("completion_timeout and completion_interval cannot be combined")

        self.AggregationStrategy = aggregation_strategy

        self.CurrentSize = 0
        self.LastFlushTime = self.App.time()
        self.LastPeriodicFlushTime = self.App.time()

        app.PubSub.subscribe("Application.stop!", self._on_application_stop)

        if self.CompletionTimeout > 0:
            app.PubSub.subscribe("Application.tick!", self._check_timeout)

        if self.CompletionInterval > 0:
            app.PubSub.subscribe("Application.tick!", self._check_periodic_flush)

    def _check_timeout(self, _):
        if self.CurrentSize > 0 and self.App.time() - self.LastFlushTime > self.CompletionTimeout:
            self.flush()

    def _check_periodic_flush(self, _):
        if self.CurrentSize > 0 and self.App.time() - self.LastPeriodicFlushTime > self.CompletionInterval:
            self.LastPeriodicFlushTime = self.App.time()
            self.flush()

    def _on_application_stop(self, _, __):
        self.flush()

    def flush(self):
        if self.AggregationStrategy.is_empty():
            return

        aggregated = self.AggregationStrategy.flush()
        self.Pipeline.ensure_future(
            self.generate({}, aggregated, self.PipelineDepth + 1)
        )

    def process(self, context, event):
        self.AggregationStrategy.append(context, event)
        self.CurrentSize += 1
        if self.CurrentSize >= self.CompletionSize:
            self.CurrentSize = 0
            self.flush()
        return None

    async def generate(self, context, aggregated_event, depth):
        self.LastFlushTime = self.App.time()
        await self.Pipeline.inject(context, aggregated_event, depth)
