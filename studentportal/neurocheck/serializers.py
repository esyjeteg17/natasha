from rest_framework import serializers

class DocumentSerializer(serializers.Serializer):
    file = serializers.FileField()



import tempfile
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import DocumentSerializer
from .extract_keywords import get_keywords_and_topic

from gigachat import GigaChat

class DocumentReviewViewSet(viewsets.ViewSet):
    """
    Принимает docx-файл, извлекает тему и ключевые слова,
    и передаёт их в GigaChat для оценки студенческой работы.
    """
    def create(self, request):
        # 1. Валидация и приём файла
        serializer = DocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data['file']

        # 2. Сохраняем его во временный файл .docx
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # 3. Извлекаем тему и топ-10 ключевых слов
        top_words, topic = get_keywords_and_topic(tmp_path, top_n=10)

        # 4. Берём первые 5 лемматизированных ключевых слов
        keywords = [word for word, freq in top_words][:5]

        # 5. Готовим промпт для GigaChat
        prompt = (
            f"Вы — преподаватель. Тема документа: «{topic}». "
            f"Ключевые слова: {', '.join(keywords)}. "
            "Соответствуют ли эти ключевые слова теме и справился ли студент с работой? "
            "Пожалуйста, дайте развёрнутый ответ."
        )

        # 6. Обращаемся к GigaChat API
        credentials = 'eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.nNnhGtyA3X3cI9kLqzMDorM-MtHzgh5_I-vDNByRHqM4hNOw6sRhfHtuum2B6nSaQXUet5pQDyllPodiae6Cqh5wUQr44FWDCDUpLb61CTl_EyF2wiOsUcFfM7q3XQU2WTzWB2FgYlORJq-o-cs3yOqMBnKWOxwXBIETBh5Mi_BDl9g7P4IVoFB_ng9td3f0mi2-MUG9d9TeSNYgMUrH8BhkZqqCRroBVC2AXVdPspHynWrtkwktK5xjt2sluwVrGfFXCWapgynMDz8uTYJUbEAOZCXEl9N36mgi9I764qOvGN2l0CADlRzXBZ4nAsjAyTCUL59PFyGUQVUmaivwPQ.YAwR3P8Vs4up-nS7OOCa4g.qEreUPosUEDFu_gr3ovqGos2qV_H5iGjcdAdMnI0sqZ3t2VOU8EmuQC4AIyQt_qkmuk7ttUv4QuATk7esRnVcFgxBuxokEObwyGv7n6te5N8xEPjwabvOsVBxtud-1w7Hirz_Gj4X3ROYcKgcbcdvA5p8gYzTvYyNKwO6KWn1mFUuZRtWytXGz5us3Uo7FDiMT37Zu53fOZGm3-S4KNw7LjfKZBqbTxh0yTrPQN3gSXa8wADdzuVM3QYfJhKPB-VrmJDppCiqD-26z0-VDViJK3rcWDwCwBkf4eI0WaP2k9HCUC02LIeN1H19xJNJNMg-gL91-AROuaOwc9bR7SkzP625_PWEDuLV2hd3M2BW6cRPVBghaK5i_0pZf2OmchgTsVOd_BPG_Qjnj6wofPjSO3FE0QeJ3cRFOr09SeFwKHuBm_9CajJlsrjTjdFtpUl500_b1t5HElHGE7tImhY9ZeVlKP9L_8X1eE_RbVtwBv67-6Db60JOfty3ggRu2r6QMlCGK6dpMP3-050kSwmKy5H_e28mCrbOogdtOfKALE-R_IXir7UEtKBO9rBWFY2xQEIDrh4XwprDw9wNKog03-BEZ_CDoEJwqjE2jRFNZjtNEQx9TGAq1QBpASgKTdrkCUk-LTgqvEG-wUorGoVn7sCbH5Yfnsh_RxkgUWdYPocy1CdpUyFvvJRAtYEoDSiXLjUE7ssmit77rVIzlymZsiYt7580zj9p927-padRpM.gXey4UrQxHm6IPdSEUwbt_RvcrDgAtS0CTCBaT5FndI'
        with GigaChat(credentials="eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.nNnhGtyA3X3cI9kLqzMDorM-MtHzgh5_I-vDNByRHqM4hNOw6sRhfHtuum2B6nSaQXUet5pQDyllPodiae6Cqh5wUQr44FWDCDUpLb61CTl_EyF2wiOsUcFfM7q3XQU2WTzWB2FgYlORJq-o-cs3yOqMBnKWOxwXBIETBh5Mi_BDl9g7P4IVoFB_ng9td3f0mi2-MUG9d9TeSNYgMUrH8BhkZqqCRroBVC2AXVdPspHynWrtkwktK5xjt2sluwVrGfFXCWapgynMDz8uTYJUbEAOZCXEl9N36mgi9I764qOvGN2l0CADlRzXBZ4nAsjAyTCUL59PFyGUQVUmaivwPQ.YAwR3P8Vs4up-nS7OOCa4g.qEreUPosUEDFu_gr3ovqGos2qV_H5iGjcdAdMnI0sqZ3t2VOU8EmuQC4AIyQt_qkmuk7ttUv4QuATk7esRnVcFgxBuxokEObwyGv7n6te5N8xEPjwabvOsVBxtud-1w7Hirz_Gj4X3ROYcKgcbcdvA5p8gYzTvYyNKwO6KWn1mFUuZRtWytXGz5us3Uo7FDiMT37Zu53fOZGm3-S4KNw7LjfKZBqbTxh0yTrPQN3gSXa8wADdzuVM3QYfJhKPB-VrmJDppCiqD-26z0-VDViJK3rcWDwCwBkf4eI0WaP2k9HCUC02LIeN1H19xJNJNMg-gL91-AROuaOwc9bR7SkzP625_PWEDuLV2hd3M2BW6cRPVBghaK5i_0pZf2OmchgTsVOd_BPG_Qjnj6wofPjSO3FE0QeJ3cRFOr09SeFwKHuBm_9CajJlsrjTjdFtpUl500_b1t5HElHGE7tImhY9ZeVlKP9L_8X1eE_RbVtwBv67-6Db60JOfty3ggRu2r6QMlCGK6dpMP3-050kSwmKy5H_e28mCrbOogdtOfKALE-R_IXir7UEtKBO9rBWFY2xQEIDrh4XwprDw9wNKog03-BEZ_CDoEJwqjE2jRFNZjtNEQx9TGAq1QBpASgKTdrkCUk-LTgqvEG-wUorGoVn7sCbH5Yfnsh_RxkgUWdYPocy1CdpUyFvvJRAtYEoDSiXLjUE7ssmit77rVIzlymZsiYt7580zj9p927-padRpM.gXey4UrQxHm6IPdSEUwbt_RvcrDgAtS0CTCBaT5FndI", verify_ssl_certs=False) as giga:
            resp = giga.chat(prompt)

        evaluation = resp.choices[0].message.content

        # 7. Отдаём результат
        return Response({
            "topic": topic,
            "keywords": keywords,
            "evaluation": evaluation
        }, status=status.HTTP_200_OK)