# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/time_series/00_basics.ipynb (unless otherwise specified).

__all__ = ['plot_series', 'create_trend', 'times', 'tseries', 'seasonal_pattern', 'create_seasonalities', 'tseries',
           'baseline', 'tseries', 'create_noise', 'noises', 'split_time', 'train_series', 'train_times', 'valid_series',
           'valid_times', 'autocorrelate1', 'autocorrelate2', 'ac_series1', 'ac_series2', 'beta', 'tseries1', 'model',
           'model_fit', 'model1', 'model_fit1', 'moving_average_model']

# Cell
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.preprocessing import sequence, timeseries_dataset_from_array
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

# ignore warnings:
import warnings
warnings.filterwarnings('ignore')

# Cell
def plot_series(time, series, format="-", start=0, end=None, label=None):
    plt.figure(figsize=(10, 6))
    plt.plot(time[start:end], series[start:end], format, label=label)
    plt.xlabel("Time")
    plt.ylabel("Value")
    if label:
        plt.legend(fontsize=14)
    plt.grid(True)
    plt.show()

# Cell
# hàm tạo xu hướng: đơn giản là hàm của thời gian nhân với tỷ lệ slope (tanh):
def create_trend(times, slope=0):
    return times * slope

# Cell
# Tạo time series và vẽ đồ thị giữa thời gian và giá trị:
times = np.arange(4*365 +1) # tạo dữ liệu cho 4 năm
tseries = create_trend(times, .1)
plot_series(times, tseries)

# Cell
# Tạo xu tính chất vụ mùa:
def seasonal_pattern(season_time):
    return np.where(season_time < 0.4,
                    np.cos(season_time * 2 * np.pi),
                    1 / np.exp(3 * season_time))

# Tạo dữ liệu có vụ mùa:
def create_seasonalities(time, period, amplitude=1, phase=0):
    season_time = ((time + phase) % period) / period
    return amplitude * seasonal_pattern(season_time)

# Cell
tseries = create_seasonalities(times, 365, amplitude=100)
plot_series(times, tseries)

# Cell
baseline = 5
tseries = baseline + create_trend(times, slope=.05) + create_seasonalities(times, period=365, amplitude=10)
plot_series(tseries, times)

# Cell
def create_noise(time, noise_level=1, seed=None):
    rnd = np.random.RandomState(seed) # tạo seed
    return rnd.randn(len(time)) * noise_level

# Cell
noises = create_noise(times, seed=42)
plot_series(times, noises)

# Cell
## Bổ sung noise vào:
tseries += noises
plot_series(times, tseries)

# Cell
# Chia dữ liệu thành tập train và valid:
split_time = 1000
train_series = tseries[:split_time]
train_times = times[:split_time]
valid_series = tseries[split_time:]
valid_times = times[split_time:]

# Cell
# Tạo hàm tạo ra dữ liệu có tính chất autocorrelate:
def autocorrelate1(time, amplitude, seed=None):
    phi1 = 0.5
    phi2 = -0.1
    rnd = np.random.RandomState(seed)
    array = rnd.randn(len(time) + 50)
    array[:50] = 100
    for i in range(50, len(time)+50):
        array[i] += phi1 + array[i - 50]
        array[i] += phi2 + array[i - 33]
    return array[50:] * amplitude

def autocorrelate2(time, amplitude, seed=None):
    phi=0.8
    rnd = np.random.RandomState(seed)
    array = rnd.randn(len(time) + 1)
    for i in range(1, len(time) + 1):
        array[i] += phi * array[i-1]
    return array[1:] * amplitude

# Cell
ac_series1 = autocorrelate1(times, 10, seed=42)
plot_series(times, ac_series1)

# Cell
ac_series2 = autocorrelate2(times, 5, seed=42)
plot_series(times, ac_series2)

# Cell
# Kết hợp lại:
tseries += ac_series2
plot_series(times, tseries)

# Cell
# Tạo mới series:
beta = 500
tseries1 = autocorrelate2(times, 10, seed=42) + create_seasonalities(times, period=50, amplitude=150) + create_trend(times, 2)
plot_series(times[:300], tseries1[:300])

# Cell
from pandas.plotting import autocorrelation_plot

# Cell
autocorrelation_plot(tseries)
plt.show()

# Cell
autocorrelation_plot(tseries1)
plt.show()

# Cell
from statsmodels.tsa.arima_model import ARIMA
model = ARIMA(tseries, order=(5, 1, 0))
model_fit = model.fit(disp=0)
print(model_fit.summary())

# Cell
# Thử với số lượng lag <= 10
model1 = ARIMA(tseries, order=(10, 1, 1))
model_fit1 = model1.fit(disp=0)
print(model_fit1.summary())

# Cell
def moving_average_model(series, lag=5, phi=1, seed=None):
    np.random.RandomSate(seed)
    for i in range(lag, len(series)+lag):
        series[i] = np.mean(sum(series[i-lag:i])) * phi
    return series[lag:]