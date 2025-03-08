import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import io
import wave

# Title of the app
st.title("Nyquist Sampling Theorem Demonstration")

# Upload audio file
st.sidebar.header("Audio Input")
upload_file = st.sidebar.file_uploader("Upload an audio file (WAV)", type=["wav"])

if upload_file:
    # Read the uploaded file
    audio_data, sample_rate = sf.read(upload_file)

    # Convert to mono if stereo
    if audio_data.ndim > 1:
        audio_data = np.mean(audio_data, axis=1)

    st.sidebar.write(f"Original Sampling Rate: {sample_rate} Hz")

    # Convert NumPy array to WAV format
    def convert_to_wav(audio_array, sample_rate):
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)  # Mono audio
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(sample_rate)
            wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())
        return wav_buffer.getvalue()

    # Play the original audio
    st.subheader("Original Audio Signal")
    st.audio(convert_to_wav(audio_data, sample_rate), format="audio/wav")

    # Plot original waveform
    fig, ax = plt.subplots()
    ax.plot(np.arange(len(audio_data)) / sample_rate, audio_data)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Original Signal")
    st.pyplot(fig)

    # Sampling rates for Nyquist demonstration
    st.sidebar.header("Sampling Parameters")
    max_freq = st.sidebar.slider("Max Frequency Component (Hz)", 100, 5000, 1000)

    Fs_under = int(max_freq / 1.5)  # Undersampling (Aliasing)
    Fs_critical = int(max_freq)  # Critical sampling
    Fs_over = int(2.5 * max_freq)  # Oversampling

    sampling_rates = [Fs_under, Fs_critical, Fs_over]
    titles = ["Undersampling (Aliasing)", "Critical Sampling", "Oversampling (No Aliasing)"]

    st.subheader("Sampling Demonstration")
    fig, axs = plt.subplots(3, 1, figsize=(8, 10))

    for i, Fs in enumerate(sampling_rates):
        # Sample the signal
        sample_indices = np.arange(0, len(audio_data), sample_rate // Fs)
        sampled_signal = audio_data[sample_indices]
        sampled_time = sample_indices / sample_rate

        # Reconstruct the signal
        t_interp = np.linspace(0, len(audio_data) / sample_rate, len(audio_data))
        reconstructed_signal = np.interp(t_interp, sampled_time, sampled_signal)

        # Plot the sampled signal
        axs[i].plot(np.arange(len(audio_data)) / sample_rate, audio_data, "gray", alpha=0.5, label="Original")
        axs[i].scatter(sampled_time, sampled_signal, color="red", label="Sampled Points")
        axs[i].plot(t_interp, reconstructed_signal, "blue", linestyle="dashed", label="Reconstructed")

        axs[i].set_title(titles[i] + f" (Fs = {Fs} Hz)")
        axs[i].set_xlabel("Time (s)")
        axs[i].set_ylabel("Amplitude")
        axs[i].legend()

    st.pyplot(fig)

    # Play reconstructed audio for different cases
    st.subheader("Reconstructed Audio")
    for i, Fs in enumerate(sampling_rates):
        sample_indices = np.arange(0, len(audio_data), sample_rate // Fs)
        sampled_signal = audio_data[sample_indices]
        sampled_time = sample_indices / sample_rate
        reconstructed_signal = np.interp(np.arange(len(audio_data)), sample_indices, sampled_signal)

        st.write(f"🔊 {titles[i]} (Fs = {Fs} Hz)")
        st.audio(convert_to_wav(reconstructed_signal, sample_rate), format="audio/wav")

    st.write("### Conclusion")
    st.write("""
    - **Undersampling:** Causes aliasing, distorting the original signal.  
    - **Critical Sampling:** Barely preserves the original waveform.  
    - **Oversampling:** Reconstructs the signal accurately without aliasing.
    """)

else:
    st.warning("⚠️ Please upload an audio file to proceed.")
