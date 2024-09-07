import os
import langcodes
import google.generativeai as genai
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from warnings import filterwarnings



def streamlit_config():

    # page configuration
    st.set_page_config(page_title='YouTube')

    # page header transparent color and Removes top padding 
    page_background_color = """
    <style>

    [data-testid="stHeader"] 
    {
    background: rgba(0,0,0,0);
    }

    .block-container {
        padding-top: 0rem;
    }

    </style>
    """
    st.markdown(page_background_color, unsafe_allow_html=True)

    # title and position
    add_vertical_space(2)
    st.markdown(f'<h2 style="text-align: center;">YouTube Transcript Summarizer with GenAI</h2>',
                unsafe_allow_html=True)
    add_vertical_space(2)



def extract_languages(video_id):

    # Fetch the List of Available Transcripts for Given Video
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Extract the Language Codes from List ---> ['en','ta']
    available_transcripts = [i.language_code for i in transcript_list]

    # Convert Language_codes to Human-Readable Language_names ---> 'en' into 'English'
    language_list = list({langcodes.Language.get(i).display_name() for i in available_transcripts})

    # Create a Dictionary Mapping Language_names to Language_codes
    language_dict = {langcodes.Language.get(i).display_name():i for i in available_transcripts}

    return language_list, language_dict



def extract_transcript(video_id, language):
    
    try:
        # Request Transcript for YouTube Video using API
        transcript_content = YouTubeTranscriptApi.get_transcript(video_id=video_id, languages=[language])
    
        # Extract Transcript Content from JSON Response and Join to Single Response
        transcript = ' '.join([i['text'] for i in transcript_content])

        return transcript
    
    
    except Exception as e:
        add_vertical_space(5)
        st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)



def generate_summary(transcript_text):

    try:
        # Configures the genai Library
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

        # Initializes a Gemini-Pro Generative Model
        model = genai.GenerativeModel(model_name = 'gemini-pro')  

        # Define a Prompt for AI Model
        prompt = """You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video, 
                    providing the important points are proper sub-heading in a concise manner (within 500 words). 
                    Please provide the summary of the text given here: """
        
        response = model.generate_content(prompt + transcript_text)

        return response.text

    except Exception as e:
        add_vertical_space(5)
        st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)


 
def main():

    # Filter the Warnings
    filterwarnings(action='ignore')

    # Load the Environment Variables
    load_dotenv()

    # Streamlit Configuration Setup
    streamlit_config()

    # Initialize the Button Variable
    button = False

    with st.sidebar:

        image_url = 'https://raw.githubusercontent.com/gopiashokan/Youtube-Data-Harvesting-and-Warehousing/main/youtube_banner.JPG'
        st.image(image_url, use_column_width=True)
        add_vertical_space(2)

        # Get YouTube Video Link From User 
        video_link = st.text_input(label='Enter YouTube Video Link')

        if video_link:
            # Extract the Video ID From URL
            video_id = video_link.split('=')[1].split('&')[0]

            # Extract Language from Video_ID
            language_list, language_dict = extract_languages(video_id)
            
            # User Select the Transcript Language
            language_input = st.selectbox(label='Select Transcript Language', 
                                        options=language_list)
            
            # Get Language_code from Dict
            language = language_dict[language_input]

            # Click Submit Button
            add_vertical_space(1)
            button = st.button(label='Submit')
        

    # User Enter the Video Link and Click Submit Button
    if button and video_link:
        
        # UI Split into Columns
        _, col2, _ = st.columns([0.07,0.83,0.1])

        # Display the Video Thumbnail Image
        with col2:
            st.image(image=f'http://img.youtube.com/vi/{video_id}/0.jpg', 
                     use_column_width=True)

        # Extract Transcript from YouTube Video
        add_vertical_space(2)
        with st.spinner(text='Extracting Transcript...'):
            transcript_text = extract_transcript(video_id, language)

        # Generating Summary using Gemini AI
        with st.spinner(text='Generating Summary...'):
            summary = generate_summary(transcript_text)

        # Display the Summary
        if summary:
            st.write(summary)
        


if __name__ == '__main__':
    
    try:
        main()

    except Exception as e:
        add_vertical_space(5)
        st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

