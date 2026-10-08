"""User-run OAuth helper. Saves credentials locally without printing tokens."""
import argparse
import json
import shutil
import sys
from pathlib import Path
from dotenv import set_key

ROOT = Path(__file__).resolve().parent.parent

def save_credentials(credentials, env_path):
    if not credentials.refresh_token:
        raise ValueError('Google did not return a refresh token. Authorize again with consent.')
    if not env_path.exists():
        shutil.copyfile(ROOT / '.env.example', env_path)
    for key, value in {
        'YOUTUBE_CLIENT_ID': credentials.client_id,
        'YOUTUBE_CLIENT_SECRET': credentials.client_secret,
        'YOUTUBE_REFRESH_TOKEN': credentials.refresh_token,
    }.items():
        set_key(str(env_path), key, value)

def main():
    parser = argparse.ArgumentParser(description='Connect your YouTube channel using a Google Desktop OAuth client.')
    parser.add_argument('--client-file', type=Path, default=ROOT / 'data' / 'google-client.json')
    args = parser.parse_args()
    if not args.client_file.is_file():
        parser.error('Download your Desktop OAuth client JSON to data/google-client.json first.')
    data = json.loads(args.client_file.read_text(encoding='utf-8-sig'))
    if 'installed' not in data:
        parser.error('Use an OAuth client of type Desktop app, not Web application.')
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(args.client_file),
        scopes=['https://www.googleapis.com/auth/youtube.upload'], autogenerate_code_verifier=True)
    credentials = flow.run_local_server(host='127.0.0.1', port=0,
        access_type='offline', prompt='consent',
        authorization_prompt_message='Opening Google sign-in. Select the account/channel you want to upload to.',
        success_message='YouTube authorization received. You can close this browser tab.')
    save_credentials(credentials, ROOT / '.env')
    print('YouTube credentials saved to .env. No tokens were printed. Restart Dreamforge Studio.')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'YouTube connection failed ({type(e).__name__}). Check the setup guide and Google OAuth configuration.', file=sys.stderr)
        sys.exit(1)
