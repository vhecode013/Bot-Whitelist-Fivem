# utils/wl_session.py

from utils.wl_questions import QUESTIONS

class WLSession:
    def __init__(self, user_id: int):
        self.user_id = user_id  # ID do Discord
        self.user_id_in_db = None  # ID da tabela vrp_users (preencher depois)
        
        self.current = 0
        self.correct = 0
        self.finished = False

    def get_question(self):
        """Retorna a pergunta atual ou None se terminou."""
        if self.current >= len(QUESTIONS):
            self.finished = True
            return None
        return QUESTIONS[self.current]

    def answer(self, choice: str):
        """Registra resposta e avança para próxima."""
        if self.finished:
            return

        question = QUESTIONS[self.current]

        if choice == question["correta"]:
            self.correct += 1

        self.current += 1
        
        # Marca como finalizado ao atingir o final
        if self.current >= len(QUESTIONS):
            self.finished = True

    def score_percent(self):
        """Retorna porcentagem de acertos."""
        if len(QUESTIONS) == 0:
            return 0
        return int((self.correct / len(QUESTIONS)) * 100)
