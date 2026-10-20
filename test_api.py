from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

risposta = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Rispondi con una sola frase: di che genere letterario è 'Il Gattopardo'?"}],
)
print(risposta.content[0].text)
