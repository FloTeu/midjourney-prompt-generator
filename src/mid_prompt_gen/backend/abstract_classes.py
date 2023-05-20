from abc import abstractmethod, ABC
from typing import List

from langchain.base_language import BaseLanguageModel
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate
from langchain.chains import LLMChain

from mid_prompt_gen.backend.data_classes import PromptGenerationMessages
from mid_prompt_gen.constants import INSTRUCTOR_USER_NAME

class TextToImagePromptGenerator(ABC):
    """
    Abstract prompt generator class. Subclasses have the ability to generate text-to-image prompts.
    """

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.messages: PromptGenerationMessages = PromptGenerationMessages(instruction_message=self._get_system_instruction())

    def _get_system_instruction(self):
        """System message to instruct the llm model how he should act"""
        return SystemMessagePromptTemplate.from_template("""
            You are a helpful assistant in helping me create text-to-image prompts.
            """)

    def set_prompt_examples(self, prompt_examples: List[str]):
        """
        Extends self.messages with prompt examples of Text-to-Image AI
        Few shot learning is implemented in this function
        sets self.prompt_examples_provided to True
        """
        messages = [SystemMessagePromptTemplate.from_template(
            "Here are some example Midjourney prompts. Try to understand the underlying format of prompts in order to create new creative prompts yourself later. ",
            additional_kwargs={"name": INSTRUCTOR_USER_NAME})]
        for i, example_prompt in enumerate(prompt_examples):
            messages.append(
                SystemMessagePromptTemplate.from_template(f'Prompt {i}: "{example_prompt}". ',
                                                          additional_kwargs={"name": INSTRUCTOR_USER_NAME}))
        self.messages.prompt_examples = messages

    def _set_human_message(self):
        """Human message which contains the input for the prompt generation"""
        human_template = """
                          Write a prompt for the text delimited by ```. 
                          Consider everything you learned about prompting and only provide the final text-to-image prompt without further details.
                          The final output prompt should only contain visual descriptions.
                            ```{text}```
                         """
        self.messages.human_message = HumanMessagePromptTemplate.from_template(human_template)

    @abstractmethod
    def set_context(self):
        """Extends self.messages with context of Text-to-Image AI and sets self.context_known to True"""
        raise NotImplementedError

    def _get_prompt_gen_chain(self) -> LLMChain:
        if not self.messages.are_prompt_examples_set():
            raise ValueError("Prompt examples are not yet provided")
        if not self.messages.is_context_known():
            self.set_context()
        if not self.messages.is_human_message_set():
            self._set_human_message()

        chat_prompt = self.messages.get_chat_prompt_template()
        return LLMChain(llm=self.llm, prompt=chat_prompt)

    def generate_prompt(self, text):
        llm_chain = self._get_prompt_gen_chain()
        return llm_chain.run(text=text)