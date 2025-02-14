# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/time_series/01_tseries_with_RNN.ipynb (unless otherwise specified).

__all__ = ['dataset', 'dataset', 'dataset', 'dataset', 'dataset', 'dataset', 'dataset', 'create_tfds', 'plot_series',
           'create_trend', 'seasonal_pattern', 'create_seasonalities', 'create_noise', 'autocorrelation', 'times',
           'baseline', 'tseries', 'dataset', 'window_size', 'dataset', 'window_size', 'train_tfds', 'valid_tfds',
           'optimizer', 'model', 'history', 'model', 'lr_schedule', 'optimizer', 'history', 'model', 'optimizer',
           'history', 'model', 'history', 'plot_history', 'y_hat', 'y_true', 'y_true']

# Cell
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow_datasets as tfds
import numpy as np
import matplotlib.pyplot as plt

# Cell
# Tạo tập dữ liệu gốc:
dataset = tf.data.Dataset.range(20)
for i in dataset:
    print(i.numpy())

# Cell
dataset = tf.data.Dataset.range(20)
dataset = dataset.window(size=5, shift=1, drop_remainder=True)

# Cell
# Biến window thành batch:
# Thay vì sử dụng map thì chúng ta sử dụng flat_map để sau khi áp dụng hàm, dữ liệu được trải phằng và vẫn giữ nguên thứ tự.
dataset = dataset.flat_map(lambda window: window.batch(5))

# Cell
# Giờ chúng ta sẽ tạo ra Xs và y từ dữ liệu trên:
# Với từng batch, giá trị cuối cùng sẽ là y, còn các giá trị còn lại là Xs.
# Chúng ta có thể sử dụng hàm cho tất cả các dạng windows hoặc sử dụng lambda như dưới:
dataset = dataset.map(lambda batch: (batch[:-1], batch[-1:]))

# Cell
# Tiếp đó, chúng ta sẽ shuffle dữ liệu:
dataset = dataset.shuffle(buffer_size=20)
for batch in dataset:
    print(batch[0].numpy(), batch[1].numpy())

# Cell
# Cuối cùng, chúng ta sẽ tạo batch:
dataset = dataset.batch(4).prefetch(1)

# Cell
def create_tfds(series, window_size=5, batch_size=32, shuffle_size=1000):
    """
        series: dữ liệu đầu vào dưới dạng series (numpy array/range)
        window_size: size của từng window view dữ liệu, ví dụ 5:  5 điểm thời gian liên tiếp
        batch_size: size của 1 batch bao gồm nhiều window: ví dụ 32: 32 chuối 5 điểm thời gian, dùng để train dữ liệu theo batch
        shuffle_size: size của 1 lần shuffle vị trí của các window.
    """
    # Biến đổi series thành tensorflow dataset:
    dataset = tf.data.Dataset.from_tensor_slices(series)

    # Tạo window:
    dataset = dataset.window(window_size+1, shift=1, drop_remainder=True)

    # Trải phẳng:
    dataset = dataset.flat_map(lambda window: window.batch(window_size+1))

    # Tạo Xs, y:
    dataset = dataset.map(lambda o: (o[:-1], o[-1]))

    # xáo dữ liệu:
    dataset = dataset.shuffle(buffer_size=shuffle_size)

    # Tạo batch:
    dataset = dataset.batch(batch_size).prefetch(1)
    return dataset

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

# hàm tạo xu hướng: đơn giản là hàm của thời gian nhân với tỷ lệ slope (tanh):
def create_trend(times, slope=0):
    return times * slope

# Tạo xu tính chất vụ mùa:
def seasonal_pattern(season_time):
    return np.where(season_time < 0.4,
                    np.cos(season_time * 2 * np.pi),
                    1 / np.exp(3 * season_time))

# Tạo dữ liệu có vụ mùa:
def create_seasonalities(time, period, amplitude=1, phase=0):
    season_time = ((time + phase) % period) / period
    return amplitude * seasonal_pattern(season_time)

# Tạo nhiễu:
def create_noise(time, noise_level=1, seed=None):
    rnd = np.random.RandomState(seed) # tạo seed
    return rnd.randn(len(time)) * noise_level

# Tạo autocorrelation:
def autocorrelation(time, amplitude, seed=None):
    phi=0.8
    rnd = np.random.RandomState(seed)
    array = rnd.randn(len(time) + 1)
    for i in range(1, len(time) + 1):
        array[i] += phi * array[i-1]
    return array[1:] * amplitude

# Cell
times = np.arange(4*365 + 1)
baseline = 50
tseries = baseline + create_trend(times, slope = 0.1)\
+ create_seasonalities(times, period=365, amplitude=100)\
+ create_noise(times, seed=42)\
+ autocorrelation(times, amplitude=15)
plot_series(times, tseries)

# Cell
dataset = create_tfds(tseries)

# Cell
window_size = 20
dataset = keras.preprocessing.timeseries_dataset_from_array(
    tseries[:len(tseries)-window_size] #data kết thúc tại len(tseires) - window_size
    , targets=tseries[window_size:] # target bắt đầu từ index của window_size.
    , sequence_length=window_size
    , sequence_stride=1
    , batch_size=128
    , shuffle=True
    , seed=4669
)

# Cell
# Tạo dữ liệu:
window_size = 20
train_tfds = create_tfds(tseries[:3*365], window_size=window_size)
valid_tfds = create_tfds(tseries[3*365:], window_size=window_size)

# Cell
# Tạo mô hình đơn giản:
optimizer = keras.optimizers.Adam(learning_rate=1e-5)
model = keras.Sequential([keras.layers.Dense(1, input_shape=[window_size])])
model.compile(optimizer=optimizer, loss='mse')
model.fit(train_tfds, epochs=300, validation_data=valid_tfds, verbose=0)

# Cell
history = model.history
plt.figure(figsize=(10,6))
plt.plot(np.sqrt(history.history['loss']))
plt.plot(np.sqrt(history.history['val_loss']))
plt.legend(list(history.history.keys()))
plt.title("LOSS - rmse")
plt.show()

# Cell
model = keras.Sequential()
# Tạo layer lambda với mục đích tăng dimension cho X
model.add(keras.layers.Lambda(lambda x: tf.expand_dims(x, -1), input_shape=[None]))

# Tạo 2 layer RNN cơ bản trồng lên nhau:
model.add(keras.layers.SimpleRNN(window_size*2, return_sequences=True))
model.add(keras.layers.SimpleRNN(window_size*2))

# Tạo layer Dense:
model.add(keras.layers.Dense(1))
model.add(keras.layers.Lambda(lambda x: x * 100.))

# Tạo learning rate schedule:
# Tạo một lr schedule thỏa mãn cứ sau 20 epochs, lr sẽ tăng lên với mũ 10, bắt đầu từ 1e-8.
lr_schedule = keras.callbacks.LearningRateScheduler(lambda epoch: 1e-8 * 10**(epoch/20))

# Sử dụng SGD optimizer với momentum = 0.9 (có thể dùng nesterov momentum)
optimizer = keras.optimizers.SGD(learning_rate=1e-8, momentum=0.9, nesterov=True)

# Compile model và chạy
model.compile(optimizer=optimizer, loss=keras.losses.Huber(), metrics=['mse'])
model.fit(train_tfds, epochs=100, validation_data=valid_tfds, callbacks=[lr_schedule])

# Cell
# Vẽ đồ thị learning rate và loss:
history = model.history
plt.figure(figsize=(8,4))
plt.semilogx(history.history["lr"], history.history["loss"])
# plt.axis([1e-8, 1e-4, 0, 30])
plt.show()

# Cell
keras.backend.clear_session()

# Cell
model = keras.Sequential()
# Tạo layer lambda với mục đích tăng dimension cho X
model.add(keras.layers.Lambda(lambda x: tf.expand_dims(x, -1), input_shape=[None]))

# Tạo 2 layer RNN cơ bản trồng lên nhau:
model.add(keras.layers.SimpleRNN(window_size*2, return_sequences=True))
model.add(keras.layers.SimpleRNN(window_size*2))

# Tạo layer Dense:
model.add(keras.layers.Dense(1))
model.add(keras.layers.Lambda(lambda x: x * 100.))

# Sử dụng SGD optimizer với momentum = 0.9 (có thể dùng nesterov momentum)
optimizer = keras.optimizers.SGD(learning_rate=3e-6, momentum=0.9, nesterov=True)

# Compile model và chạy. Giờ chúng ta sẽ ko dùng lr scheduler nữa:
model.compile(optimizer=optimizer, loss=keras.losses.Huber(), metrics=['mse'])
model.fit(train_tfds, epochs=400, validation_data=valid_tfds)

# Cell
history = model.history
plt.figure(figsize=(10,6))
plt.plot(np.sqrt(history.history['loss']))
plt.plot(np.sqrt(history.history['val_loss']))
plt.legend(list(history.history.keys()))
plt.title("LOSS - rmse")
plt.show()

# Cell
keras.backend.clear_session()

# Cell
model = keras.Sequential()
model.add(keras.layers.Lambda(lambda x: tf.expand_dims(x, axis=-1), input_shape=[None]))
model.add(keras.layers.Bidirectional(keras.layers.LSTM(32, return_sequences=True)))
model.add(keras.layers.Bidirectional(keras.layers.LSTM(32)))
model.add(keras.layers.Dense(1))
model.add(keras.layers.Lambda(lambda x: x * 100.))

model.compile(optimizer=keras.optimizers.SGD(lr=3e-6, momentum=.9, nesterov=True), loss=keras.losses.Huber(), metrics=['mse'])
model.summary()

# Cell
model.fit(train_tfds, epochs=400, validation_data=valid_tfds)

# Cell
history = model.history

# Cell
def plot_history(history, metrics:str='Accuracy'):
    item_dict = {'Loss': ['loss', 'val_loss'], f'{metrics}': [f'{metrics.lower()}', f'val_{metrics.lower()}']}
    plot_list = ['Loss', f'{metrics}']
    plt.figure(figsize=(8, 4))
    for i in range(len(plot_list)):
        plt.subplot(1, 2, i+1)
        item = plot_list[i]
        for items in item_dict[item]:
            plt.plot(history.history[items])
        plt.legend(item_dict[item])
    plt.tight_layout()

# Cell
plot_history(history, 'mse')

# Cell
y_hat = model.predict(valid_tfds)

# Cell
y_true = []
for tfds in valid_tfds:
    y = tfds[1].numpy()
    for i in y:
        y_true.append(i)
y_true = np.array(y_true)

# Cell
plt.figure(figsize=(10,6))
plt.plot(y_true)
plt.plot(y_hat)
plt.legend(['y_true', 'y_hat'])
plt.show()