from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain import prompts
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import tool
from PIL import Image
from dotenv import load_dotenv
import os 
import requests
import base64
import io
import streamlit as st

load_dotenv()
openai_nvapi_key = os.getenv("OPENAI_NVAPI_KEY")
stablediff_nvapi_key = os.getenv("STABLEDIFF_NVAPI_KEY")

# re-writing the input promotion title in to appropriate image_gen prompt 
def llm_rewrite_to_image_prompts(user_query: str) -> str:
    prompt = prompts.ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Summarize the following user request into a concise topic, in 2 sentences, for image generation. 
                It MUST follow this format: An iconic, joyful, and realistic image that grabs attention of, WITHOUT text, no amputations, NO faces, bright, vibrant.
                Your output MUST be in english.
                """,
            ),
            ("user", "{input}"),
        ]
    )
    model = ChatNVIDIA(model="meta/llama-3.1-405b-instruct", api_key = openai_nvapi_key)
    chain = ( prompt | model | StrOutputParser() )
    out= chain.invoke({"input": user_query})
    return out.strip()

@tool
def generate_image(prompt:str) -> str:
    """
    Generate a high quality image from text
    Args:
        prompt: input text used as source to generate the image. 
    """
    gen_prompt = llm_rewrite_to_image_prompts(prompt)
    #print(gen_prompt)
    print("Start generating image with llm re-write prompt:", gen_prompt)
    
    invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-xl"
    
    headers = {
        "Authorization": f"Bearer {stablediff_nvapi_key}",
        "Accept": "application/json",
    }
    
    payload = {"text_prompts": [{"text": gen_prompt, "weight": 1}, 
                                {"text":  "" , "weight": -1}],
    "cfg_scale": 5,
    "sampler": "K_DPM_2_ANCESTRAL",
    "seed": 0,
    "steps": 25
    }
    
    response = requests.post(invoke_url, headers=headers, json=payload)
    
    response.raise_for_status()
    response_body = response.json()
    #print(response_body['artifacts'])
    imgdata = base64.b64decode(response_body["artifacts"][0]["base64"])
    return io.BytesIO(imgdata)


def output_to_tool_execution(out):
    tool_calls = out.tool_calls
    if len(tool_calls) > 0:
        if 'args' in tool_calls[0]:
            prompt = tool_calls[0]['args']['prompt']
            output = generate_image.invoke(prompt)
        else:
            print('### out.tool_calls', out.tool_calls[0].keys())
            output = None
            # "cannot find input prompt from llm output, please rerun again"
    else:
        print("----------------", out)
        print('### out.tool_calls', out.tool_calls)
        output = None
        #"Agent did not find generate_image tool, please check the tool binding is succesful"
    return output

llm = ChatNVIDIA(model='meta/llama-3.1-405b-instruct', api_key= openai_nvapi_key)
llm_with_img_gen_tool = llm.bind_tools([generate_image], tool_choice="generate_image")

# Digital Artist Agent with langchain
digital_artist = (
    llm_with_img_gen_tool
    | output_to_tool_execution
)