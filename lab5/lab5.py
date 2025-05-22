import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

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

t = np.linspace(0, 2 * np.pi, 1000)
noise = np.random.normal(init_vals['noise_mean'], np.sqrt(init_vals['noise_cov']), len(t))

def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_cov, show_noise):
    global noise
    clean = amplitude * np.sin(frequency * t + phase)
    if show_noise:
        noisy = clean + noise
    else:
        noisy = clean
    return clean, noisy

def apply_filter(signal):
    b, a = butter(4, 0.05)
    return filtfilt(b, a, signal)

# Побудова графіка
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, bottom=0.45)

clean, noisy = harmonic_with_noise(
    init_vals['amplitude'],
    init_vals['frequency'],
    init_vals['phase'],
    init_vals['noise_mean'],
    init_vals['noise_cov'],
    init_vals['show_noise']
)
filtered = apply_filter(noisy)

line_clean, = ax.plot(t, clean, label='Чиста гармоніка', color='blue')
line_noisy, = ax.plot(t, noisy, label='Зашумлена', color='gray', alpha=0.5)
line_filtered, = ax.plot(t, filtered, label='Фільтрована', color='green', linestyle='--')
ax.legend()

# Слайдери
axcolor = 'lightgoldenrodyellow'
sliders = {}

def create_slider(name, label, valmin, valmax, valinit, ypos):
    ax_slider = plt.axes([0.2, ypos, 0.65, 0.04], facecolor=axcolor)
    slider = Slider(ax_slider, label, valmin, valmax, valinit=valinit)
    sliders[name] = slider

create_slider('amplitude', 'Амплітуда', 0.1, 5.0, init_vals['amplitude'], 0.35)
create_slider('frequency', 'Частота', 0.1, 5.0, init_vals['frequency'], 0.3)
create_slider('phase', 'Фаза', 0.0, 2 * np.pi, init_vals['phase'], 0.25)
create_slider('noise_mean', 'Сер. шуму', -1.0, 1.0, init_vals['noise_mean'], 0.2)
create_slider('noise_cov', 'Дисперсія', 0.01, 1.0, init_vals['noise_cov'], 0.15)

# Чекбокси
check_ax = plt.axes([0.1, 0.08, 0.15, 0.05], facecolor=axcolor)
check = CheckButtons(check_ax, ['Шум'], [init_vals['show_noise']])

check_ax_f = plt.axes([0.8, 0.08, 0.15, 0.05], facecolor=axcolor)
check_f = CheckButtons(check_ax_f, ['Фільтр'], [init_vals['show_filtered']])

# Кнопка Reset
reset_ax = plt.axes([0.45, 0.08, 0.1, 0.04])
button = Button(reset_ax, 'Reset', color=axcolor, hovercolor='0.975')

def update(val=None):
    global noise
    amp = sliders['amplitude'].val
    freq = sliders['frequency'].val
    phase = sliders['phase'].val
    mean = sliders['noise_mean'].val
    cov = sliders['noise_cov'].val
    show_noise = check.get_status()[0]
    show_filtered = check_f.get_status()[0]

    # Якщо змінився шум — оновлюємо його
    if val in ('noise_mean', 'noise_cov'):
        noise = np.random.normal(mean, np.sqrt(cov), len(t))

    clean, noisy = harmonic_with_noise(amp, freq, phase, mean, cov, show_noise)
    filtered = apply_filter(noisy)

    line_clean.set_ydata(clean)
    line_noisy.set_ydata(noisy)
    line_noisy.set_visible(show_noise)
    line_filtered.set_ydata(filtered)
    line_filtered.set_visible(show_filtered)

    fig.canvas.draw_idle()

# Прив'язка слайдерів
for key in sliders:
    if key in ('noise_mean', 'noise_cov'):
        sliders[key].on_changed(lambda val, k=key: update(k))
    else:
        sliders[key].on_changed(update)

# Прив'язка чекбоксів
check.on_clicked(lambda label: update())
check_f.on_clicked(lambda label: update())

# Reset-функція
def reset(event):
    global noise
    for k, slider in sliders.items():
        slider.reset()
    # Скидання чекбоксів
    if check.get_status()[0] != init_vals['show_noise']:
        check.set_active(0)
    if check_f.get_status()[0] != init_vals['show_filtered']:
        check_f.set_active(0)
    noise = np.random.normal(init_vals['noise_mean'], np.sqrt(init_vals['noise_cov']), len(t))
    update()

button.on_clicked(reset)

plt.show()