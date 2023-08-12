# spindle

API & cloud agnostic library for extensibly orchestrating relational actions using cloud functions.

### backstory

We use Serverless and AWS at my job to pull data from API endpoints. Oftentimes we'll run into issues like:
- *"what if the sequence of API calls takes longer than my function timeout?"* 
- *"how do I manage rate limiting across multiple invocations of my function?"*
- *"how can I cleanly write code that is dependant on other API calls, but also events its result to an event pipeline?"*

The main impetus for me, was the last question. I didn't want my teammates to read the garbage code I cobbled together walking an API by throwing payloads back onto a queue and triggering a lambda and back onto a queue and triggering a lambda...you get the point.

Thus, as a personal project, I started this library.

#### do you sew or something?

Nope! - but I did read the Wheel of Time. It's hard to pick a good name, and as I was thinking about all the metaphors, spindle popped into my head -- I wasn't familiar with a popular library that used that imagery before. It also wouldn't be the first library abiding by illustrative names: pandas has unstack and stack, melt and unmelt. There's BeautifulSoup, Bokeh & Seaborn, fuzzywuzzy, pendulum, etc. Anyways, whatever the metaphor, I wanted to avoid the junkyard of "run", "execute", "fetch", "go", "do", "trigger", "start". I don't think any of those capture the complexitiy you can manage (or create) with this pattern. 

#### why cloud functions and not another service?

You certainly do pay a premium for FaaS, but, for a team that has solely used serverless technologies and approaches are you prepared to ask them to manage a server? Or take on a new service?  Will you advocate changing cloud providers because the compute is cheaper as well? It's a spectrum, and you'll need to weigh the pros and cons yourself. For us, we had a lot of existing patterns and libraries that utilized SNS, SQS, and Lambdas. Switching to EC2, Step Functions, or Batch would have been a bigger lift that we couldn't deliver fast enough.

#### why are there kwargs everywhere?

Well, I don't know what your requirements are. Maybe you need to grab an eTag at runtime, or fetch an access token from DynamoDB, or pass a value down a few relationships. I chose kwargs with the hope that these possibilities could be solved easier.

## example

We want to pull from an imaginary API that has three tiers: grandparents, parents, and children. We need to support that the total sum of all these calls may easily exhaust our timeout, so I can't expect to use only one lambda invocation. In this example, the triggering message is some payload with the 'trigger' key.

```

class Trigger(spindle.Spool):

    def unwind(**kwargs):
        for grandparent in self.session.get(url='grandparents'):
            grandparent_ = Grandparent(grandparent)
            grandparent_.stitch() # event to queue/topic for processing
            grandparent_.backstitch() # event to _triggering_ queue, to continue crawling API
            yield grandparent

class Grandparents(spindle.Spool):

    def unwind(**kwargs):
        for parent in self.session.get(url='parents'):
            parent_ = Parent(parent)
            parent_.stitch()  # event to queue/topic for processing
            parent_.backstitch()  # event to _triggering_ queue, to continue cracchefwling API
            yield parent

    def stitch(**kwargs):
        boto3.client('sqs').send_message(**kwargs)

    def backstitch(**kwargs):
        boto3.client('sqs').send_message(**kwargs)


class Parents(spindle.Spool):
    def unwind(**kwargs):
        for child in self.session.get(url='children'):
            child_ = Child(child)
            child_.stitch()
            # child_.backstitch() end of line here, so no need to rethread
            yield child_

    def stitch(**kwargs):
        boto3.client('sqs').send_message(**kwargs)

    def backstitch(**kwargs):
        boto3.client('sqs').send_message(**kwargs)


def lambda_handler(event, context):
    for record in json.loads(event['Records']):
        s = Spindle(record)
        s.set_attributes(session=requests.Session())
        s.weave()

```

## notes & gotchas
- leverage your cloud providers features like:
  - reserved concurrency & message timeouts to help manage rate-limits
  - partial batch response for retries (while not paying for a sleeping invocation!)
