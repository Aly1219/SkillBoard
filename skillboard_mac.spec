# skillboard_mac.spec
# Compile avec : pyinstaller skillboard_mac.spec

block_cipher = None

a = Analysis(
    ['skillboard_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('skillboard.config.json', '.'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.cocoa',
        'Foundation',
        'AppKit',
        'WebKit',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SkillBoard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    argv_emulation=True,     # Requis sur Mac pour les .app
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='static/img/logo.icns',  # Décommenter si tu as une icône .icns
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SkillBoard',
)

# Crée le bundle .app natif macOS
app = BUNDLE(
    coll,
    name='SkillBoard.app',
    icon='static/img/logo.icns',               # Remplacer par 'static/img/logo.icns' si disponible
    bundle_identifier='com.skillboard.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleName': 'SkillBoard',
        'NSRequiresAquaSystemAppearance': False,
    },
)
