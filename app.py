import streamlit as st
import os, sys
import math
import requests
from typing import List
from io import BytesIO
from mid_prompt_gen.frontend.session import update_request, SessionState
from mid_prompt_gen.frontend.crawling_fns import crawl_midjourney, login_to_midjourney
from mid_prompt_gen.frontend.data_classes import MidjourneyImage
from mid_prompt_gen.backend.prompt_gen import MidjourneyPromptGenerator
from langchain.chat_models.openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = st.secrets["open_ai_api_key"]

MAX_IMAGES_PER_ROW = 4


@st.cache_data
def image_url2image_bytes_io(image_url: str) -> BytesIO:
    response = requests.get(image_url)
    return BytesIO(response.content)

def split_list(list_obj, split_size):
    return [list_obj[i:i+split_size] for i in range(0, len(list_obj), split_size)]

def display_midjourney_images(midjourney_images: List[MidjourneyImage]):
    """ Displays already crawled midjourney images with prompts to frontend.
    """
    progress_text = "Crawling in progress. Please wait."
    crawling_progress_bar = st.progress(0, text=progress_text)
    display_images = st.empty()
    display_cols = display_images.columns(MAX_IMAGES_PER_ROW)
    for j, midjourney_images_splitted_list in enumerate(split_list(midjourney_images, MAX_IMAGES_PER_ROW)):
        for i, midjourney_image in enumerate(midjourney_images_splitted_list):
            crawling_progress_bar.progress(math.ceil(100 / len(midjourney_images) * ((j * MAX_IMAGES_PER_ROW) + i)) + 1,
                                           text=progress_text)
            image_bytes_io: BytesIO = image_url2image_bytes_io(midjourney_image.image_url)
            display_cols[i].image(image_bytes_io)
            #color = "black" if not midjourney_image.selected else "green"
            #display_cols[i].markdown(f":{color}[{(j * MAX_IMAGES_PER_ROW) + i + 1}. {mba_product.title}]")
            display_cols[i].write(f"{(j * MAX_IMAGES_PER_ROW) + i + 1}. Prompt: {midjourney_image.prompt}")

    crawling_progress_bar.empty()

def main():

    st.header("Midjourney Few Shot Prompt Generator")
    st.sidebar.subheader("1. Midjourney Login")
    st.sidebar.info("*prompt search is only available for authenticated midjourney users")
    st.sidebar.text_input("Midjourney Email", value=os.environ.get("user_name", ""), key="mid_email")
    st.sidebar.text_input("Midjourney Password", type="password", value=os.environ.get("password", ""), key="mid_password")
    st.sidebar.button("Login", on_click=login_to_midjourney, key="button_midjourney_login")

    st.sidebar.subheader("2. Midjourney Crawling")
    st.sidebar.text_input("Search Term", key="search_term", on_change=update_request)
    if st.sidebar.button("Start Crawling", on_click=crawl_midjourney, key="button_midjourney_crawling"):
        session_state: SessionState = st.session_state["session_state"]
        display_midjourney_images(session_state.crawling_data.midjourney_images)

    if "session_state" in st.session_state:
        session_state: SessionState = st.session_state["session_state"]
        st.sidebar.subheader("3. Prompt Generation")
        midjourney_images = session_state.crawling_data.midjourney_images
        selected_prompts = st.sidebar.multiselect("Select Designs for prompt generation:", [i+1 for i in range(len(midjourney_images))], on_change=display_midjourney_images, args=(session_state.crawling_data.midjourney_images,), key='selected_prompts')
        st.sidebar.text_input("Prompt Gen Input", key="prompt_gen_input")
        if st.sidebar.button("Prompt Generation", on_click=display_midjourney_images, args=(session_state.crawling_data.midjourney_images,), key="button_prompt_generation"):
            temperature = 0.7
            llm = ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo")
            midjourney_prompt_gen = MidjourneyPromptGenerator(llm)
            prompts = [mid_img.prompt for i, mid_img in enumerate(midjourney_images) if (i+1) in selected_prompts]

            # Subset of elements based on indexes
            #prompts_subset = [prompts[i-1] for i in selected_prompts]

            midjourney_prompt_gen.set_few_shot_examples(prompts)
            st.subheader("Generated Prompt")
            llm_output = midjourney_prompt_gen.generate(text=st.session_state["prompt_gen_input"])
            st.write(llm_output)




if __name__ == "__main__":
    main()
