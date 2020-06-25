# Timeseries

The data usually is some measurements with a timestamp and sometimes we can observe patterns in this data in time. If we learned somehow these patterns,
we can predict the future data based on previous measurements and compare it with actual measurement. What happens, if predicted and actual measurements are different? Either we learned the pattern incorrectly, or there is an anomaly. We want to detect anomalies fairly early and send an alarm.

The pattern can be described by the model of the observed historical data. There are nearly infinite number of kinds of them; LSTM, Random Forest, SVM are examples of most popular models. They are results of machine learning algorithms, but pure statistics, signal processing algorithms could also be used.

# Training of the model

The training itself is beyond the scope of current implementation. Now it happens offline, the historical data is collected, the training algorithm is chosen, the model parameters are selected, the model is trained. After (successfull) training the model is saved, the model and data specific parameters are also stored in some file. 

Any specific implementations are on users and libriries/algorithms they use.

# Model serving

For online data streaming there is a `TimeSeriesPredictor` (in `timeseries` module), which collects the incoming data into
time window and using pretrained model predicts the next value.

In `bspump.model` there is a simple interface for the saved model. The loading method should be implemented (`load_model_from_file` or anything else). The model should be able to transform the input data to the input it expects (method `transform`) and predict the output (method `predict`).

# Timeseries prediction

The example of model serving and prediction in folder `examples` `bspump-time-series.py`. It shows, how pretrained LSTM model is loaded and being served.
The timeseries is loaded from csv file and values are transformed to expected model input and predicted.

