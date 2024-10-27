import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO
from mistralai import Mistral

def encode_image_from_url(image_url):
    """
    Fetch an image from a URL and encode it to base64.
    """
    response = requests.get(image_url)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def call_mistral_api(api_key, image_base64, prompt):
    """
    Get a description of the image using the Mistral Pixtral API.
    """
    try:
        client = Mistral(api_key=api_key)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            }
        ]
        
        chat_response = client.chat.complete(
            model="pixtral-12b-2409",
            messages=messages
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Mistral API call failed: {str(e)}")

# Streamlit app
st.title("Image URL to Description Generator")
st.write("Enter an image URL and your Mistral API key to get a detailed description using the Pixtral model")

# Input for API key
api_key = st.text_input("Enter your Mistral API key:", type="password")

# Input for image URL
image_url = st.text_input("Enter the URL of the image:")

if st.button("Generate Description"):
    if api_key and image_url:
        try:
            # Display the image
            st.image(image_url, caption="Input Image", use_column_width=True)
            
            # Encode the image
            encoded_image = encode_image_from_url(image_url)
            
            # Define the prompt
            prompt = "Based on this image, create a detailed prompt for generating a new image. Describe the scene, key elements, colors, lighting, mood, and composition, including specific visual features that should be replicated or stylized in a new version of the image. Ensure the prompt includes keywords for artistic style, perspective, and any relevant objects or characters, so it’s ready for use in image generation with another AI model. Give me the prompt in a paragraph format"
            
            # Get and display the description
            with st.spinner("Generating description..."):
                description = call_mistral_api(api_key, encoded_image, prompt)
            st.subheader("Image Description:")
            st.write(description)
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while fetching the image: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if "unauthorized" in str(e).lower():
                st.error("This might be due to an invalid API key or insufficient permissions.")
    else:
        if not api_key:
            st.warning("Please enter your Mistral API key.")
        if not image_url:
            st.warning("Please enter an image URL.")

st.sidebar.markdown("### How to use")
st.sidebar.write("1. Enter your Mistral API key in the first text box.")
st.sidebar.write("2. Enter the URL of an image in the second text box.")
st.sidebar.write("3. Click the 'Generate Description' button.")
st.sidebar.write("4. Wait for the AI to analyze the image and provide a description.")
st.sidebar.write("5. The description will appear below the image.")

st.sidebar.markdown("### Note")
st.sidebar.write("Your API key is not stored and is only used for this session.")
st.sidebar.write("Make sure to use a valid Mistral API key with access to the Pixtral model.")
st.sidebar.write("If you encounter errors, double-check your API key and ensure you have the necessary permissions.")
