import bspump.unittest
from bspump.common import Aggregator, StringAggregationStrategy, ListEventAggregationStrategy


class TestAggregator(bspump.unittest.ProcessorTestCase):

    def test_aggregator(self):
        events = [
            ({}, {"message": "one"}),
            ({}, {"message": "two"}),
            ({}, {"message": "three"}),
            ({}, {"message": "four"}),
            ({}, {"message": "five"}),
            ({}, {"message": "six"}),
            ({}, {"message": "seven"}),
            ({}, {"message": "eight"}),
            ({}, {"message": "nine"}),
            ({}, {"message": "ten"})
        ]

        self.set_up_processor(Aggregator, config={"completion_size": "5"})

        output = self.execute(events)

        self.assertEqual(2, len(output))

        self.assertEqual(({}, [
            ({}, {"message": "one"}),
            ({}, {"message": "two"}),
            ({}, {"message": "three"}),
            ({}, {"message": "four"}),
            ({}, {"message": "five"})
        ]), output[0])

        self.assertEqual(({}, [
            ({}, {"message": "six"}),
            ({}, {"message": "seven"}),
            ({}, {"message": "eight"}),
            ({}, {"message": "nine"}),
            ({}, {"message": "ten"})
        ]), output[1])

    def test_aggregator_flush_on_stop(self):
        events = [
            ({}, {"message": "one"}),
            ({}, {"message": "two"}),
            ({}, {"message": "three"}),
        ]

        self.set_up_processor(Aggregator, config={"completion_size": "2"})

        output = self.execute(events)

        self.assertEqual(2, len(output))

        self.assertEqual(({}, [
            ({}, {"message": "one"}),
            ({}, {"message": "two"})
        ]), output[0])

        self.assertEqual(({}, [
            ({}, {"message": "three"})
        ]), output[1])

    def test_list_event_aggragation_strategy(self):
        events = [
            ({}, {"message": "one"}),
            ({}, {"message": "two"}),
            ({}, {"message": "three"}),
            ({}, {"message": "four"})
        ]

        self.set_up_processor(Aggregator,
                              aggregation_strategy=ListEventAggregationStrategy(),
                              config={"completion_size": "2"}
                              )

        output = self.execute(events)

        self.assertEqual(2, len(output))

        self.assertEqual(({}, [
            {"message": "one"},
            {"message": "two"}
        ]), output[0])

        self.assertEqual(({}, [
            {"message": "three"},
            {"message": "four"}
        ]), output[1])

    def test_string_aggregation_strategy(self):
        events = [
            ({}, "one"),
            ({}, "two"),
            ({}, "three")
        ]

        self.set_up_processor(Aggregator,
                              aggregation_strategy=StringAggregationStrategy(delimiter=";"),
                              config={"completion_size": "3"}
                              )

        output = self.execute(events)

        self.assertEqual(1, len(output))

        self.assertEqual(({}, "one;two;three"), output[0])
