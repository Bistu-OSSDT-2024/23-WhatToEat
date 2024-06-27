#WhatToEat/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import os
from django.conf import settings
import base64
from zhipuai import ZhipuAI

def index(request):
    return render(request, 'index.html')

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_encoded

def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        upload_dir = os.path.join(settings.BASE_DIR, 'temp')
        os.makedirs(upload_dir, exist_ok=True)
        uploaded_file = request.FILES['file']
        file_path = os.path.join(upload_dir, 'upload_photo.jpg')

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        selected_option = request.POST.get('dropdown', '未选择')
        option_file_path = os.path.join(upload_dir, 'option.txt')

        with open(option_file_path, 'w', encoding='utf-8') as option_file:
            option_file.write(selected_option)

        return JsonResponse({"message": "图片上传成功，正在解析中！"})
    return JsonResponse({"message": "上传失败！"}, status=400)

def run_python_code(request):
    try:
        print('开始运行')
        file_path = os.path.join(settings.BASE_DIR, 'temp', 'upload_photo.jpg')
        data = image_to_base64(file_path)
        file_name = os.path.join(settings.BASE_DIR, 'WTE', 'answer.txt')
        client = ZhipuAI(api_key="your_api_key_here")

        response = client.chat.completions.create(
            model="glm-4v",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": ''' 假如有一个游客在旅游是拍了这样一张照片，请告诉我这是哪国的菜单，因此你在哪国旅游
                            然后列出菜单上每一个菜，并且告诉我它们的价格是多少
                            
                            下面是一个输出的例子，请严格按照以下格式进行输出
                            “这个是中国的菜单，所以该游客 在中国旅游
                            鱼香肉丝：20人民币
                            宫保鸡丁：22人民币
                            ......”
                            特别注意：该例子是经过省略的，在输出的时候，请把所有识别到的菜品全部输出
                                    '''
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data
                            }
                        }
                    ]
                }
            ],
            stream=True,
        )

        with open(file_name, "w", encoding='utf-8') as file:
            for chunk in response:
                file.write(chunk.choices[0].delta.content)

        print("第一步(orc)已完成")

        with open(file_name, 'r', encoding='utf-8') as file:
            string = file.read()
            string += ' 游客所在国家是 '
            with open(os.path.join(settings.BASE_DIR, "temp", "option.txt"), "r", encoding='utf-8') as f:
                string += f.read()

        response = client.chat.completions.create(
            model="glm-4-0520",
            messages=[
                {"role": "user", "content": string + '''
                输出：1.用旅游地的语言呈现菜名
                2.用游客所在国家所说的语言表示食材，如德文的鸡蛋
                3.用游客所在国家所说的语言阐述菜品口味，如德语表达香辣
                4.游客所在国家所说的语言阐述是否有常见的过敏食材 
                5.用游客所在国家所说的语言展示按照国际汇率换算的游客所在国家所用货币的金额
                把同一个菜品的介绍放在一起，先用游客所在国家写出你要输出的项目是什么，然后再进行介绍，并且我不要注释
                
                特别注意要严格遵循本条规则：除了菜名本身，其余回复的文字均使用游客所在国家输出，不要刻意用提示词的语言回复我
                '''}
            ],
        )

        with open(file_name, "w", encoding='utf-8') as file:
            file.write(response.choices[0].message.content)

        return JsonResponse({"message": "代码执行完成", "redirect_url": "/display_result/"})
    except Exception as e:
        print(f"代码执行失败: {str(e)}")
        return JsonResponse({"message": f"代码执行失败: {str(e)}"}, status=500)

def display_result(request):
    try:
        file_path = os.path.join(settings.BASE_DIR, 'WTE', 'answer.txt')
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return render(request, 'display_result.html', {'content': content})
    except Exception as e:
        return HttpResponse(f"无法读取文件内容: {str(e)}")
