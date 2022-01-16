import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def recaptcha(request):
    r = requests.post(
      'https://www.google.com/recaptcha/api/siteverify',
      data={
        'secret': '6LcFmBQeAAAAAHsoXFfXbicFHU_uCN2YXb0gMies',
        'response': request.data['captcha_value'],
      }
    )

    return Response({'captcha': r.json()})

