from spindle.spindle import Spindle
from spindle.spool import Spool
import requests
import boto3


class Company(Spool):
    key = "company"

    def __init__(self, body):
        self.__body = body

    def unwind(self, **kwargs):
        for farm in self.session.post(url=""):
            farm_ = Farm(farm)
            farm_.stitch()
            farm_.backstitch()
            yield farm_

    def stitch(self, **kwargs):
        self.sqs_client.send_message(queue="QUEUE FOR PROCESSING" ** kwargs)

    def backstitch(self, **kwargs):
        self.sqs_client.send_message(queue="QUEUE FOR RETRIGGERING" ** kwargs)


class Farm(Spool):
    key = "farm"

    def __init__(self, body):
        self.__body = body

    def unwind(self, **kwargs):
        for field in self.session.post(url=""):
            field_ = Field(field)
            field_.stitch()
            field_.backstitch()
            yield field_

    def stitch(self, **kwargs):
        self.sqs_client.send_message(queue="QUEUE FOR PROCESSING" ** kwargs)

    def backstitch(self, **kwargs):
        self.sqs_client.send_message(queue="QUEUE FOR RETRIGGERING" ** kwargs)


class Field(Spool):
    key = "farm"

    def __init__(self, body):
        self.__body = body

    def unwind(self, **kwargs):
        """End of the line here, we don't resubmit this."""
        return

    def stitch(self, **kwargs):
        self.sqs_client.send_message(queue="QUEUE FOR PROCESSING" ** kwargs)

    def backstitch(self, **kwargs):
        self.sqs_client.send_message(queue="QUEUE FOR RETRIGGERING" ** kwargs)


def handler(event, context):
    for record in event.records:
        s = Spindle(key=None, body=record.body)

        s.set_attributes(session=requests.Session(headers={}), sqs_client=boto3.client("sqs"))

        s.weave()
