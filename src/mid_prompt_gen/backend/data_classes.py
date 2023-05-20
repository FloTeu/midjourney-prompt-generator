from typing import List, Optional
from dataclasses import dataclass
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate
from langchain.prompts.chat import BaseMessagePromptTemplate

@dataclass
class PromptGenerationMessages:
    instruction_message: SystemMessagePromptTemplate
    context: Optional[List[BaseMessagePromptTemplate]] = None
    prompt_examples: Optional[List[BaseMessagePromptTemplate]] = None
    human_message: Optional[HumanMessagePromptTemplate] = None

    def is_context_known(self):
        return bool(self.context)

    def are_prompt_examples_set(self):
        return bool(self.prompt_examples)

    def is_human_message_set(self):
        return bool(self.human_message)

    def get_chat_prompt_template(self) -> ChatPromptTemplate:
        assert self.instruction_message != None
        assert self.context != None
        assert self.prompt_examples != None
        assert self.human_message != None
        messages = [
            self.instruction_message,
            *self.context,
            *self.prompt_examples,
            self.human_message
        ]
        return ChatPromptTemplate.from_messages(messages)
