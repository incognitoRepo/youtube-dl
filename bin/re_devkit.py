import requests
import json
import re
import webbrowser

URL = "https://regex101.com/api/regex"
HEADERS = {'content-type': 'application/json'}


class reDevKit:
  def __init__(self):
    self.payload: dict
    self.request_response: requests.Response
    self.apiurl: str
    self.browserurl: str

  def make_payload(self, regex, test, flags="gm", delimiter="\"", flavor="python"):
    d = {
        "regex": f"{regex}",
        "testString": f"{test}",
        "flags": f"{flags}",
        "delimiter": f"{delimiter}",
        "flavor": f"{flavor}",
    }
    self.payload = d
    return self

  def create(self, payload: dict = None):
    if not payload:
      payload = self.payload
    payload_json: str = json.dumps(payload)
    response = requests.request("POST", URL, data=payload_json, headers=HEADERS)
    print(response.text)
    self.request_response = response
    return self

  def openbrowser(self, response: requests.Response = None):
    if not response:
      response = self.request_response
    link, v = response.json()['permalinkFragment'], response.json()['version']
    apiurl = f"https://regex101.com/api/regex/{link}/{v}"
    browserurl = f"https://regex101.com/r/{link}/{v}"
    self.apiurl, self.browserurl = apiurl, browserurl
    webbrowser.open(browserurl)


def test():
  rgx = r"\s+[.]{3}\s+(?P<type>(return|exception) value):\s+(?P<data>.+)$"
  tststr = "                                               ...       return value: None"
  d = {
      "regex": rgx,
      "test": tststr,
  }
  redk = reDevKit()
  (redk.make_payload(**d)
   .create()
   .openbrowser())
  print("test not defined")


if __name__ == "__main__":
  test()
