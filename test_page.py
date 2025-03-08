import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import io
import wave

# Title of the app
st.title("Nyquist Sampling Theorem Demonstration")

# Sidebar: Choose input method
st.sidebar.header("Input Signal")
input_method = st.sidebar.radio("Select Signal Source", ["Upload Audio File", "Generate Tone"])

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

# Handle audio file upload
if input_method == "Upload Audio File":
    upload_file = st.sidebar.file_uploader("Upload an audio file (WAV)", type=["wav"])
    if upload_file:
        # Read uploaded file
        audio_data, sample_rate = sf.read(upload_file)

        # Convert to mono if stereo
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

        st.sidebar.write(f"Original Sampling Rate: {sample_rate} Hz")

# Handle sine wave generation
elif input_method == "Generate Tone":
    st.sidebar.header("Tone Generator")
    frequency = st.sidebar.slider("Tone Frequency (Hz)", 50, 5000, 1000)
    duration = st.sidebar.slider("Duration (seconds)", 1, 5, 2)
    sample_rate = 44100  # Default sampling rate

    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)

    st.sidebar.write(f"Generated Tone: {frequency} Hz | {duration} sec")

# Ensure audio_data is defined and is 1D (mono) for both uploaded and generated signals
if audio_data is not None and audio_data.ndim > 1:
    audio_data = np.mean(audio_data, axis=1)

# Play original audio or tone
if audio_data is not None:
    st.subheader("Original Audio Signal")
    st.audio(convert_to_wav(audio_data, sample_rate), format="audio/wav")

    # Plot original waveform
    fig, ax = plt.subplots()
    ax.plot(np.arange(len(audio_data)) / sample_rate, audio_data)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Original Signal")
    st.pyplot(fig)

    # Sampling controls
    st.sidebar.header("Sampling Parameters")
    
    # Only show "Max Frequency Component" slider if the input method is "Generate Tone"
    if input_method == "Generate Tone":
        max_freq = st.sidebar.slider("Max Frequency Component (Hz)", 100, 5000, 1000)

        # Default sampling rates
        default_Fs_under = int(max_freq / 1.5)  # Undersampling (Aliasing)
        default_Fs_critical = int(max_freq)  # Critical sampling
        default_Fs_over = int(2.5 * max_freq)  # Oversampling

        # User-defined sampling rates
        Fs_under = st.sidebar.number_input("Undersampling Frequency (Fs < Fm)", min_value=1, value=default_Fs_under)
        Fs_critical = st.sidebar.number_input("Critical Sampling Frequency (Fs = Fm)", min_value=1, value=default_Fs_critical)
        Fs_over = st.sidebar.number_input("Oversampling Frequency (Fs > 2Fm)", min_value=1, value=default_Fs_over)

        # Display calculated values
        st.write("### Calculated Sampling Frequencies:")
        st.write(f"🔴 **Undersampling Frequency (Aliasing):** {default_Fs_under} Hz")
        st.write(f"🟠 **Critical Sampling Frequency:** {default_Fs_critical} Hz")
        st.write(f"🟢 **Oversampling Frequency (No Aliasing):** {default_Fs_over} Hz")

        # Sampling demonstration
        st.subheader("Sampling Demonstration")
        fig, axs = plt.subplots(3, 1, figsize=(8, 10))
        sampling_rates = [Fs_under, Fs_critical, Fs_over]
        titles = ["Undersampling (Aliasing)", "Critical Sampling", "Oversampling (No Aliasing)"]

    # Play reconstructed audio
    st.subheader("Reconstructed Audio")
    for i, Fs in enumerate(sampling_rates):
        sample_indices = np.arange(0, len(audio_data), sample_rate // Fs)
        sampled_signal = audio_data[sample_indices]
        sampled_time = sample_indices / sample_rate
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
