# -*- mode: python ; coding: utf-8 -*-
import os


a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[('resources', 'resources'), ('gui', 'gui'), ('utils', 'utils')],
    hiddenimports=['gui', 'gui.theme', 'gui.base_dialog', 'gui.animation_mixin', 'gui.styles',
                   'gui.usb_latency_dialog', 'gui.disk_corruption_dialog', 'gui.input_lag_dialog',
                   'gui.service_dependency_dialog', 'gui.physical_cores_dialog', 'gui.driver_registry_dialog',
                   'utils'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SystemPulse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\icon.ico'],
)