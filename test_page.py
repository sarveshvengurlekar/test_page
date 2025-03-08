import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import io
import wave

# Title of the app
st.title("Nyquist Sampling Theorem Demonstration")

# Sidebar: Choose input method
st.header("Input Signal")
input_method = st.selectbox("Select Signal Source", ["Upload Audio File (.wav)", "Generate Tone"])

# Function to convert numpy audio to WAV
def convert_to_wav(audio_array, sample_rate):
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())
    return wav_buffer.getvalue()

# Initialize audio_data as None
audio_data = None
sample_rate = 44100  # Default sample rate

# Handle audio file upload
if input_method == "Upload Audio File (.wav)":
    upload_file = st.file_uploader("Upload an audio file (WAV)", type=["wav"])
    if upload_file:
        audio_data, sample_rate = sf.read(upload_file)
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)  # Convert to mono
        st.write(f"Original Sampling Rate: {sample_rate} Hz")

# Handle sine wave generation
elif input_method == "Generate Tone":
    st.header("Tone Generator")
    frequency = st.slider("Tone Frequency (Hz)", 50, 5000, 1000)
    duration = st.slider("Duration (seconds)", 1, 5, 2)
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
    st.write(f"Generated Tone: {frequency} Hz | {duration} sec")

# Function to calculate maximum frequency using FFT
def get_max_frequency(audio_data, sample_rate):
    N = len(audio_data)
    fft_data = np.fft.fft(audio_data)
    fft_freqs = np.fft.fftfreq(N, 1 / sample_rate)
    positive_freqs = fft_freqs[:N // 2]
    positive_fft_data = np.abs(fft_data[:N // 2])
    max_freq_idx = np.argmax(positive_fft_data)
    return positive_freqs[max_freq_idx]

if audio_data is not None:
    max_freq = get_max_frequency(audio_data, sample_rate)
    st.write(f"Maximum Frequency Component: {max_freq:.2f} Hz")

    # Sampling parameters
    default_Fs_under = int(max_freq / 1.5)
    default_Fs_critical = int(max_freq)
    default_Fs_over = int(2.5 * max_freq)

    Fs_under = st.number_input("Undersampling Frequency (Fs < Fm)", min_value=1, value=default_Fs_under)
    Fs_critical = st.number_input("Critical Sampling Frequency (Fs = Fm)", min_value=1, value=default_Fs_critical)
    Fs_over = st.number_input("Oversampling Frequency (Fs > 2Fm)", min_value=1, value=default_Fs_over)
    
    sampling_rates = [Fs_under, Fs_critical, Fs_over]
    titles = ["Undersampling (Aliasing)", "Critical Sampling", "Oversampling (No Aliasing)"]

    # Function to plot frequency spectrum
    def plot_frequency_spectrum(audio_signal, sample_rate, title, ax):
        N = len(audio_signal)
        fft_data = np.fft.fft(audio_signal)
        fft_freqs = np.fft.fftfreq(N, 1 / sample_rate)
        positive_freqs = fft_freqs[:N // 2]
        positive_fft_data = np.abs(fft_data[:N // 2])
        ax.plot(positive_freqs, positive_fft_data, color="blue")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Magnitude")
        ax.set_title(title)
        ax.set_xlim(0, sample_rate / 2)

    # Plot Frequency Spectrum
    fig, axs = plt.subplots(4, 1, figsize=(10, 12))
    plot_frequency_spectrum(audio_data, sample_rate, "Original Signal Spectrum", axs[0])

    for i, Fs in enumerate(sampling_rates):
        sample_indices = np.arange(0, len(audio_data), sample_rate // Fs)
        sampled_signal = audio_data[sample_indices]
        reconstructed_signal = np.interp(np.arange(len(audio_data)), sample_indices, sampled_signal)
        plot_frequency_spectrum(reconstructed_signal, sample_rate, f"{titles[i]} Spectrum", axs[i+1])
    
    st.pyplot(fig)

    # Play reconstructed audio
    st.subheader("Reconstructed Audio")
    for i, Fs in enumerate(sampling_rates):
        sample_indices = np.arange(0, len(audio_data), sample_rate // Fs)
        sampled_signal = audio_data[sample_indices]
        reconstructed_signal = np.interp(np.arange(len(audio_data)), sample_indices, sampled_signal)
        st.write(f"🔊 {titles[i]} (Fs = {Fs} Hz)")
        st.audio(convert_to_wav(reconstructed_signal, sample_rate), format="audio/wav")

    # Conclusion
    st.write("### Conclusion")
    st.write("""
    - **Undersampling:** Causes aliasing, distorting the original signal.
    - **Critical Sampling:** Barely preserves the original waveform.
    - **Oversampling:** Reconstructs the signal accurately without aliasing.
    """)
