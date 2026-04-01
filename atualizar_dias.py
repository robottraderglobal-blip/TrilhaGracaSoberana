import asyncio
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env')

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Faltam variáveis de ambiente!")
    exit(1)

supabase = create_client(url, key)

dias = {
    1: 'Domingo',
    2: 'Segunda',
    3: 'Terça',
    4: 'Quarta',
    5: 'Quinta',
    6: 'Sexta',
    7: 'Sábado'
}

for desc, name in dias.items():
    res = supabase.table('plano_devocional').update({'dia_nome': name}).eq('dia_semana', desc).execute()
    print(f"Atualizado {desc} para {name}")

print('Concluído!')
