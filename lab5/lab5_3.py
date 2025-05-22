import numpy as np
from bokeh.layouts import column, row
from bokeh.models import Slider, Button, CheckboxGroup, ColumnDataSource
from bokeh.plotting import figure, curdoc

t = np.linspace(0, 2 * np.pi, 1000)

# Початкові значення
init_vals = {
    'amplitude': 1.0,
    'frequency': 1.0,
    'phase': 0.0,
    'noise_mean': 0.0,
    'noise_cov': 0.1,
    'show_noise': True,
    'show_filtered': True
}

def generate_noise(mean, cov):
    return np.random.normal(mean, np.sqrt(cov), len(t))

def harmonic_with_noise(amplitude, frequency, phase, noise, show_noise):
    clean = amplitude * np.sin(frequency * t + phase)
    noisy = clean + noise if show_noise else clean
    return clean, noisy

# Власна реалізація фільтра (просте ковзне середнє)
def my_filter(signal, window_size=10):
    filtered = np.copy(signal)
    half = window_size // 2
    for i in range(half, len(signal) - half):
        filtered[i] = np.mean(signal[i - half:i + half + 1])
    return filtered

# Ініціалізація
noise = generate_noise(init_vals['noise_mean'], init_vals['noise_cov'])
clean, noisy = harmonic_with_noise(init_vals['amplitude'], init_vals['frequency'], init_vals['phase'], noise, init_vals['show_noise'])
filtered = my_filter(noisy)

source_clean = ColumnDataSource(data=dict(x=t, y=clean))
source_noisy = ColumnDataSource(data=dict(x=t, y=noisy))
source_filtered = ColumnDataSource(data=dict(x=t, y=filtered))

# Фігури
p1 = figure(title="Чиста гармоніка", height=200, width=800)
p1.line('x', 'y', source=source_clean, color="blue", legend_label="Чиста")

p2 = figure(title="Зашумлена", height=200, width=800)
p2.line('x', 'y', source=source_noisy, color="gray", legend_label="Шум")

p3 = figure(title="Фільтрована", height=200, width=800)
p3.line('x', 'y', source=source_filtered, color="green", legend_label="Фільтрована")

# Віджети
amplitude_slider = Slider(title="Амплітуда", start=0.1, end=5.0, step=0.1, value=init_vals['amplitude'])
frequency_slider = Slider(title="Частота", start=0.1, end=5.0, step=0.1, value=init_vals['frequency'])
phase_slider = Slider(title="Фаза", start=0.0, end=2 * np.pi, step=0.1, value=init_vals['phase'])
noise_mean_slider = Slider(title="Середнє шуму", start=-1.0, end=1.0, step=0.01, value=init_vals['noise_mean'])
noise_cov_slider = Slider(title="Дисперсія шуму", start=0.01, end=1.0, step=0.01, value=init_vals['noise_cov'])

checkboxes = CheckboxGroup(labels=["Показати шум", "Показати фільтр"], active=[0, 1])
reset_button = Button(label="Скинути", button_type="success")

# Update function
def update(attr, old, new):
    global noise
    amp = amplitude_slider.value
    freq = frequency_slider.value
    phase = phase_slider.value
    mean = noise_mean_slider.value
    cov = noise_cov_slider.value
    show_noise = 0 in checkboxes.active
    show_filtered = 1 in checkboxes.active
    window_size = 10

    # Генерація нового шуму лише якщо змінюються шумові параметри
    if attr in ("value",):
        noise[:] = generate_noise(mean, cov)

    clean, noisy = harmonic_with_noise(amp, freq, phase, noise, show_noise)
    filtered = my_filter(noisy, window_size)

    source_clean.data = dict(x=t, y=clean)
    source_noisy.data = dict(x=t, y=noisy)
    source_filtered.data = dict(x=t, y=filtered)

    p2.visible = show_noise
    p3.visible = show_filtered

# Reset function
def reset():
    amplitude_slider.value = init_vals['amplitude']
    frequency_slider.value = init_vals['frequency']
    phase_slider.value = init_vals['phase']
    noise_mean_slider.value = init_vals['noise_mean']
    noise_cov_slider.value = init_vals['noise_cov']
    checkboxes.active = [0, 1]
    update(None, None, None)

# Прив'язка віджетів
for slider in [amplitude_slider, frequency_slider, phase_slider,
               noise_mean_slider, noise_cov_slider]:
    slider.on_change("value", update)

checkboxes.on_change("active", update)
reset_button.on_click(reset)

# Layout
layout = column(
    p1, p2, p3,
    row(amplitude_slider, frequency_slider, phase_slider),
    row(noise_mean_slider, noise_cov_slider),
    row(checkboxes, reset_button)
)

curdoc().add_root(layout)
curdoc().title = "Гармоніка з шумом і фільтром"