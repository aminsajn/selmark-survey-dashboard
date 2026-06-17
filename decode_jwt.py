import base64, json
payload = 'eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl0bWNia2dybmF5dGJ4emtjd3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0NzQxNjEsImV4cCI6MjA5NjA1MDE2MX0'
padded = payload + '=' * (4 - len(payload) % 4)
data = json.loads(base64.b64decode(padded))
ref = data['ref']
print('Project URL: https://' + ref + '.supabase.co')
