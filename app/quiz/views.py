from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import request_schema, response_schema, querystring_schema, docs

from app.quiz.schemes import (
    ThemeSchema,
    ThemeListSchema,
    QuestionSchema,
    ThemeIdSchema,
    ListQuestionSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(
        tags=["VK Bot"],
        summary="Add new theme",
        description="Add new theme to database",
    )
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title = self.data["title"]
        if await self.store.quizzes.get_theme_by_title(title):
            raise HTTPConflict(reason="Theme with such title already exists")
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(
        tags=["VK Bot"], summary="List themes", description="List themes from database"
    )
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        raw_themes = [ThemeSchema().dump(theme) for theme in themes]
        return json_response({"themes": raw_themes})


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=["VK Bot"],
        summary="Add new question",
        description="Add new question to database",
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data["title"]
        if await self.store.quizzes.get_question_by_title(title):
            raise HTTPConflict(reason="Question with such title already exists")
        theme_id = self.data["theme_id"]
        if not await self.store.quizzes.get_theme_by_id(theme_id):
            raise HTTPNotFound(reason="Theme with such id doesn't exist")
        answers = self.data["answers"]
        if len(answers) < 2:
            raise HTTPBadRequest(
                reason="Incorrect format of answers to the question. Please check the accuracy of filling in the answer fields"
            )
        correct_answers = [answer for answer in answers if answer["is_correct"]]
        if len(correct_answers) != 1:
            raise HTTPBadRequest(
                reason="Incorrect format of answers to the question. Please check the accuracy of filling in the answer fields"
            )
        question = await self.store.quizzes.create_question(
            title=title, theme_id=theme_id, answers=answers
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=["VK Bot"],
        summary="List questions",
        description="List questions from database",
    )
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        try:
            theme_id = self.request.query.get("theme_id")
        except KeyError:
            theme_id = None
        questions = await self.store.quizzes.list_questions(theme_id)
        raw_questions = [QuestionSchema().dump(question) for question in questions]
        return json_response(data={"questions": raw_questions})
