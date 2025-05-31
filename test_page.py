import streamlit as st
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wav
import io
import base64
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Signals & Systems Virtual Lab",
    layout="wide",
    page_icon=" "
)

# Function to convert audio to base64 for browser playback
def get_audio_base64(audio, sample_rate):
    buffer = io.BytesIO()
    wav.write(buffer, sample_rate, (audio * 32767).astype(np.int16))
    audio_bytes = buffer.getvalue()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    return f"data:audio/wav;base64,{audio_base64}"

# Initialize session state variables
if 'audio' not in st.session_state:
    st.session_state.audio = None
    st.session_state.sample_rate = None
    st.session_state.filtered_audio = None
    st.session_state.filter_params = None

# Streamlit app layout
st.title("Audio Filtering App")

# File uploader
uploaded_file = st.file_uploader("Upload a WAV file", type=["wav"])

if uploaded_file is not None:
    try:
        # Read and process audio file
        sample_rate, audio = wav.read(uploaded_file)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        audio = audio / np.max(np.abs(audio))
        st.session_state.audio = audio
        st.session_state.sample_rate = sample_rate
        st.success("Audio file loaded successfully!")
        
        # Display original audio
        st.audio(get_audio_base64(audio, sample_rate), format="audio/wav")
        
    except Exception as e:
        st.error(f"Failed to load audio: {e}")

# Filter selection
filter_type = st.selectbox("Select Filter Type", ["Low-Pass", "High-Pass", "Band-Pass"])

# Cutoff frequency inputs
nyquist = 0.5 * st.session_state.sample_rate if st.session_state.sample_rate else 22050  # Default Nyquist for error handling
col1, col2 = st.columns(2)

if filter_type in ["Low-Pass", "High-Pass"]:
    cutoff = col1.number_input("Cutoff Frequency (Hz)", min_value=1, max_value=int(nyquist), value=1000)
elif filter_type == "Band-Pass":
    low_cutoff = col1.number_input("Lower Cutoff Frequency (Hz)", min_value=1, max_value=int(nyquist), value=500)
    high_cutoff = col2.number_input("Upper Cutoff Frequency (Hz)", min_value=1, max_value=int(nyquist), value=1500)

# Apply filter button
if st.button("Apply Filter"):
    if st.session_state.audio is None:
        st.error("No audio file loaded!")
    else:
        try:
            if filter_type == "Low-Pass":
                normal_cutoff = cutoff / nyquist
                b, a = signal.butter(6, normal_cutoff, btype='low', analog=False)
            elif filter_type == "High-Pass":
                normal_cutoff = cutoff / nyquist
                b, a = signal.butter(6, normal_cutoff, btype='high', analog=False)
            elif filter_type == "Band-Pass":
                if low_cutoff >= high_cutoff or low_cutoff <= 0 or high_cutoff >= nyquist:
                    st.error(f"Enter valid frequencies (1-{int(nyquist)} Hz) with low < high.")
                else:
                    normal_cutoff = [low_cutoff / nyquist, high_cutoff / nyquist]
                    b, a = signal.butter(6, normal_cutoff, btype='band', analog=False)
            
            # Apply filter
            st.session_state.filtered_audio = signal.filtfilt(b, a, st.session_state.audio)
            st.session_state.filter_params = (b, a)
            st.success("Filter applied! You can now play the filtered audio or plot the response.")
            
            # Display filtered audio
            st.audio(get_audio_base64(st.session_state.filtered_audio, st.session_state.sample_rate), format="audio/wav")
            
        except ValueError:
            st.error("Invalid input! Please enter valid numeric cutoff values.")

# Plot response button
if st.button("Plot Response"):
    if st.session_state.filter_params is None:
        st.error("Apply a filter first to plot the response!")
    else:
        b, a = st.session_state.filter_params
        nyquist = 0.5 * st.session_state.sample_rate
        w, h = signal.freqz(b, a, worN=2000)

        # Compute FFT
        N = len(st.session_state.audio)
        N_fft = 2**np.ceil(np.log2(N)).astype(int)
        freqs = np.fft.fftfreq(N_fft, d=1/st.session_state.sample_rate)
        fft_original = np.fft.fft(st.session_state.audio, N_fft)
        fft_filtered = np.fft.fft(st.session_state.filtered_audio, N_fft) if st.session_state.filtered_audio is not None else None

        # Set x-axis range
        max_freq = min(5000, nyquist)
        mask = (freqs >= 0) & (freqs <= max_freq)
        freq_hz = freqs[mask]
        filter_freq_hz = (w * nyquist / np.pi)

        # Create plots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

        # Filter Frequency Response
        ax1.plot(filter_freq_hz, 20 * np.log10(abs(h)), 'black')
        ax1.set_title("Filter Frequency Response")
        ax1.set_xlabel("Frequency (Hz)")
        ax1.set_ylabel("Gain (dB)")
        ax1.set_xticks(np.arange(250, max_freq+1, 250))
        ax1.set_xlim(0, max_freq)
        ax1.grid(color='gray', linestyle='--', linewidth=0.5)

        # FFT of Original Audio
        ax2.plot(freq_hz, np.abs(fft_original[mask]), color='blue')
        ax2.set_title("FFT of Original Audio")
        ax2.set_xlabel("Frequency (Hz)")
        ax2.set_ylabel("Magnitude")
        ax2.set_xticks(np.arange(250, max_freq+1, 250))
        ax2.set_xlim(0, max_freq)
        ax2.grid(color='gray', linestyle='--', linewidth=0.5)

        # FFT of Filtered Audio
        if fft_filtered is not None:
            ax3.plot(freq_hz, np.abs(fft_filtered[mask]), color='red')
            ax3.set_title("FFT of Filtered Audio")
            ax3.set_xlabel("Frequency (Hz)")
            ax3.set_ylabel("Magnitude")
            ax3.set_xticks(np.arange(250, max_freq+1, 250))
            ax3.set_xlim(0, max_freq)
            ax3.grid(color='gray', linestyle='--', linewidth=0.5)

        plt.tight_layout()
        st.pyplot(fig)
