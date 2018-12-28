"""
This is a python wrapper for Kasisto NLU API Request
"""

import requests


URL = "http://localhost:8090/kai/api/v1/nlu"

HEADER = {
    "authKey": "T328JSS382RN",
    "secret": "5a04bfef-39eb-435a-a0d0-b271392790bb"}

REQUEST_TEMPLATE={
    "vpa_request": {
        "question": "what can you do",
        "version_info": {
            "api_version": "1.0"
        },
        "custom_context": {
            "deviceInfo": {
                "device_model": "test",
                "device_type": "test",
                "device_os": "test"
            }
        },
        "user_context": {
            "user_id": "andrew",
            "token": "test",
            "token_type": "kai",
        }
    }
}


class NluRequest:

    def __init__(self, utterance):
        self.body = REQUEST_TEMPLATE
        self.body['vpa_request']['question'] = utterance
        self.header = HEADER

    def load(self, utterance):
        self.body['vpa_request']["question"] = utterance

    def post(self):
        return make_request(URL, self.header, self.body)


class NluResponse:
    def __init__(self, resp_dict):
        self.current = resp_dict['currentIntent']['intents']
        self.final = resp_dict['finalIntent']['intents']
        self.parseroutputs = resp_dict['parserOutputs']
        print(resp_dict)

NLU = NluRequest("how bad can it be?")

def NluApi(utterance):
    NLU.load(utterance)
    response = NLU.post()
    return response

def make_request(url, headers, body):
    r = requests.post(url, json=body, headers=headers)
    print(r.status_code, r.reason)
    if r.text == 'null':
        print(body)

    return eval((r.text).replace('null', 'None').replace("false", "False").replace('true', "True"))




if __name__ == "__main__":
    first_utterance = "How can I add money to my bank account?"
    nlu = NluRequest(first_utterance)
    response = nlu.post()
    print(response)
    NLU.load(first_utterance)