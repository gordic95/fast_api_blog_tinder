import requests

url = "http://127.0.0.1:8000/users/me"

YOUR_ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuaWtpdGEiLCJleHAiOjE3NTU1MjM4MDl9.9ZaqNPxIDmo3zM-LiXsaNPxDB9fHRx1nufeya3EVIS8"
headers = {
    "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}",
}
response = requests.get(url, headers=headers)
print(response.json())

# from fastapi.testclient import TestClient
# from main import app  # импортируйте ваше приложение FastAPI
#
# client = TestClient(app)
#
# def test_logout():
#     # Генерация поддельного токена (для целей тестирования)
#     fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNzU1MzczMjY5fQ.zj4qS3q65FUPDC7sJykt9h2tr4rd5kvLf6kR0syqHpk"
#
#     # Отправляем запрос на выход
#     response = client.post("/users/logout", headers={
#         "Authorization": f"Bearer {fake_token}"
#     })
#
#     assert response.status_code == 200
#     assert response.json()["detail"] == "Вы успешно вышли из аккаунта."
