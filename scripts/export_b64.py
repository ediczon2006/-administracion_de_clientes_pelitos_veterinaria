import base64
import os

os.makedirs('assets', exist_ok=True)
with open('assets/banner_pets.png', 'rb') as f:
    b64_banner = base64.b64encode(f.read()).decode('utf-8')
with open('assets/flyer_preview.png', 'rb') as f:
    b64_flyer = base64.b64encode(f.read()).decode('utf-8')

with open('assets/b64_assets.js', 'w', encoding='utf-8') as f:
    f.write('const BANNER_PETS_B64 = "data:image/png;base64,' + b64_banner + '";\n')
    f.write('const FLYER_PREVIEW_B64 = "data:image/png;base64,' + b64_flyer + '";\n')

print('Assets saved successfully!')
