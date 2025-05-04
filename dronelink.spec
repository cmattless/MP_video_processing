block_cipher = None

a = Analysis(
    ['dronelink.py'],
    pathex=[
        'c:/Users/conno/Desktop/temp_repos/Major_Project',
        'c:/Users/conno/Desktop/temp_repos/Major_Project/src'
    ],
    binaries=[],
    datas=[
        ('./src/assets/*', './assets/'),
    ],
    hiddenimports=[
        'src',
        'src.assets',
        'src.core',
        'src.core.video_utils',
        'src.core.video_utils.video_queue',
        'src.core.archive_processor',
        'src.core.metadata_processor',
        'src.core.model_processor',
        'src.core.stream_processor',
        'src.core.video_processor',
        'src.gui',
        'src.gui.dialog_handler',
        'src.gui.metadata_viewer',
        'src.gui.settings_dialog',
        'src.gui.video_player'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dronelink',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
