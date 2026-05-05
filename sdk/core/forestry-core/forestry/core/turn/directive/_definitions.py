from typing import ContextManager, Generic, TypeVar, TYPE_CHECKING
import abc
import time

#: Question and answer types
QuestionType = TypeVar("QuestionType")
AnswerType = TypeVar("AnswerType")

if TYPE_CHECKING:
    #: Avoid circular import issues
    from forestry.core.turn import Turn

class Directive(ContextManager["Turn"], abc.ABC, Generic[QuestionType, AnswerType]):
    """Directive interface as steps making upp a pipe that turns questions into answers"""
    
    @abc.abstractmethod
    def process(self, question: QuestionType) -> AnswerType:
        """Process a question and return an answer i.e. turn"""

    @abc.abstractmethod
    def open(self) -> None:
        """Open new session when none exists."""

    @abc.abstractmethod
    def close(self) -> None:
        """Close session when not external."""

    def sleep(self, duration: float) -> None:
        time.sleep(duration)