# 8237a95f18d2aed79cba61ef9c365dc32191484659210bb42cdbe07b45fff04bacbf911956b7105d66e26
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkApi
import requests
import json
import re

token = '8237a95f18d2aed79cba61ef9c365dc32191484659210bb42cdbe07b45fff04bacbf911956b7105d66e26'

vk_session = VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def send(id, text):
    vk_session.method('messages.send', {
                      'user_id': id, 'message': text, 'random_id': 0})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            if event.text.lower() == 'начать':
                send(event.user_id, 'Здравствуйте! Ждем ссылку на задание!\nПримеры ссылок: \n1. https://uchebnik.mos.ru/exam/test/selftest/spec/99999/…\n2. https://uchebnik.mos.ru/exam/test/training_spec/99999/…\n3. https://uchebnik.mos.ru/exam/test/test_by_binding/99999/…')
            elif bool(re.search(r"(selftest\/spec|training_spec|test_by_binding)\/([\w]+)", msg)) or 'attach1_url' in event.attachments:
                if 'attach1_url' in event.attachments:
                    msg = event.attachments['attach1_url']
                settings = list(re.findall(
                    r"(selftest\/spec|training_spec|test_by_binding)\/([\w]+)", msg)[0])
                if settings[0] == 'test_by_binding':
                    settings[0] = 'homework'
                else:
                    settings[0] = 'spec'
                if len(settings) == 2:
                    url = "https://uchebnik.mos.ru/exam/rest/secure/testplayer/group"

                    payload = json.dumps({"test_type": "training_test",
                                          "generation_context_type": settings[0], "generation_by_id": settings[1]})
                    headers = {
                        'Content-Type': 'application/json',
                        'Cookie': 'udacl=mesh; auth_type=MOSRU; auth_token=9a40552f7a82641cd43d265cfffd3303; user_id=5331602; profile_id=16025483; profile_type=student; last_used_user_id=5331602; last_used_profile_id=16025483; last_used_profile_type=student; default_class_level_id=10'
                    }

                    response = requests.request(
                        "POST", url, headers=headers, data=payload)

                    pred = response.json()
                    send(event.user_id,
                         'Номер задания: {0}.\nРабота началась.\n\n'.format(settings[1]))
                    for task in pred['training_tasks']:
                        question = task['test_task']['question_elements'][0]['text']
                        type_of_question = task['test_task']['answer']['type']
                        if type_of_question == "answer/multiple":
                            right_answer = task['test_task']['answer']['right_answer']['ids']
                            variants = task['test_task']['answer']['options']
                            for i in variants:
                                if i['id'] in right_answer:
                                    right_answer[right_answer.index(
                                        i['id'])] = i['text']
                            right_answer = ';\n'.join(right_answer)
                        elif type_of_question == "answer/single":
                            right_answer = task['test_task']['answer']['right_answer']['id']
                            variants = task['test_task']['answer']['options']
                            for i in variants:
                                if i['id'] in right_answer:
                                    right_answer = i['text']
                        elif type_of_question == 'answer/string':
                            right_answer = task['test_task']['answer']['right_answer']['string']
                        elif type_of_question == 'answer/match':
                            answers = task['test_task']['answer']['right_answer']['match']
                            variants = task['test_task']['answer']['options']
                            right_answer = []
                            for key, value in answers.items():
                                temp = [key]+value
                                right_answer.append(temp)
                            for i in variants:
                                for a in right_answer:
                                    if i['id'] in a:
                                        url = ''
                                        try:
                                            if i['content'][0]['file']['type'] == 'file/image':
                                                url = 'https://uchebnik.mos.ru/exam{0}'.format(
                                                    i['content'][0]['file']['relative_url'])
                                        except:
                                            pass
                                        right_answer[right_answer.index(
                                            a)][right_answer[right_answer.index(a)].index(i['id'])] = i['text']+' ' + url + ' '
                            answer_for_user = ''
                            for i in right_answer:
                                answer_for_user += '\n{0} -> {1};\n'.format(
                                    i[0], ' ,'.join(i[1:]))
                            right_answer = answer_for_user
                        send(event.user_id, 'ВОПРОС: {0}\nОТВЕТ: {1}\n\n'.format(
                            question, right_answer))
            else:
                send(event.user_id, 'Неверная ссылка')
pred = None
