from langchain.base_language import BaseLanguageModel
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate

from mid_prompt_gen.backend.midjourney import context as midjourney_context
from mid_prompt_gen.backend.abstract_classes import TextToImagePromptGenerator
from mid_prompt_gen.constants import INSTRUCTOR_USER_NAME


class MidjourneyPromptGenerator(TextToImagePromptGenerator):
    def __init__(self, llm: BaseLanguageModel):
        super().__init__(llm)

    def set_context(self):
        context_messages = []
        context_messages.append(SystemMessagePromptTemplate.from_template(
            "Here is some general information about the Midjourney company. ",
            additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(
            SystemMessagePromptTemplate.from_template(midjourney_context.midjourney_company_information,
                                                      additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(
            SystemMessagePromptTemplate.from_template(midjourney_context.midjourney_v5_general_description,
                                                      additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(
            SystemMessagePromptTemplate.from_template(midjourney_context.midjourney_v5_additional_description,
                                                      additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(SystemMessagePromptTemplate.from_template(
            "Now i will provide you some information about prompt engineering for Midjourney.",
            additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(
            SystemMessagePromptTemplate.from_template(midjourney_context.prompt_general_description,
                                                      additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        context_messages.append(SystemMessagePromptTemplate.from_template(midjourney_context.prompt_length,
                                                                       additional_kwargs={
                                                                           "name": INSTRUCTOR_USER_NAME}))
        context_messages.append(SystemMessagePromptTemplate.from_template(midjourney_context.prompt_grammer,
                                                                       additional_kwargs={
                                                                           "name": INSTRUCTOR_USER_NAME}))
        context_messages.append(SystemMessagePromptTemplate.from_template(midjourney_context.prompt_what_you_want,
                                                                       additional_kwargs={
                                                                           "name": INSTRUCTOR_USER_NAME}))
        context_messages.append(SystemMessagePromptTemplate.from_template(midjourney_context.prompt_details,
                                                                       additional_kwargs={
                                                                           "name": INSTRUCTOR_USER_NAME}))
        self.messages.context = context_messages

    def _set_human_message(self):
        """Human message which contains the input for the prompt generation"""
        human_template = """
                          Write a prompt for the text delimited by ```. 
                          Consider everything you learned about prompting and only provide the final text-to-image prompt without further details.
                          Take some inspiration from the format of the example prompts, but do not copy them.
                          The final output prompt should only contain visual descriptions.

                          ```{text}```
                         """
        self.messages.human_message = HumanMessagePromptTemplate.from_template(human_template)