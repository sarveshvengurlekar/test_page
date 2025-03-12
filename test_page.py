import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import io
import wave

st.set_page_config(
    page_title="Signals & Systems Virtual Lab",
    layout="wide",
    page_icon=" "
)



# Inject custom CSS for header styling
st.markdown(
    f"""
    <style>
    .header {{
        position: fixed;
        left: 0;
        top: 0;
        width: 100%;
        height: 148px;
        background-color: #00b3ff;
        color: #FFFFFF;
        text-align: center;
        padding: 90px 10px;
        z-index: 1000;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .header-content {{
        flex-grow: 1;
        text-align: center;
    }}
    

    .header p {{
        font-family: "Times New Roman", Times, serif;
        font-size: 15px;
        line-height: 1.2;
        margin: 5px 0;
    }}

    .header p1 {{
        font-family: "Times New Roman", Times, serif;
        font-size: 30px;
        line-height: 1.2;
        margin: 5px 0;
    }}

    .header-content {{
        flex-grow: 1;
        text-align: center;
        padding-top: 50px; /* Adjust this value to move text down */
    }}

    .logo-container {{
        padding-right: 20px;
        padding-top: 60px;
    }}

    .logo-container img {{
        width: 100px;
        height: auto;
    }}
    .stApp {{
        margin-top: 180px; /* Push content below the fixed header */
        padding-bottom: 80px; /* Avoid footer overlap */
    }}

    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        height: 42px;
        background-color: #00b3ff;
        color: #FFFFFF;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        z-index: 1000;
    }}
    </style>

    <!-- Header section with logo on the top-right corner -->
    <div class="header">
        <div class="header-content">
            <p><b>AGNEL CHARITIES</b></p>
            <p1><b>FR. C. RODRIGUES INSTITUTE OF TECHNOLOGY</b></p1>
            <p>Agnel Technical Education Complex Sector 9-A, Vashi, Navi Mumbai, Maharashtra, India PIN - 400703</p>
            <p>(An Autonomous Institute & Permanently Affiliated To University Of Mumbai)</p>
        </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Inject custom CSS for footer
st.markdown(
    """
    <div class="footer">
        <p>© 2025 Fr. Conceicao Rodrigues Institute of Technology. All rights reserved.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Hide Streamlit default menu
hide_menu = """
<style>
#MainMenu {
visibility:hidden;
}
</style>
"""

# Remove unnecessary UI elements
st.markdown("""<style>[data-testid="stDecoration"] { display: none; }</style>""", unsafe_allow_html=True)
st.markdown(hide_menu, unsafe_allow_html=True)  # Apply hidden menu style


st.markdown("<h1 style='text-align: center; color: black;'> Our Vision </h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size:28px; text-align: justify;'>"
    "The <b>Signal Processing Virtual Lab</b> is a digital learning platform designed by <b>Fr. C. Rodrigues Institute of Technology</b> to bridge the gap "
    "between theoretical concepts and practical visualization in signal processing. By providing an "
    "interactive environment, it enables users to analyze, observe, and understand various signal "
    "characteristics through real-time graphical representations. "
    "This platform overcomes geographical and resource limitations, ensuring wider accessibility "
    "to high-quality education in signal processing."
    "</p>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# Key Features with Increased Text Size
st.markdown("<h1 style='color: black;'> • Key Features</h1>", unsafe_allow_html=True)

features = [
    "<b>Interactive Learning:</b> Explore and visualize fundamental signal processing concepts through simulations.",
    "<b>Dynamic Visualizations:</b> Gain insights into signal behavior with real-time graphical representations.",
    "<b>Unrestricted Accessibility:</b> Access the lab anytime, anywhere, without the need for physical equipment.",
    "<b>Conceptual Clarity:</b> Strengthen understanding of signal properties, transformations, and system behavior.",
    "<b>Bridging Theory and Visualization:</b> Enhance learning by observing how theoretical concepts translate into signal representations."
]

# Display Key Features with Larger Font
for feature in features:
    st.markdown(f"<p style='font-size:28px;'> - {feature}</p>", unsafe_allow_html=True)


st.header("")

st.header("</> Developers Team", divider="blue")

st.header("")

# Title of the app
st.sidebar.title("Nyquist Sampling Theorem Demonstration")

# Sidebar: Choose input method
st.header("Input Signal")
input_method = st.selectbox("Select Signal Source", ["Generate Tone", "Upload Audio File (.wav)"])

# Function to convert numpy audio to WAV
def convert_to_wav(audio_array, sample_rate):
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())
    return wav_buffer.getvalue()

# Initialize variables
audio_data = None
sample_rate = 44100  # Default sample rate

# Handle audio file upload
if input_method == "Upload Audio File (.wav)":
    upload_file = st.file_uploader("Upload an audio file (WAV)", type=["wav"])

    # Define the local file path
    local_file_path = "audio2 (2).wav"  # Update this with the correct path

    # Read the file in binary mode
    with open(local_file_path, "rb") as file:
        wav_bytes = file.read()
    # Streamlit download button
    st.download_button(
        label="Download Audio File",
        data=wav_bytes,
        file_name="downloaded_audio.wav",
        mime="audio/wav")


    
    if upload_file:
        audio_data, sample_rate = sf.read(upload_file)
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)  # Convert to mono
            st.write(f"Original Sampling Rate: {sample_rate} Hz")

# Handle sine wave generation
elif input_method == "Generate Tone":
    st.header("Tone Generator")
    frequency = st.number_input("Tone Frequency (Hz)", 50, 5000, 1000)
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
    default_Fs_under = int(max_freq / 1.5)  # Undersampling (Aliasing)
    default_Fs_critical = int(max_freq)  # Critical sampling
    default_Fs_over = int(2.5 * max_freq)  # Oversampling (No Aliasing)

    Fs_under = st.number_input("Undersampling Frequency (Fs < Fm)", min_value=1, value=default_Fs_under)
    Fs_critical = st.number_input("Critical Sampling Frequency (Fs = Fm)", min_value=1, value=default_Fs_critical)
    Fs_over = st.number_input("Oversampling Frequency (Fs > 2Fm)", min_value=1, value=default_Fs_over)
    
    sampling_rates = [Fs_under, Fs_critical, Fs_over]
    titles = ["Undersampling (Aliasing)", "Critical Sampling", "Oversampling (No Aliasing)"]
    colors = ["red", "orange", "darkblue"]

    # Play reconstructed audio (before the plots)
    st.subheader("Reconstructed Audio")
    for i, Fs in enumerate(sampling_rates):
        sample_indices = np.arange(0, len(audio_data), sample_rate // Fs)
        sampled_signal = audio_data[sample_indices]
        reconstructed_signal = np.interp(np.arange(len(audio_data)), sample_indices, sampled_signal)
        st.write(f"🔊 {titles[i]} (Fs = {Fs} Hz)")
        st.audio(convert_to_wav(reconstructed_signal, sample_rate), format="audio/wav")

    # Function to plot time-domain signal
    def plot_time_domain(audio_signal, sample_rate, title, ax, color):
        N = min(1500, len(audio_signal))  # Only first 1500 samples
        t = np.linspace(0, N / sample_rate, num=N)
        ax.plot(t, audio_signal[:N], color=color)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title(title)

    # Function to plot frequency spectrum
    def plot_frequency_spectrum(audio_signal, sample_rate, title, ax, color):
        N = len(audio_signal)
        fft_data = np.fft.fft(audio_signal)
        fft_freqs = np.fft.fftfreq(N, 1 / sample_rate)
        positive_freqs = fft_freqs[:N // 2]
        positive_fft_data = np.abs(fft_data[:N // 2])
        ax.plot(positive_freqs, positive_fft_data, color=color)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Magnitude")
        ax.set_title(title)
        ax.set_xlim(0, sample_rate / 2)

    # Create 4x2 Subplots (Time Domain & Frequency Domain)
    fig, axs = plt.subplots(4, 2, figsize=(16, 16))

    # Original Signal (Time Domain & Frequency Domain)
    plot_time_domain(audio_data, sample_rate, "Original Signal (Time Domain)", axs[0, 0], "darkviolet")
    plot_frequency_spectrum(audio_data, sample_rate, "Original Signal Spectrum", axs[0, 1], "darkviolet")

    # Plot sampled signal (Time domain & Frequency domain)
    for i, Fs in enumerate(sampling_rates):
        sample_indices = np.arange(0, len(audio_data), sample_rate // Fs)
        sampled_signal = audio_data[sample_indices]
        reconstructed_signal = np.interp(np.arange(len(audio_data)), sample_indices, sampled_signal)

        # Time-domain plots (left column)
        plot_time_domain(reconstructed_signal, sample_rate, f"{titles[i]} (Time Domain)", axs[i+1, 0], colors[i])

        # Frequency-domain plots (right column)
        plot_frequency_spectrum(reconstructed_signal, sample_rate, f"{titles[i]} Spectrum", axs[i+1, 1], colors[i])

    # Adjust layout and display plot at the end
    plt.tight_layout()
    st.pyplot(fig)

