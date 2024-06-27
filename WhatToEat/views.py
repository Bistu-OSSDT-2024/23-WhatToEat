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
                            "text": ''' 首先分析该菜单是哪个国家的菜单，然后把每道菜名字及其对应价格输出给我(如果有价格)
                                        注：要用按该国文字以及货币输出输出
                                        举例1：这是中国的菜单 1.鱼香肉丝 18￥ 2.宫保鸡丁 22￥
                                        举例2：こちらは和食メニューです  1.とんこつラーメン 300円 2.寿司 200円
                                        如果看不清具体的菜单，则菜单应为图片中出现的文字对应国家的菜单
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

        print("第一步完成")

        with open(file_name, 'r', encoding='utf-8') as file:
            string = file.read()
            string += ' customer from '
            with open(os.path.join(settings.BASE_DIR, "temp", "option.txt"), "r", encoding='utf-8') as f:
                string += f.read()

        response = client.chat.completions.create(
            model="glm-4-0520",
            messages=[
                {"role": "user", "content": '根据我的输入：' + string + '''
                格式为：这是旅游地的菜单，...（n个菜及其价格），游客故乡所说的语言

                按照如下要求输出：
                1.用旅游地的语言呈现菜名1
                2.用游客故乡的语言介绍有什么食材
                3.用游客故乡的语言阐述菜品口味
                4.游客故乡的语言阐述是否有常见的过敏食材 
                5.用游客故乡的语言展示按照国际汇率换算的游客故乡所用货币的金额

                1.用旅游地的语言呈现菜名2
                2.用游客故乡的语言介绍有什么食材
                3.用游客故乡的语言阐述菜品口味
                4.游客故乡的语言阐述是否有常见的过敏食材 
                5.用游客故乡的语言展示按照国际汇率换算的游客故乡所用货币的金额

                ......

                不要输出分步的标题,我不需要过程,并严谨按照我给的格式输出（输出所有的菜而不只是两个）
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
