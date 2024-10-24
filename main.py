import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# Gemini API endpoint
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

def encode_image_from_url(image_url):
    """
    Fetch an image from a URL and encode it to base64.
    """
    response = requests.get(image_url)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_image_description(image_url, api_key):
    """
    Get a description of the image using the Gemini 1.5 Flash API.
    """
    encoded_image = encode_image_from_url(image_url)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [
                {"inlineData": {"mimeType": "image/png", "data": encoded_image}},
                {"text": "Describe the image in great detail, analyzing the objects, people, or elements present, their appearance, colors, lighting, and textures. Focus on the mood, atmosphere, and how the composition creates a particular feeling or emotion. Discuss any interactions, gestures, or visual relationships between the elements, and the overall aesthetic impact of the image. Additionally, identify and describe the artistic or photographic style, considering factors such as techniques, influences, and distinctive visual characteristics that contribute to the image's overall presentation."}
            ]
        }]
    }
    
    response = requests.post(f"{GEMINI_API_ENDPOINT}?key={api_key}", headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

# Streamlit app
st.title("Image URL to Description Generator")
st.write("Enter an image URL and your Gemini API key to get a detailed description using Gemini 1.5 Flash API")

# Input for API key
api_key = st.text_input("Enter your Gemini API key:", type="password")

# Input for image URL
image_url = st.text_input("Enter the URL of the image:")

if st.button("Generate Description"):
    if api_key and image_url:
        try:
            # Display the image
            st.image(image_url, caption="Input Image", use_column_width=True)
            
            # Get and display the description
            with st.spinner("Generating description..."):
                description = get_image_description(image_url, api_key)
            st.subheader("Image Description:")
            st.write(description)
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while making the API request: {str(e)}")
            if "403" in str(e):
                st.error("This might be due to an invalid API key or insufficient permissions.")
            elif "404" in str(e):
                st.error("The API endpoint might be incorrect or the service is unavailable.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
    else:
        if not api_key:
            st.warning("Please enter your Gemini API key.")
        if not image_url:
            st.warning("Please enter an image URL.")

st.sidebar.markdown("### How to use")
st.sidebar.write("1. Enter your Gemini API key in the first text box.")
st.sidebar.write("2. Enter the URL of an image in the second text box.")
st.sidebar.write("3. Click the 'Generate Description' button.")
st.sidebar.write("4. Wait for the AI to analyze the image and provide a description.")
st.sidebar.write("5. The description will appear below the image.")

st.sidebar.markdown("### Note")
st.sidebar.write("Your API key is not stored and is only used for this session.")
st.sidebar.write("Make sure to use a valid Gemini API key with access to the Gemini 1.5 Flash Vision model.")
st.sidebar.write("If you encounter errors, double-check your API key and ensure you have the necessary permissions.")