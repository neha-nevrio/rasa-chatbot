# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from rasa_sdk.events import UserUtteranceReverted, EventType
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from llama_index import SimpleDirectoryReader, VectorStoreIndex
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

class OpenAIModel:
    def __init__(self):
        self.index = None
        self.chat_engine = None

    def initialize(self):
        documents = SimpleDirectoryReader('Knowledge').load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        self.chat_engine = self.index.as_chat_engine()

    def answer_me(self, question):
        response = self.chat_engine.chat(question)
        return response


class ActionCustomFallback(Action):
    def __init__(self):
        self.user_sessions = {}

    def name(self) -> Text:
        return "action_custom_fallback"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        try:

            self.session = OpenAIModel()
            self.session.initialize()


            question = tracker.latest_message['text']

            answer = self.session.answer_me(str(question))

            dispatcher.utter_message(str(answer))

            return [UserUtteranceReverted()]

        except Exception as e:
            dispatcher.utter_message(text=str(e))
