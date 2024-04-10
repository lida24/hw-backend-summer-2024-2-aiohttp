from dataclasses import dataclass, field

from app.quiz.models import Theme, Question


@dataclass
class Database:
    # TODO: добавить поля admins и questions
    themes: list[Theme] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)

    @property
    def next_theme_id(self) -> int:
        return len(self.themes) + 1

    @property
    def next_question_id(self) -> int:
        return len(self.questions) + 1

    def clear(self):
        self.themes.clear()
        self.questions.clear()
