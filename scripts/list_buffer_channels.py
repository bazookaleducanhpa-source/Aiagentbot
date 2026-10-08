"""Read connected channels; never print the personal Buffer API key."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.providers import buffer_channels, ProviderError

if __name__ == '__main__':
    try:
        channels = buffer_channels()
        if not channels:
            print('No channels found. Connect your TikTok account in Buffer first.')
        for channel in channels:
            print(f"{channel['service']} | {channel.get('displayName') or channel['name']} | {channel['organization']} | channel_id={channel['id']}")
    except ProviderError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
