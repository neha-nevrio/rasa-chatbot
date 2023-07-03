# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType
from rasa_sdk.types import DomainDict
from rasa_sdk.events import UserUtteranceReverted
from llama_index import SimpleDirectoryReader, GPTListIndex, GPTVectorStoreIndex, LLMPredictor, PromptHelper, \
    ServiceContext, StorageContext, load_index_from_storage
from langchain import OpenAI
from dotenv import load_dotenv
import smtplib
import re
import os
import requests
import json

load_dotenv()


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "company_website_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        Link = os.getenv('NEVRIO_LINK')

        dispatcher.utter_template("utter_info", tracker, link=Link)

        return []


class AskForFullName(Action):
    def name(self) -> Text:
        return "action_ask_full_name"

    def run(
            self, dispatcher: CollectingDispatcher,
            tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(response="utter_ask_full_name", attachment="full_name")

        return []


class AskForEmailID(Action):
    def name(self) -> Text:
        return "action_ask_email_id"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(response="utter_ask_email_id", full_name=tracker.get_slot("full_name"),
                                 attachment="email_id")
        return []


class AskForPhoneNumber(Action):
    def name(self) -> Text:
        return "action_ask_phone_number"

    def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(response="utter_ask_phone_number", email_id=tracker.get_slot("email_id"),
                                 attachment="phone_number")
        return []


class ValidateInfoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_info_form"

    def validate_full_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `full_name` value."""

        # If the name is super short, it might be wrong.
        pattern = r'^[a-zA-Z]+([-\'\s][a-zA-Z]+)*$'
        name = slot_value
        if re.match(pattern, name) and len(name) >= 2:
            return {"full_name": name}

        dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")

        return {"full_name": None}

    def validate_email_id(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `email_id` value."""

        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        email = slot_value
        if re.match(regex, email):
            return {"email_id": email}

        dispatcher.utter_message(text=f"Please enter a valid email address.")

        return {"email_id": None}


class SendEmail(Action):

    def name(self) -> Text:
        return "action_send_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        full_name = tracker.get_slot("full_name")
        email_id = tracker.get_slot("email_id")

        try:

            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(os.getenv("SENDER_EMAIL_ID"), os.getenv("PASSWORD"))
                to_address = os.getenv('RECEIV_EMAILID')
                # to_address = to_address.removesuffix('[').remove(']').split(',')
                if to_address.startswith('[') and to_address.endswith(']'):
                    new_to_address = to_address[1:len(to_address)]
                    print(new_to_address)

                for email in to_address:
                    connection.sendmail(from_addr=os.getenv("SENDER_EMAIL_ID"),
                                        to_addrs=email,
                                    msg=f"Subject: IMPORTANT! \n\nName - {full_name} Email_id- {email_id}")


        except Exception as e:
            print(e)


class ActionSubmit(Action):

    def name(self) -> Text:
        return "action_submit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        Link = os.getenv('CANLENDLY_LINK')
        dispatcher.utter_message(response="utter_submit", full_name=tracker.get_slot("full_name"), link=Link)

        return []


class ActionJobHunt(Action):

    def name(self) -> Text:
        return "action_job"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        response = requests.get('https://www.jsonkeeper.com/b/1T0V')
        response.raise_for_status()

        jobs = response.json()["jobs"]

        dispatcher.utter_message(response="utter_job_vacancy")
        response_str = ""
        for job in jobs:
            response_str += "Job ID: {}\nTitle: {}\nDescription: {}\nStatus: {}\n\n".format(
                json.dumps(job["id"]),
                json.dumps(job["title"]),
                json.dumps(job["description"]),
                json.dumps(job["active"])
            )

        dispatcher.utter_message(response_str)

        return []


class OpenAIModel:
    def answerMe(question):
        storage_context = StorageContext.from_defaults(persist_dir='Store')
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine()
        response2 = query_engine.query(question)

        return response2


class ActionCustomFallback(Action):
    def name(self) -> Text:
        return "action_custom_fallback"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        answer = OpenAIModel.answerMe(str(text))

        dispatcher.utter_message(text=str(answer))

        return [UserUtteranceReverted()]
