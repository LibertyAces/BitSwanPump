# Timeseries prediction

There is a simple time series predictor `TimeSeriesPredictor` (in `timeseries` module), which collects the incoming data into
time window and using pretrained model predicts the next value. The `Model` (`model` module) is an `abc` class, which should be implemented.
The loading method should be implemented (`load_model_from_file` or anything else). The model should be able to transform the input data
to the input it expects (method `transform`) and predict the output (method `predict`). The model should be pretrained.

For more information see the example `bspump-time-series.py` (uses pretrained LSTM model to predict timeseries).
