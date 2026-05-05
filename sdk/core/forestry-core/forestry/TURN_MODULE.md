# Forestry Turn module
This module explains the Forestry turn development of turning questions to answers where the transition is responsible for calling a service.  A transition might be an HTTP call or local AI interaction or just testing.

## Turn
Naming derives from AI where a turn is a pipe of directives that can edit a question into an editable answer.  An adjacency pair is a bearer of the question and answer.  A directive operates on the adjacency pair where the last directive wraps the transition.  Directives can capture errors embedding into an answer that can be analyzed by an answer analyzer.

There are default directives like retrying and logging.

A pipeline may be created by a SDK developer:

```python
from Forestry.core.turn import Pipeline, AnswerType
from Forestry.core.turn.directives import RetryDirective, DirectivePosition

class MontyClient:
    def __init__(self, **args: Any) -> None:
        """ Pop transition then directives from arguments to make a pipeline
        """
        transition = args.pop('transition', None)
        if transition is None:
            raise RuntimeError("Unable to get transition")

        retry_directive = args.pop('retry-directive', None)
        if retry_directive is None:
            retry_directive = RetryDirective(DirectivePosition.Retry, **args)
        
        directives = [ retry_directive ] ## add more directives by position

        self._pipeline = Pipeline(transition, directives=directives)

    def get_monty_stuff(self, **args: Any) -> AnswerType
        question = self._pipeline.transition.create_question(**args)
        answer = self._pipeline.process(question, **args)
        return answer
```

Then use the client:
```python
from Forestry.core.security import MontySecurity
from Forestry.core.http import HttpTransition
from Forestry.monty import MontyClient

security = MontySecurity("api-key")
endpoint = "http://service.Forestry.se
transition = new HttpTransition(endpoint, security)

client = FooServiceClient(transition)
answer = client.get_monty_stuff()
```